"""
텔레그램 시그널 메시지 파서

지원 형식:
🚀 NEW-LAUNCH SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━
Token: - $WarGPT
├ 6JFvA3ZKEfi3wDnzEVB3jzMGsLfcqVr4oqi3BzXHpump
└ 👾 #SOL
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


def parse_signal(message: str) -> Optional[TradeSignal]:
    """
    텔레그램 메시지에서 매매 시그널을 파싱합니다.
    파싱 실패 시 None 반환.
    """
    if not message:
        return None

    # BUY 시그널 감지 (NEW-LAUNCH SIGNAL)
    is_buy = "NEW-LAUNCH SIGNAL" in message or "NEW LAUNCH" in message.upper()
    is_sell = "SELL" in message.upper() and "NEW-LAUNCH" not in message

    if not (is_buy or is_sell):
        return None

    # Solana 민트 주소 추출 (44자 Base58 문자열 우선)
    addresses = SOLANA_ADDRESS_PATTERN.findall(message)
    mint_address = None
    for addr in addresses:
        # Solana 주소는 보통 32-44자, pump.fun 토큰은 'pump'로 끝남
        if len(addr) >= 32:
            mint_address = addr
            break

    if not mint_address:
        return None

    # 토큰 이름 추출
    token_match = TOKEN_NAME_PATTERN.search(message)
    token_name = token_match.group(1) if token_match else "UNKNOWN"

    # 체인 감지
    chain = "SOL" if "#SOL" in message or "solana" in message.lower() else "UNKNOWN"

    if chain == "UNKNOWN":
        return None

    signal_type = "BUY" if is_buy else "SELL"

    return TradeSignal(
        token_name=token_name,
        mint_address=mint_address,
        chain=chain,
        signal_type=signal_type,
    )
