"""단기·요청별 서명으로 MCP 쓰기 Tool 호출을 제한합니다.

서명은 신뢰할 수 있는 API가 승인 여부를 확인한 뒤에만 생성합니다.
이 예제는 로컬 학습용이며 실제 사용자 인증 시스템은 아닙니다.
"""
import base64
import hashlib
import hmac
import json
import os
import time

from app.store import create_ticket


def _signing_secret() -> bytes:
    # 단일 사용자 로컬 학습에서는 DEMO_ADMIN_KEY를 대체 비밀키로 사용합니다.
    key = os.environ.get("MCP_APPROVAL_SIGNING_KEY") or os.environ.get("DEMO_ADMIN_KEY", "")
    if len(key) < 16 or key == "replace-with-your-private-random-secret":
        raise PermissionError("쓰기 승인 비밀키가 설정되지 않았습니다.")
    return key.encode("utf-8")


def issue_approval_token(title: str, description: str, request_id: str, ttl: int = 60) -> str:
    """승인된 요청을 처리하는 신뢰할 수 있는 백엔드에서만 호출합니다."""
    if ttl <= 0 or ttl > 300:
        raise ValueError("승인 유효시간은 1~300초여야 합니다.")
    payload = {
        "title": title,
        "description": description,
        "request_id": request_id,
        "expires": int(time.time()) + ttl,
    }
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")
    signature = hmac.new(_signing_secret(), encoded.encode("ascii"), hashlib.sha256).hexdigest()
    return encoded + "." + signature


def verify_approval_token(title: str, description: str, request_id: str, token: str) -> None:
    """누락·변조·만료·다른 요청의 토큰을 모두 거부합니다."""
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(_signing_secret(), encoded.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise PermissionError("승인 서명이 올바르지 않습니다.")
        raw = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        payload = json.loads(raw)
        if payload.get("expires", 0) < int(time.time()):
            raise PermissionError("승인 유효시간이 지났습니다.")
        if any(payload.get(k) != v for k, v in
               (("title", title), ("description", description), ("request_id", request_id))):
            raise PermissionError("승인된 요청 내용과 다릅니다.")
    except (ValueError, UnicodeError, TypeError, KeyError) as exc:
        raise PermissionError("유효하지 않은 승인 토큰입니다.") from exc


def create_approved_ticket(title: str, description: str, request_id: str,
                           approval_token: str) -> dict:
    verify_approval_token(title, description, request_id, approval_token)
    return create_ticket(title, description, request_id)
