"""
포지션 관리 및 자동 TP/SL 모니터링

매수 후 포지션을 추적하고, +30% 익절 / -30% 손절 도달 시 자동 매도
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

import jupiter_client
from config import TAKE_PROFIT_RATIO, STOP_LOSS_RATIO, PRICE_CHECK_INTERVAL


@dataclass
class Position:
    mint_address: str
    token_name: str
    entry_price: float          # 매수 시 USD 가격
    entry_time: datetime
    sol_invested: float         # 투자한 SOL 금액
    token_amount: int           # 보유 토큰 수량 (raw)
    tx_signature: str           # 매수 트랜잭션 서명
    closed: bool = False


class PositionManager:
    def __init__(self, keypair: Keypair, rpc_client: AsyncClient):
        self.keypair = keypair
        self.rpc_client = rpc_client
        self.positions: dict[str, Position] = {}  # mint_address → Position
        self._monitoring_task: Optional[asyncio.Task] = None

    def add_position(self, position: Position):
        """새 포지션 추가"""
        self.positions[position.mint_address] = position
        print(
            f"[Position] 포지션 추가: ${position.token_name} "
            f"진입가 ${position.entry_price:.8f}"
        )

    def has_position(self, mint_address: str) -> bool:
        """해당 토큰의 활성 포지션 여부"""
        pos = self.positions.get(mint_address)
        return pos is not None and not pos.closed

    def start_monitoring(self):
        """백그라운드 TP/SL 모니터링 시작"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitor_loop())
            print("[Position] TP/SL 모니터링 시작")

    async def _monitor_loop(self):
        """주기적으로 모든 활성 포지션의 가격을 확인"""
        while True:
            await asyncio.sleep(PRICE_CHECK_INTERVAL)
            active = [p for p in self.positions.values() if not p.closed]
            if not active:
                continue

            for position in active:
                try:
                    await self._check_position(position)
                except Exception as e:
                    print(f"[Position] {position.token_name} 모니터링 오류: {e}")

    async def _check_position(self, position: Position):
        """단일 포지션의 가격 확인 및 TP/SL 실행"""
        current_price = await jupiter_client.get_token_price(position.mint_address)
        if current_price is None:
            print(f"[Position] {position.token_name} 가격 조회 실패")
            return

        pnl_ratio = (current_price - position.entry_price) / position.entry_price
        pnl_pct = pnl_ratio * 100

        print(
            f"[Position] ${position.token_name} | "
            f"진입가: ${position.entry_price:.8f} | "
            f"현재가: ${current_price:.8f} | "
            f"손익: {pnl_pct:+.1f}%"
        )

        should_sell = False
        reason = ""

        if pnl_ratio >= TAKE_PROFIT_RATIO:
            should_sell = True
            reason = f"익절 +{pnl_pct:.1f}%"
        elif pnl_ratio <= -STOP_LOSS_RATIO:
            should_sell = True
            reason = f"손절 {pnl_pct:.1f}%"

        if should_sell:
            await self._close_position(position, reason)

    async def _close_position(self, position: Position, reason: str):
        """포지션 청산 (전량 매도)"""
        print(f"[Position] {reason} 도달! ${position.token_name} 매도 실행...")

        # 현재 보유 토큰 수량 재확인
        token_balance = await jupiter_client.get_token_balance(
            self.rpc_client,
            str(self.keypair.pubkey()),
            position.mint_address,
        )

        if not token_balance or token_balance == 0:
            print(f"[Position] ${position.token_name} 잔액 없음, 포지션 종료")
            position.closed = True
            return

        tx_sig = await jupiter_client.sell_token(
            self.keypair,
            self.rpc_client,
            position.mint_address,
            token_balance,
        )

        position.closed = True

        if tx_sig:
            print(f"[Position] 매도 성공! ({reason})")
            print(f"[Position] 트랜잭션: https://solscan.io/tx/{tx_sig}")
        else:
            print(f"[Position] 매도 실패! 수동 확인 필요: {position.mint_address}")
