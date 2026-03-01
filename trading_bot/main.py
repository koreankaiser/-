"""
Solana 밈코인 자동매매 봇

실행 방법:
1. .env.example을 .env로 복사하고 값을 채워넣으세요
2. pip install -r requirements.txt
3. python main.py
"""

import asyncio
import sys
from solana.rpc.async_api import AsyncClient

from config import TRADE_AMOUNT_SOL, TAKE_PROFIT_RATIO, STOP_LOSS_RATIO, SIGNAL_SOURCE
from solana_wallet import load_keypair, get_sol_balance, create_rpc_client
from position_manager import PositionManager
from telegram_listener import SignalListener


def print_banner():
    print("=" * 50)
    print("  Solana 밈코인 자동매매 봇")
    print("=" * 50)
    print(f"  시그널 소스:  {SIGNAL_SOURCE}")
    print(f"  매매 금액:    {TRADE_AMOUNT_SOL} SOL / 시그널")
    print(f"  익절 목표:    +{TAKE_PROFIT_RATIO * 100:.0f}%")
    print(f"  손절 기준:    -{STOP_LOSS_RATIO * 100:.0f}%")
    print("=" * 50)


async def main():
    print_banner()

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
    try:
        balance = await get_sol_balance(rpc_client, str(keypair.pubkey()))
        print(f"[Wallet] SOL 잔액: {balance:.4f} SOL")
        if balance < TRADE_AMOUNT_SOL:
            print(f"[경고] 잔액({balance:.4f} SOL)이 매매 금액({TRADE_AMOUNT_SOL} SOL)보다 적습니다!")
    except Exception as e:
        print(f"[경고] 잔액 조회 실패: {e}")

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
