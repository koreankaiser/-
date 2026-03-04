"""
Solana 자동매매 봇 (Trojan 봇 연동)

실행:
  pip install -r requirements.txt
  python main.py
"""

import asyncio
import ctypes
import sys

from config import (
    SIGNAL_SOURCES, TROJAN_BOT,
    TRADE_AMOUNT_PCT, TAKE_PROFIT_RATIO, STOP_LOSS_RATIO,
)
from telegram_listener import TelegramSignalBot


def prevent_sleep():
    """Windows 절전 모드 및 화면 꺼짐 방지"""
    if sys.platform == "win32":
        ES_CONTINUOUS      = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
        print("[시스템] 절전 모드 방지 활성화")


def print_banner():
    print("=" * 50)
    print("  Solana 자동매매 봇 (Trojan 봇 연동)")
    print("=" * 50)
    print(f"  감시 채널 ({len(SIGNAL_SOURCES)}개):")
    for src in SIGNAL_SOURCES:
        print(f"    • {src}")
    print(f"  투자 비율:  {TRADE_AMOUNT_PCT * 100:.0f}%")
    print(f"  익절 목표:  +{TAKE_PROFIT_RATIO * 100:.0f}%")
    print(f"  손절 기준:  -{STOP_LOSS_RATIO * 100:.0f}%")
    print("=" * 50)


async def main():
    prevent_sleep()
    print_banner()

    print("[시스템] 자동매매 봇 활성화")
    print(f"[설정] 감시 채널: {len(SIGNAL_SOURCES)}개")
    print(f"[설정] 매수 봇: @{TROJAN_BOT}")
    print(
        f"[설정] 투자 비율: {TRADE_AMOUNT_PCT*100:.0f}% | "
        f"익절: +{TAKE_PROFIT_RATIO*100:.0f}% | "
        f"손절: -{STOP_LOSS_RATIO*100:.0f}%"
    )

    bot = TelegramSignalBot()

    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\n[봇] 종료 중...")
    print("[봇] 종료 완료")


if __name__ == "__main__":
    asyncio.run(main())
