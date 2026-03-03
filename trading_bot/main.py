"""
Solana 밈코인 자동매매 봇 (Trojan 봇 연동 방식)

실행 방법:
1. .env.example을 .env로 복사하고 값을 채워넣으세요
2. pip install -r requirements.txt
3. python main.py
"""

import asyncio
import ctypes
import sys

from config import (
    SIGNAL_SOURCES,
    TRADE_AMOUNT_PCT,
    TAKE_PROFIT_RATIO,
    STOP_LOSS_RATIO,
)
from telegram_listener import TelegramSignalBot


def prevent_sleep():
    """Windows 절전 모드 및 화면 꺼짐 방지"""
    if sys.platform == "win32":
        ES_CONTINUOUS = 0x80000000
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
    print(f"  투자 비율:  {TRADE_AMOUNT_PCT * 100:.0f}% / 시그널 (복리식)")
    print(f"  익절 목표:  +{TAKE_PROFIT_RATIO * 100:.0f}%")
    print(f"  손절 기준:  -{STOP_LOSS_RATIO * 100:.0f}%")
    print("=" * 50)


async def main():
    prevent_sleep()

    if not SIGNAL_SOURCES:
        print("[오류] SIGNAL_SOURCES가 설정되지 않았습니다. .env 파일을 확인하세요.")
        sys.exit(1)

    print_banner()

    bot = TelegramSignalBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\n[봇] 종료")


if __name__ == "__main__":
    asyncio.run(main())
