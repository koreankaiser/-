"""
Solana 밈코인 자동매매 봇

실행 방법:
1. .env.example을 .env로 복사하고 값을 채워넣으세요
2. pip install -r requirements.txt
3. python main.py
"""

import asyncio
import ctypes
import sys
from solana.rpc.async_api import AsyncClient

from config import (
    SIGNAL_SOURCES,
    TRADE_AMOUNT_PCT,
    TAKE_PROFIT_RATIO,
    STOP_LOSS_RATIO,
    SLIPPAGE_BPS,
    FEE_ESTIMATE_BPS,
)
from solana_wallet import load_keypair, get_sol_balance, create_rpc_client
from position_manager import PositionManager
from telegram_listener import SignalListener


def prevent_sleep():
    """Windows 절전 모드 및 화면 꺼짐 방지"""
    if sys.platform == "win32":
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
        print("[시스템] 절전 모드 및 화면 꺼짐 방지 활성화")


def print_banner(balance: float):
    trade_sol = balance * TRADE_AMOUNT_PCT
    print("=" * 58)
    print("  Solana 밈코인 자동매매 봇")
    print("=" * 58)
    print(f"  모니터링 채널 ({len(SIGNAL_SOURCES)}개):")
    for src in SIGNAL_SOURCES:
        print(f"    • {src}")
    print(f"  투자 비율:    {TRADE_AMOUNT_PCT * 100:.0f}% / 시그널 (복리식)")
    print(f"  현재 잔액:    {balance:.4f} SOL → 시그널당 {trade_sol:.4f} SOL")
    print(f"  익절 목표:    +{TAKE_PROFIT_RATIO * 100:.0f}%")
    print(f"  손절 기준:    -{STOP_LOSS_RATIO * 100:.0f}%")
    print(f"  슬리피지:     {SLIPPAGE_BPS / 100:.1f}% | 수수료 추정: {FEE_ESTIMATE_BPS / 100:.1f}%")
    print("=" * 58)


async def main():
    # 절전 모드 방지
    prevent_sleep()

    # 지갑 로드
    try:
        keypair = load_keypair()
        print(f"[Wallet] 주소: {keypair.pubkey()}")
    except Exception as e:
        print(f"[오류] 지갑 로드 실패: {e}")
        print("       .env 파일의 WALLET_PRIVATE_KEY를 확인하세요")
        sys.exit(1)

    # RPC 클라이언트 생성
    rpc_client = create_rpc_client()

    # SOL 잔액 확인
    balance = 0.0
    try:
        balance = await get_sol_balance(rpc_client, str(keypair.pubkey()))
    except Exception as e:
        print(f"[경고] 잔액 조회 실패: {e}")

    print_banner(balance)

    min_trade = 0.001
    trade_sol = balance * TRADE_AMOUNT_PCT
    if trade_sol < min_trade:
        print(f"[경고] 투자 가능 금액({trade_sol:.6f} SOL)이 너무 적습니다. SOL을 충전하세요.")

    if not SIGNAL_SOURCES:
        print("[오류] SIGNAL_SOURCES가 설정되지 않았습니다. .env 파일을 확인하세요.")
        sys.exit(1)

    # 포지션 매니저 생성 및 모니터링 시작
    position_manager = PositionManager(keypair, rpc_client)
    position_manager.start_monitoring()

    # 텔레그램 리스너 시작
    listener = SignalListener(keypair, rpc_client, position_manager)

    try:
        await listener.start()
    except KeyboardInterrupt:
        print("\n[봇] 종료 중...")
    finally:
        await rpc_client.close()
        print("[봇] 종료 완료")


if __name__ == "__main__":
    asyncio.run(main())
