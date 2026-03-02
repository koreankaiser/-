"""
텔레그램 시그널 메시지 파서

CA(컨트랙트 주소) 우선 감지 방식:
채널마다 포맷이 달라도 Solana CA 주소가 있으면 BUY 시그널로 처리.
명시적 SELL 키워드가 있을 때만 SELL로 분류.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class TradeSignal:
    token_name: str
    mint_address: str
    chain: str
    signal_type: str  # "BUY" or "SELL"


# Solana 주소 패턴: 32-44자 Base58 문자열
SOLANA_ADDRESS_PATTERN = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")

# 토큰 이름 패턴: $로 시작하는 단어
TOKEN_NAME_PATTERN = re.compile(r"\$([A-Za-z0-9_]+)")

# 명시적 SELL/위험 키워드 (이 단어가 있으면 SELL 시그널)
_SELL_KEYWORDS = {"SELL", "EXIT", "RUG", "DUMP", "SCAM", "WARNING", "AVOID", "CAUTION"}


def parse_signal(message: str) -> Optional[TradeSignal]:
    """
    텔레그램 메시지에서 매매 시그널을 파싱합니다.
    파싱 실패 시 None 반환.

    로직:
    1. Solana CA 주소 추출 (없으면 무시)
    2. SOL 체인 여부 확인 (#SOL, pump 주소, solana 언급 등)
    3. SELL 키워드 없으면 BUY, 있으면 SELL
    """
    if not message:
        return None

    # 1단계: Solana CA 주소 추출 (32자 이상 Base58, pump 주소 우선)
    addresses = SOLANA_ADDRESS_PATTERN.findall(message)
    mint_address = None
    for addr in addresses:
        if len(addr) >= 32:
            # pump.fun 토큰 주소 우선 선택
            if addr.endswith("pump"):
                mint_address = addr
                break
            if mint_address is None:
                mint_address = addr

    if not mint_address:
        return None

    # 2단계: SOL 체인 확인
    msg_lower = message.lower()
    is_sol = (
        "#sol" in msg_lower
        or "solana" in msg_lower
        or "pump.fun" in msg_lower
        or mint_address.endswith("pump")   # pump.fun 주소 = Solana 확정
    )
    if not is_sol:
        return None

    # 3단계: SELL vs BUY 판단
    msg_upper = message.upper()
    words = set(re.findall(r"[A-Z]+", msg_upper))
    is_sell = bool(words & _SELL_KEYWORDS)

    # 4단계: 토큰 이름 추출
    token_match = TOKEN_NAME_PATTERN.search(message)
    token_name = token_match.group(1) if token_match else "UNKNOWN"

    return TradeSignal(
        token_name=token_name,
        mint_address=mint_address,
        chain="SOL",
        signal_type="SELL" if is_sell else "BUY",
    )
