"""
텔레그램 시그널 리스너 + Trojan 봇 실거래 연동

핵심 로직:
  1. 시그널 채널 → CA 감지
  2. Trojan 봇에 CA 전송 → 토큰 구매 페이지 수신
  3. [X SOL 🖊️] 버튼 클릭 → 금액 입력 → [BUY] 버튼 클릭 → 실거래 실행
  4. DexScreener로 가격 모니터링 → 익절/손절 시 [SELL] 버튼 클릭
"""

import asyncio
import re
import time

import httpx
from telethon import TelegramClient, events

from config import (
    TELEGRAM_API_ID, TELEGRAM_API_HASH,
    SIGNAL_SOURCES, TROJAN_BOT,
    TRADE_AMOUNT_PCT, TAKE_PROFIT_RATIO, STOP_LOSS_RATIO,
    PRICE_CHECK_INTERVAL,
)

# Solana CA 패턴 (Base58, 32~44자, pump 접미사 포함)
CA_PATTERN = re.compile(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}(?:pump)?\b')

# 알려진 고정 주소 (CA가 아닌 것들)
KNOWN_ADDRESSES = {
    "So11111111111111111111111111111111111111112",    # Wrapped SOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    "11111111111111111111111111111111",               # System Program
}


# ────────────────────────────────────────────────
# 가격 조회 (DexScreener)
# ────────────────────────────────────────────────

async def get_token_price(ca: str) -> float:
    """DexScreener API로 현재 USD 가격 조회"""
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://api.dexscreener.com/latest/dex/tokens/{ca}")
            pairs = r.json().get("pairs") or []
            if pairs:
                return float(pairs[0].get("priceUsd") or 0)
    except Exception:
        pass
    return 0.0


# ────────────────────────────────────────────────
# 포지션 데이터 클래스
# ────────────────────────────────────────────────

class Position:
    def __init__(self, ca: str, entry_price: float, sol_amount: float):
        self.ca = ca
        self.entry_price = entry_price
        self.sol_amount = sol_amount
        self.entry_time = time.time()
        self.sold = False


# ────────────────────────────────────────────────
# 메인 봇 클래스
# ────────────────────────────────────────────────

