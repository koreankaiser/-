"""
텔레그램 자동화 매매 봇

흐름:
  1. 시그널 채널에서 CA 감지
  2. Trojan 봇으로 잔액 10% 매수 (인라인 버튼 클릭)
  3. DexScreener API로 실시간 가격 모니터링
  4. +30% 도달 시 100% 익절 / -30% 도달 시 100% 손절
"""

import re
import asyncio
import httpx
from dataclasses import dataclass, field
from datetime import datetime
from telethon import TelegramClient, events
from config import (
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    SIGNAL_SOURCES,
    TRADING_BOT_USERNAME,
    TRADE_AMOUNT_PCT,
    TAKE_PROFIT_RATIO,
    STOP_LOSS_RATIO,
)

# ──────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────

# Solana CA 패턴 (Base58, 32~44자)
CA_PATTERN = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')

# Trojan 봇 잔액 파싱 패턴
BALANCE_PATTERN = re.compile(r'(\d+\.?\d*)\s*SOL', re.IGNORECASE)

# Trojan 봇 Buy 버튼 텍스트 후보
# ⚠️ 실제 버튼 텍스트가 다르면 여기에 추가하세요
BUY_BUTTON_TEXTS = ["Buy", "BUY", "🟢 Buy", "매수"]

# Trojan 봇 Sell 버튼 / 전량 매도 버튼 텍스트 후보
SELL_BUTTON_TEXTS = ["Sell", "SELL", "🔴 Sell", "매도"]
SELL_ALL_BUTTON_TEXTS = ["100%", "Sell All", "All", "전체"]

# 가격 모니터링 주기 (초)
PRICE_CHECK_INTERVAL = 30

# DexScreener API
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/tokens/{ca}"


# ──────────────────────────────────────────────
# 포지션 데이터 클래스
# ──────────────────────────────────────────────

@dataclass
class Position:
    ca: str
    entry_price_usd: float          # 진입 시 USD 가격
    sol_invested: float             # 투자한 SOL
    entry_time: datetime = field(default_factory=datetime.now)

    def pnl_ratio(self, current_price: float) -> float:
        """손익 비율 계산 (0.30 = +30%)"""
        if self.entry_price_usd == 0:
            return 0.0
        return (current_price - self.entry_price_usd) / self.entry_price_usd


# ──────────────────────────────────────────────
# 메인 봇 클래스
# ──────────────────────────────────────────────

