"""Translation engine — Baidu (primary) + Tencent (fallback).

Supports:
- Source selection: auto / baidu / tencent
- Request cancellation via threading.Event
- Graceful error handling for all API failures
"""

import hashlib
import hmac
import json
import random
import threading
import time
from datetime import datetime, timezone

import requests

import config
from core.language import get_api_code


class TranslationResult:
    """Holds translation result or error."""

    def __init__(self, text: str = "", source: str = "", target: str = "",
                 api_used: str = "", error: str = "", phonetic: str = ""):
        self.text = text
        self.source = source
        self.target = target
        self.api_used = api_used
        self.error = error
        self.phonetic = phonetic

    @property
    def ok(self) -> bool:
        return not self.error


def translate(text: str, source: str, target: str,
              source_pref: str = "auto",
              cancel: threading.Event = None) -> TranslationResult:
    """Translate text with source preference and cancellation.

    Args:
        text: Text to translate
        source: Source language code
        target: Target language code
        source_pref: 'auto' | 'baidu' | 'tencent'
        cancel: Threading event for cancellation
    """
    if not text.strip():
        return TranslationResult(error="请输入文本")

    def _cancelled():
        return cancel and cancel.is_set()

    # Direct to specific API
    if source_pref == "baidu":
        if _cancelled():
            return TranslationResult(error="cancelled")
        return _baidu_translate(text, source, target)

    if source_pref == "tencent":
        if _cancelled():
            return TranslationResult(error="cancelled")
        return _tencent_translate(text, source, target)

    # Auto: try Baidu first, then Tencent
    if _cancelled():
        return TranslationResult(error="cancelled")

    result = _baidu_translate(text, source, target)
    if result.ok or _cancelled():
        return result

    return _tencent_translate(text, source, target)


# ── Baidu ──────────────────────────────────────────────────────────

def _baidu_translate(text: str, source: str, target: str) -> TranslationResult:
    if not config.BAIDU_APP_ID or not config.BAIDU_SECRET_KEY:
        return TranslationResult(error="百度API未配置，请在.env中设置")

    url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    salt = str(random.randint(10000, 99999))
    sign_str = config.BAIDU_APP_ID + text + salt + config.BAIDU_SECRET_KEY
    sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()

    # Use "auto" for source language detection (single API call)
    src_code = get_api_code(source, "baidu")

    params = {
        "q": text,
        "from": src_code,
        "to": get_api_code(target, "baidu"),
        "appid": config.BAIDU_APP_ID,
        "salt": salt,
        "sign": sign,
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()

        if "error_code" in data:
            code = str(data["error_code"])
            msg = data.get("error_msg", code)
            return TranslationResult(error=f"百度错误: {msg}")

        trans = data.get("trans_result", [])
        if not trans:
            return TranslationResult(error="百度: 无翻译结果")

        translated = "\n".join(item["dst"] for item in trans)

        # Extract phonetic for single words
        phonetic = ""
        if src_code != "auto" and len(text.split()) <= 2:
            phonetic = data.get("from", "")
            if "trans_result" in data and len(data["trans_result"]) == 1:
                phonetic = data["trans_result"][0].get("src", "")

        return TranslationResult(translated, source, target, api_used="baidu")

    except requests.Timeout:
        return TranslationResult(error="百度请求超时，请检查网络")
    except requests.ConnectionError:
        return TranslationResult(error="网络连接失败")
    except requests.RequestException as e:
        return TranslationResult(error=f"百度请求异常: {e}")
    except (KeyError, ValueError, TypeError) as e:
        return TranslationResult(error=f"百度响应解析失败")


# ── Tencent ────────────────────────────────────────────────────────

def _tencent_translate(text: str, source: str, target: str) -> TranslationResult:
    if not config.TENCENT_SECRET_ID or not config.TENCENT_SECRET_KEY:
        return TranslationResult(error="腾讯API未配置，请在.env中设置")

    service = "tmt"
    action = "TextTranslate"
    version = "2018-03-21"
    region = "ap-guangzhou"
    endpoint = "https://tmt.tencentcloudapi.com"

    src_code = get_api_code(source, "tencent")
    tgt_code = get_api_code(target, "tencent")

    params = {
        "SourceText": text,
        "Source": src_code if src_code != "auto" else "auto",
        "Target": tgt_code,
        "ProjectId": 0,
    }

    payload = json.dumps(params)
    timestamp = int(time.time())
    date = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")

    # TC3 signature
    ct = "application/json; charset=utf-8"
    canonical_headers = f"content-type:{ct}\nhost:tmt.tencentcloudapi.com\nx-tc-action:{action.lower()}\n"
    signed_headers = "content-type;host;x-tc-action"
    hashed_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    canonical_request = f"POST\n/\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"

    algorithm = "TC3-HMAC-SHA256"
    credential_scope = f"{date}/{service}/tc3_request"
    hashed_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_request}"

    def _hmac(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    sd = _hmac(("TC3" + config.TENCENT_SECRET_KEY).encode("utf-8"), date)
    ss = _hmac(sd, service)
    sig_key = _hmac(ss, "tc3_request")
    signature = hmac.new(sig_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    authorization = (
        f"{algorithm} Credential={config.TENCENT_SECRET_ID}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers = {
        "Authorization": authorization,
        "Content-Type": ct,
        "Host": "tmt.tencentcloudapi.com",
        "X-TC-Action": action,
        "X-TC-Version": version,
        "X-TC-Timestamp": str(timestamp),
        "X-TC-Region": region,
    }

    try:
        resp = requests.post(endpoint, data=payload, headers=headers, timeout=5)
        data = resp.json()

        response = data.get("Response", {})
        if "Error" in response:
            err = response["Error"]
            return TranslationResult(
                error=f"腾讯错误: {err.get('Message', err.get('Code', '未知'))}"
            )

        translated = response.get("TargetText", "")
        if not translated:
            return TranslationResult(error="腾讯: 无翻译结果")

        return TranslationResult(translated, source, target, api_used="tencent")

    except requests.Timeout:
        return TranslationResult(error="腾讯请求超时，请检查网络")
    except requests.ConnectionError:
        return TranslationResult(error="网络连接失败")
    except requests.RequestException as e:
        return TranslationResult(error=f"腾讯请求异常: {e}")
    except (KeyError, ValueError, TypeError) as e:
        return TranslationResult(error=f"腾讯响应解析失败")
