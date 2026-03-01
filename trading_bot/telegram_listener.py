"""
텔레그램 시그널 리스너

Telethon을 사용하여 여러 채널/봇의 메시지를 동시에 모니터링하고
시그널 감지 시 현재 자산의 10%로 자동 매수 (복리식)
"""

from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import User, Channel

from config import (
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    SIGNAL_SOURCES,
    TRADE_AMOUNT_PCT,
)
from signal_parser import parse_signal
from position_manager import Position, PositionManager
from solana_wallet import get_sol_balance
import jupiter_client


class SignalListener:
    def __init__(self, keypair, rpc_client, position_manager: PositionManager):
        self.keypair = keypair
        self.rpc_client = rpc_client
        self.position_manager = position_manager
        self.client = TelegramClient("trading_bot_session", TELEGRAM_API_ID, TELEGRAM_API_HASH)

    async def start(self):
        """텔레그램 클라이언트 시작 및 다중 채널 이벤트 핸들러 등록"""
        await self.client.start()
        print("[Telegram] 로그인 성공")

        # 각 시그널 채널 접근 확인
        valid_sources = []
        for source in SIGNAL_SOURCES:
            try:
                entity = await self.client.get_entity(source)
                if isinstance(entity, User):
                    name = entity.username or entity.first_name
                elif isinstance(entity, Channel):
                    name = entity.title
                else:
                    name = source
                print(f"[Telegram] ✓ 채널 연결: {name} (@{source})")
                valid_sources.append(source)
            except Exception as e:
                print(f"[Telegram] ✗ 채널 접근 실패: {source} → {e}")

        if not valid_sources:
            print("[Telegram] 연결 가능한 채널이 없습니다. 설정을 확인하세요.")
            return

        # 모든 유효 채널을 한 번에 구독
        @self.client.on(events.NewMessage(chats=valid_sources))
        async def handle_message(event):
            await self._process_message(event.message.text)

        print(f"\n[Telegram] 시그널 대기 중... (활성 채널: {len(valid_sources)}/{len(SIGNAL_SOURCES)}개)")
        await self.client.run_until_disconnected()

    async def _process_message(self, text: str):
        """수신된 메시지 처리"""
        if not text:
            return

        signal = parse_signal(text)
        if not signal:
            return

        print(f"\n[Signal] 시그널 감지: {signal.signal_type} ${signal.token_name}")
        print(f"[Signal] 민트 주소: {signal.mint_address}")

        if signal.signal_type == "BUY":
            await self._execute_buy(signal)
        elif signal.signal_type == "SELL":
            await self._execute_sell(signal)

    async def _execute_buy(self, signal):
        """매수 실행 — 현재 SOL 잔액의 10%를 복리식으로 투자"""
        if self.position_manager.has_position(signal.mint_address):
            print(f"[Buy] ${signal.token_name} 이미 포지션 보유 중, 스킵")
            return

        # 현재 SOL 잔액 조회 후 비율 계산 (복리식)
        try:
            balance = await get_sol_balance(self.rpc_client, str(self.keypair.pubkey()))
        except Exception as e:
            print(f"[Buy] SOL 잔액 조회 실패: {e}, 매수 취소")
            return

        trade_sol = round(balance * TRADE_AMOUNT_PCT, 6)

        if trade_sol < 0.001:
            print(f"[Buy] SOL 잔액 부족 ({balance:.4f} SOL → 투자 예정 {trade_sol:.6f} SOL), 매수 취소")
            return

        print(
            f"[Buy] ${signal.token_name} 매수 시작 | "
            f"현재 잔액: {balance:.4f} SOL | "
            f"투자 금액: {trade_sol:.4f} SOL ({TRADE_AMOUNT_PCT * 100:.0f}%)"
        )

        # 현재 가격 조회 (진입가 기록용)
        entry_price = await jupiter_client.get_token_price(signal.mint_address)
        if entry_price is None:
            print(f"[Buy] ${signal.token_name} 가격 조회 실패, 매수 취소")
            return

        # 매수 실행
        tx_sig = await jupiter_client.buy_token(
            self.keypair,
            self.rpc_client,
            signal.mint_address,
            trade_sol,
        )

        if not tx_sig:
            print(f"[Buy] ${signal.token_name} 매수 실패!")
            return

        print(f"[Buy] 매수 성공! 트랜잭션: https://solscan.io/tx/{tx_sig}")

        # 구매한 토큰 수량 조회
        token_amount = await jupiter_client.get_token_balance(
            self.rpc_client,
            str(self.keypair.pubkey()),
            signal.mint_address,
        )

        # 포지션 등록
        position = Position(
            mint_address=signal.mint_address,
            token_name=signal.token_name,
            entry_price=entry_price,
            entry_time=datetime.now(),
            sol_invested=trade_sol,
            token_amount=token_amount or 0,
            tx_signature=tx_sig,
        )
        self.position_manager.add_position(position)

    async def _execute_sell(self, signal):
        """매도 실행 (SELL 시그널 수신 시)"""
        if not self.position_manager.has_position(signal.mint_address):
            print(f"[Sell] ${signal.token_name} 보유 포지션 없음, 스킵")
            return

        position = self.position_manager.positions[signal.mint_address]
        await self.position_manager._close_position(position, "SELL 시그널 수신")