class TelegramSignalBot:
    def __init__(self):
        self.client = TelegramClient(
            "trading_session", TELEGRAM_API_ID, TELEGRAM_API_HASH
        )
        self.positions: dict[str, Position] = {}
        self.active_cas: set[str] = set()
        self.sol_balance = 0.0
        # Trojan 봇 인터랙션 직렬화 (동시 접근 방지)
        self._trojan_lock = asyncio.Lock()

    # ──────────────────────────────────────────
    # 유틸
    # ──────────────────────────────────────────

    async def _click_button(self, message, keyword: str) -> bool:
        """
        메시지 인라인 키보드에서 keyword를 포함한 버튼을 찾아 클릭.
        성공하면 True 반환.
        """
        if not message or not message.buttons:
            return False
        for row in message.buttons:
            for btn in row:
                if btn.text and keyword.lower() in btn.text.lower():
                    await btn.click()
                    return True
        return False

    def _log_buttons(self, message, label: str):
        """디버그: 현재 메시지의 버튼 목록 출력"""
        if message and message.buttons:
            rows = [[b.text for b in row] for row in message.buttons]
            print(f"[디버그] {label} 버튼: {rows}")
        else:
            print(f"[디버그] {label}: 버튼 없음")

    async def _wait_response_or_edit(self, conv, timeout: float = 10.0):
        """새 메시지 또는 기존 메시지 수정 중 먼저 오는 것을 반환"""
        tasks = [
            asyncio.create_task(
                asyncio.wait_for(conv.get_response(), timeout=timeout)
            ),
            asyncio.create_task(
                asyncio.wait_for(conv.get_edit(), timeout=timeout)
            ),
        ]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
        result = done.pop().result() if done else None
        return result

    # ──────────────────────────────────────────
    # 잔액 조회
    # ──────────────────────────────────────────

    async def get_sol_balance(self) -> float:
        """Trojan 봇 /start 응답에서 SOL 잔액 파싱"""
        try:
            async with self._trojan_lock:
                async with self.client.conversation(TROJAN_BOT, timeout=20) as conv:
                    await conv.send_message("/start")
                    resp = await conv.get_response()
                    m = re.search(r'Balance:\s*([\d.]+)\s*SOL', resp.text or "")
                    if m:
                        return float(m.group(1))
        except Exception as e:
            print(f"[잔액] 조회 오류: {e}")
        return self.sol_balance

    # ──────────────────────────────────────────
    # 매수 (버튼 클릭)
    # ──────────────────────────────────────────

    async def execute_buy(self, ca: str, sol_amount: float) -> float:
        """
        Trojan 봇 인라인 버튼 클릭으로 매수 실행.

        흐름:
          CA 전송
          → 토큰 구매 페이지 수신 (버튼: X SOL 🖊️, BUY 등)
          → [X SOL 🖊️] 클릭
          → sol_amount 입력
          → 업데이트된 페이지 수신
          → [BUY] 클릭
          → 확인 메시지 수신 → 진입가 파싱/조회
        """
        print(f"[매수] CA: {ca[:8]}... | 금액: {sol_amount:.4f} SOL")

        try:
            async with self._trojan_lock:
                async with self.client.conversation(TROJAN_BOT, timeout=60) as conv:

                    # ① CA 전송 → 토큰 구매 페이지
                    await conv.send_message(ca)
                    page = await conv.get_response()

                    if not page.buttons:
                        print("[매수] 오류: Trojan 응답에 버튼 없음")
                        self._log_buttons(page, "CA 응답")
                        return 0.0

                    # ② [X SOL 🖊️] 버튼 클릭 → 커스텀 금액 입력 모드
                    if await self._click_button(page, "X SOL"):
                        # Trojan이 새 메시지 또는 편집으로 응답할 수 있음
                        try:
                            page = await self._wait_response_or_edit(conv, timeout=10)
                        except Exception:
                            pass  # 입력 대기 상태일 수 있으므로 계속

                        # ③ SOL 금액 입력
                        await conv.send_message(f"{sol_amount:.4f}")

                        # ④ 업데이트된 구매 페이지 수신
                        try:
                            page = await self._wait_response_or_edit(conv, timeout=10)
                        except Exception:
                            pass
                    else:
                        # X SOL 버튼이 없으면 현재 선택된 프리셋(✅ 0.5 SOL)으로 진행
                        print("[매수] 커스텀 금액 버튼 없음 — 기본 프리셋으로 진행")

                    # ⑤ [BUY] 버튼 클릭
                    if not await self._click_button(page, "BUY"):
                        print("[매수] 오류: BUY 버튼을 찾을 수 없음")
                        self._log_buttons(page, "BUY 시도 시점")
                        return 0.0

                    # ⑥ 매수 확인 메시지 대기
                    try:
                        confirm = await asyncio.wait_for(conv.get_response(), timeout=30)
                        confirm_text = confirm.text or ""
                    except asyncio.TimeoutError:
                        print("[매수] 확인 메시지 타임아웃 — 외부 API로 가격 조회")
                        confirm_text = ""

                    # ⑦ 진입가 파싱 (실패 시 DexScreener 조회)
                    price = _parse_price_from_text(confirm_text)
                    if price == 0.0:
                        await asyncio.sleep(3)
                        price = await get_token_price(ca)

                    if price > 0:
                        print(f"[매수 완료] 진입가: ${price:.8f}")
                    else:
                        print(f"[매수] ⚠️  진입가 조회 실패 — 0으로 기록 (모니터링은 계속)")
                        if confirm_text:
                            print(f"[매수] Trojan 응답: {confirm_text[:200]}")

                    return price

        except asyncio.TimeoutError:
            print("[매수] 전체 타임아웃")
        except Exception as e:
            print(f"[매수] 오류: {type(e).__name__}: {e}")

        return 0.0

    # ──────────────────────────────────────────
    # 매도 (버튼 클릭)
    # ──────────────────────────────────────────

    async def execute_sell(self, ca: str, reason: str = "익절") -> bool:
        """
        Trojan 봇 인라인 버튼 클릭으로 100% 매도 실행.

        흐름:
          CA 전송 (컨텍스트 설정)
          → /start switchToSell 전송 → 매도 페이지 수신
          → [100%] 버튼 클릭 (없으면 [SELL] 직접 클릭)
          → 확인 메시지 수신
        """
        print(f"[매도] {ca[:8]}... ({reason})")

        try:
            async with self._trojan_lock:
                async with self.client.conversation(TROJAN_BOT, timeout=60) as conv:

                    # ① CA 전송 → 컨텍스트 설정 (Trojan이 어떤 CA인지 기억)
                    await conv.send_message(ca)
                    await conv.get_response()  # 토큰 페이지 (사용하지 않음)

                    # ② 매도 모드 전환
                    #    t.me/menelaus_trojanbot?start=switchToSell 딥링크 클릭과 동일
                    await conv.send_message("/start switchToSell")

                    try:
                        sell_page = await asyncio.wait_for(
                            conv.get_response(), timeout=15
                        )
                    except asyncio.TimeoutError:
                        print("[매도] 매도 페이지 수신 타임아웃")
                        return False

                    # ③ [100%] 버튼 클릭 시도
                    sold = False
                    for keyword in ["100%", "100", "SELL", "Sell"]:
                        if await self._click_button(sell_page, keyword):
                            sold = True
                            break

                    if not sold:
                        print("[매도] SELL/100% 버튼을 찾을 수 없음")
                        self._log_buttons(sell_page, "매도 페이지")
                        return False

                    # ④ SELL 버튼이 별도로 있는 경우 처리
                    try:
                        confirm = await asyncio.wait_for(
                            conv.get_response(), timeout=20
                        )
                        # 100%만 눌렀을 때 추가 SELL 버튼이 있을 수 있음
                        if confirm.buttons and await self._click_button(confirm, "SELL"):
                            confirm = await asyncio.wait_for(
                                conv.get_response(), timeout=20
                            )
                    except asyncio.TimeoutError:
                        # 타임아웃이어도 매도가 실행됐을 수 있음
                        pass

                    print(f"[매도 완료] {reason} — {ca[:8]}...")
                    return True

        except asyncio.TimeoutError:
            print(f"[매도] 전체 타임아웃 ({ca[:8]}...)")
        except Exception as e:
            print(f"[매도] 오류: {type(e).__name__}: {e}")

        return False

    # ──────────────────────────────────────────
    # 포지션 P&L 모니터링
    # ──────────────────────────────────────────

    async def monitor_position(self, pos: Position):
        """포지션 P&L 모니터링 → 익절/손절 조건 충족 시 매도"""
        short = pos.ca[:8] + "..."

        while not pos.sold:
            await asyncio.sleep(PRICE_CHECK_INTERVAL)
            if pos.sold:
                break

            cur = await get_token_price(pos.ca)
            if cur == 0 or pos.entry_price == 0:
                continue

            pnl = (cur - pos.entry_price) / pos.entry_price
            elapsed = int((time.time() - pos.entry_time) / 60)

            print(
                f"[모니터] {short} | "
                f"진입: ${pos.entry_price:.8f} | "
                f"현재: ${cur:.8f} | "
                f"P&L: {pnl*100:+.1f}% | "
                f"{elapsed}분 경과"
            )

            if pnl >= TAKE_PROFIT_RATIO:
                print(f"[익절] {short} {pnl*100:+.1f}% 도달 → 100% 매도")
                pos.sold = True
                await self.execute_sell(pos.ca, "익절")
                break

            if pnl <= -STOP_LOSS_RATIO:
                print(f"[손절] {short} {pnl*100:+.1f}% 도달 → 100% 매도")
                pos.sold = True
                await self.execute_sell(pos.ca, "손절")
                break

        self.active_cas.discard(pos.ca)
        self.positions.pop(pos.ca, None)

    # ──────────────────────────────────────────
    # 시그널 처리
    # ──────────────────────────────────────────

    async def handle_signal(self, ca: str):
        """새 CA 시그널: 잔액 확인 → 매수 → 포지션 모니터링 시작"""
        if ca in self.active_cas or ca in KNOWN_ADDRESSES:
            return

        self.active_cas.add(ca)
        print(f"\n[시그널] CA 감지: {ca}")

        # 잔액 조회
        print("[잔액] 조회 중...")
        self.sol_balance = await self.get_sol_balance()
        print(f"[잔액] {self.sol_balance:.4f} SOL")

        trade_sol = round(self.sol_balance * TRADE_AMOUNT_PCT, 4)
        if trade_sol < 0.001:
            print(f"[경고] 잔액 부족 ({self.sol_balance:.4f} SOL), 건너뜀")
            self.active_cas.discard(ca)
            return

        # 매수 실행
        print(f"[매수] CA: {ca} | 금액: {trade_sol:.4f} SOL")
        print(f"[매수] 금액 입력: {trade_sol:.4f} SOL")
        entry_price = await self.execute_buy(ca, trade_sol)

        if entry_price == 0.0:
            print(f"[매수 실패] {ca[:8]}... — 포지션 없음")
            self.active_cas.discard(ca)
            return

        pos = Position(ca=ca, entry_price=entry_price, sol_amount=trade_sol)
        self.positions[ca] = pos
        print(f"[매수 완료] 진입가: ${entry_price:.8f} | 포지션 모니터링 시작")

        asyncio.create_task(self.monitor_position(pos))

    # ──────────────────────────────────────────
    # 시작
    # ──────────────────────────────────────────

    async def start(self):
        await self.client.start()

        # 초기 잔액 조회
        print("[잔액] 조회 중...")
        self.sol_balance = await self.get_sol_balance()
        print(f"[잔액] {self.sol_balance:.4f} SOL")

        # 시그널 채널 엔티티 해석
        entities = []
        for src in SIGNAL_SOURCES:
            try:
                ent = await self.client.get_entity(src)
                entities.append(ent)
            except Exception as e:
                print(f"[경고] 채널 '{src}' 접근 실패: {e}")

        if not entities:
            print("[오류] 접근 가능한 채널이 없습니다")
            return

        @self.client.on(events.NewMessage(chats=entities))
        async def on_new_message(event):
            text = event.message.text or ""
            for ca in set(CA_PATTERN.findall(text)):
                if ca not in KNOWN_ADDRESSES and len(ca) >= 32:
                    asyncio.create_task(self.handle_signal(ca))

        print("[시스템] 시그널 대기 중...")
        await self.client.run_until_disconnected()


# ────────────────────────────────────────────────
# 헬퍼
# ────────────────────────────────────────────────

def _parse_price_from_text(text: str) -> float:
    """Trojan 확인 메시지에서 USD 가격 파싱 (최선 시도)"""
    if not text:
        return 0.0
    m = re.search(r'\$\s*([\d]+\.[\d]+(?:e[+-]?\d+)?)', text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return 0.0