class TelegramSignalBot:
    def __init__(self):
        self.client = TelegramClient('bot_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.current_balance_sol = 0.0
        self.trading_bot_username = TRADING_BOT_USERNAME
        self.positions: dict[str, Position] = {}   # CA → Position
        self._processing: set[str] = set()         # 중복 CA 방지

    # ──────────────────────────────
    # 시작
    # ──────────────────────────────

    async def start(self):
        await self.client.start()
        print("[시스템] 자동매매 봇 활성화")
        print(f"[설정] 감시 채널: {len(SIGNAL_SOURCES)}개")
        print(f"[설정] 매수 봇: {self.trading_bot_username}")
        print(f"[설정] 투자 비율: {TRADE_AMOUNT_PCT * 100:.0f}% | "
              f"익절: +{TAKE_PROFIT_RATIO * 100:.0f}% | "
              f"손절: -{STOP_LOSS_RATIO * 100:.0f}%")

        await self.update_balance()

        # 시그널 채널 구독
        @self.client.on(events.NewMessage(chats=SIGNAL_SOURCES))
        async def handler(event):
            if event.message.text:
                await self.process_message(event.message.text)

        # 가격 모니터링 백그라운드 태스크 시작
        asyncio.create_task(self._monitor_loop())

        print("\n[시스템] 시그널 대기 중...")
        await self.client.run_until_disconnected()

    # ──────────────────────────────
    # 잔액 조회
    # ──────────────────────────────

    async def update_balance(self) -> float:
        """Trojan 봇 /start 응답에서 SOL 잔액 파싱"""
        print("[잔액] 조회 중...")
        try:
            await self.client.send_message(self.trading_bot_username, "/start")
            await asyncio.sleep(3)

            messages = await self.client.get_messages(self.trading_bot_username, limit=5)
            for msg in messages:
                if not msg.text:
                    continue
                match = BALANCE_PATTERN.search(msg.text)
                if match:
                    self.current_balance_sol = float(match.group(1))
                    print(f"[잔액] {self.current_balance_sol:.4f} SOL")
                    return self.current_balance_sol

            print("[잔액] ⚠️  파싱 실패 — 봇 /start 응답 형식을 확인하세요")

        except Exception as e:
            print(f"[잔액] 오류: {e}")

        return self.current_balance_sol

    # ──────────────────────────────
    # 시그널 처리
    # ──────────────────────────────

    async def process_message(self, text: str):
        """메시지에서 CA 감지 → 매수 실행"""
        match = CA_PATTERN.search(text)
        if not match:
            return

        ca = match.group(0)

        if ca in self._processing or ca in self.positions:
            return
        self._processing.add(ca)

        try:
            print(f"\n[시그널] CA 감지: {ca}")
            await self.update_balance()

            buy_amount = self.current_balance_sol * TRADE_AMOUNT_PCT
            if buy_amount < 0.01:
                print(f"[취소] 잔액 부족: {buy_amount:.4f} SOL")
                return

            await self._execute_buy(ca, buy_amount)

        finally:
            self._processing.discard(ca)

    # ──────────────────────────────
    # 매수 실행
    # ──────────────────────────────

    async def _execute_buy(self, ca: str, amount: float):
        """Trojan 봇 인라인 버튼으로 매수"""
        print(f"[매수] CA: {ca} | 금액: {amount:.4f} SOL")

        try:
            # 1. CA 전송
            await self.client.send_message(self.trading_bot_username, ca)
            await asyncio.sleep(3)

            # 2. 봇 응답 (인라인 버튼 포함) 가져오기
            messages = await self.client.get_messages(self.trading_bot_username, limit=1)
            if not messages or not messages[0].buttons:
                print("[매수 실패] 봇 응답 없거나 버튼 없음")
                return
            bot_msg = messages[0]

            # 3. Buy 버튼 클릭
            if not await self._click_button(bot_msg, BUY_BUTTON_TEXTS, "Buy"):
                return
            await asyncio.sleep(2)

            # 4. 금액 입력 (봇이 amount 프롬프트를 보내는 경우)
            await self.client.send_message(self.trading_bot_username, f"{amount:.4f}")
            print(f"[매수] 금액 입력: {amount:.4f} SOL")
            await asyncio.sleep(5)

            # 5. 진입가 조회 (DexScreener)
            entry_price = await self._get_price(ca)
            if entry_price is None:
                print("[매수] ⚠️  진입가 조회 실패 — 0으로 기록 (모니터링은 계속)")
                entry_price = 0.0

            # 6. 포지션 등록
            self.positions[ca] = Position(
                ca=ca,
                entry_price_usd=entry_price,
                sol_invested=amount,
            )
            print(f"[매수 완료] 진입가: ${entry_price:.8f} | 포지션 모니터링 시작")

        except Exception as e:
            print(f"[매수 오류] {e}")

    # ──────────────────────────────
    # 가격 모니터링 루프
    # ──────────────────────────────

    async def _monitor_loop(self):
        """보유 포지션 가격을 30초마다 확인해 익절/손절 실행"""
        while True:
            await asyncio.sleep(PRICE_CHECK_INTERVAL)

            if not self.positions:
                continue

            for ca in list(self.positions.keys()):
                pos = self.positions[ca]
                current_price = await self._get_price(ca)

                if current_price is None:
                    continue

                pnl = pos.pnl_ratio(current_price)
                elapsed = (datetime.now() - pos.entry_time).seconds // 60
                print(f"[모니터] {ca[:8]}... | "
                      f"진입: ${pos.entry_price_usd:.8f} | "
                      f"현재: ${current_price:.8f} | "
                      f"P&L: {pnl * 100:+.1f}% | {elapsed}분 경과")

                if pnl >= TAKE_PROFIT_RATIO:
                    print(f"[익절] {ca[:8]}... +{pnl * 100:.1f}% 도달 → 100% 매도")
                    await self._execute_sell(ca, reason="익절")

                elif pnl <= -STOP_LOSS_RATIO:
                    print(f"[손절] {ca[:8]}... {pnl * 100:.1f}% 도달 → 100% 매도")
                    await self._execute_sell(ca, reason="손절")

    # ──────────────────────────────
    # 매도 실행
    # ──────────────────────────────

    async def _execute_sell(self, ca: str, reason: str = ""):
        """Trojan 봇 인라인 버튼으로 전량 매도"""
        try:
            # 1. CA 전송
            await self.client.send_message(self.trading_bot_username, ca)
            await asyncio.sleep(3)

            messages = await self.client.get_messages(self.trading_bot_username, limit=1)
            if not messages or not messages[0].buttons:
                print(f"[매도 실패] 봇 응답 없음 ({reason})")
                return
            bot_msg = messages[0]

            # 2. Sell 버튼 클릭
            if not await self._click_button(bot_msg, SELL_BUTTON_TEXTS, "Sell"):
                return
            await asyncio.sleep(2)

            # 3. 100% 전량 매도 버튼 클릭
            messages2 = await self.client.get_messages(self.trading_bot_username, limit=1)
            if messages2 and messages2[0].buttons:
                await self._click_button(messages2[0], SELL_ALL_BUTTON_TEXTS, "100%")

            print(f"[매도 완료] {reason} — {ca[:8]}...")

            # 포지션 제거
            self.positions.pop(ca, None)

            # 잔액 갱신
            await asyncio.sleep(5)
            await self.update_balance()

        except Exception as e:
            print(f"[매도 오류] {e}")

    # ──────────────────────────────
    # 공통 유틸
    # ──────────────────────────────

    async def _click_button(self, msg, candidates: list[str], label: str) -> bool:
        """
        인라인 버튼 중 candidates 텍스트와 일치하는 버튼 클릭.
        실패 시 실제 버튼 목록 출력 후 False 반환.
        """
        for text in candidates:
            try:
                await msg.click(text=text)
                return True
            except Exception:
                continue

        # 실패 시 실제 버튼 텍스트 출력 (디버깅용)
        print(f"[버튼 오류] '{label}' 버튼을 찾지 못했습니다. 실제 버튼 목록:")
        if msg.buttons:
            for row in msg.buttons:
                for btn in row:
                    print(f"          → '{btn.text}'")
        print(f"          위 텍스트를 BUY_BUTTON_TEXTS 또는 SELL_BUTTON_TEXTS에 추가하세요")
        return False

    async def _get_price(self, ca: str) -> float | None:
        """DexScreener API로 현재 USD 가격 조회 (무료, 인증 불필요)"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(DEXSCREENER_URL.format(ca=ca))
                if response.status_code != 200:
                    return None
                data = response.json()
                pairs = data.get("pairs")
                if pairs:
                    return float(pairs[0].get("priceUsd", 0))
        except Exception:
            pass
        return None


if __name__ == '__main__':
    bot = TelegramSignalBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("[시스템] 봇 종료")
