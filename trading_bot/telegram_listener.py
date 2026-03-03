"""
텔레그램 자동화 매매 봇

흐름: 시그널 채널 CA 감지 → Trojan 봇에 CA 전송 → 인라인 Buy 버튼 클릭 → 금액 입력
TP/SL: Trojan 봇 설정에서 미리 기본값으로 설정 필요 (봇 /start → Settings → TP/SL)
"""

import re
import asyncio
from telethon import TelegramClient, events
from config import (
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    SIGNAL_SOURCES,
    TRADING_BOT_USERNAME,
    TRADE_AMOUNT_PCT,
)

# Solana CA 패턴 (Base58, 32~44자)
CA_PATTERN = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')

# Trojan 봇 잔액 응답 파싱 패턴
# 봇이 실제로 어떤 형식으로 응답하는지 확인 후 필요시 수정
BALANCE_PATTERN = re.compile(r'(\d+\.?\d*)\s*SOL', re.IGNORECASE)

# Trojan 봇 Buy 버튼 텍스트 후보 (실제 버튼 텍스트 확인 후 수정)
BUY_BUTTON_TEXTS = ["Buy", "매수", "BUY", "🟢 Buy"]


class TelegramSignalBot:
    def __init__(self):
        self.client = TelegramClient('bot_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.current_balance_sol = 0.0
        self.trading_bot_username = TRADING_BOT_USERNAME
        self._processing: set[str] = set()  # 중복 CA 처리 방지

    async def start(self):
        await self.client.start()
        print("[시스템] 텔레그램 자동화 매매 봇 활성화")
        print(f"[설정] 감시 채널: {len(SIGNAL_SOURCES)}개")
        print(f"[설정] 대상 매수 봇: {self.trading_bot_username}")
        print(f"[설정] 투자 비율: {TRADE_AMOUNT_PCT * 100:.0f}%")
        print()
        print("⚠️  TP/SL 설정 안내:")
        print("   Trojan 봇은 텍스트 명령으로 TP/SL 설정 불가")
        print("   봇에서 직접: /start → Settings → TP/SL 기본값 설정 필요")
        print()

        await self.update_balance()

        @self.client.on(events.NewMessage(chats=SIGNAL_SOURCES))
        async def handler(event):
            if event.message.text:
                await self.process_message(event.message.text)

        print("[시스템] 시그널 대기 중...")
        await self.client.run_until_disconnected()

    async def update_balance(self) -> float:
        """
        Trojan 봇에 /start 전송 후 응답에서 SOL 잔액 파싱
        """
        print("[잔액] Trojan 봇에서 잔액 조회 중...")
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
                    print(f"[잔액] 현재 잔액: {self.current_balance_sol:.4f} SOL")
                    return self.current_balance_sol

            # 파싱 실패 시 — 잔액이 0이면 매수 불가
            if self.current_balance_sol == 0.0:
                print("[잔액] ⚠️  잔액 파싱 실패. Trojan 봇 응답 형식 확인 필요")
                print("[잔액] 봇에 /start 입력 후 응답 메시지에서 SOL 숫자 형식 확인하세요")
            else:
                print(f"[잔액] 파싱 실패, 기존 잔액 유지: {self.current_balance_sol:.4f} SOL")

        except Exception as e:
            print(f"[잔액] 조회 오류: {e}")

        return self.current_balance_sol

    async def process_message(self, text: str):
        """수신 메시지에서 CA 감지 후 매수 실행"""
        match = CA_PATTERN.search(text)
        if not match:
            return

        ca = match.group(0)

        if ca in self._processing:
            print(f"[중복] {ca[:8]}... 이미 처리 중, 스킵")
            return
        self._processing.add(ca)

        try:
            print(f"\n[시그널] CA 감지: {ca}")
            await self.update_balance()

            buy_amount = self.current_balance_sol * TRADE_AMOUNT_PCT

            if buy_amount < 0.01:
                print(f"[취소] 잔액 부족 — 매수 금액: {buy_amount:.4f} SOL (최소 0.01 SOL)")
                return

            await self.send_buy_command(ca, buy_amount)

        finally:
            await asyncio.sleep(300)  # 5분 후 중복 방지 해제
            self._processing.discard(ca)

    async def send_buy_command(self, ca: str, amount: float):
        """
        Trojan 봇 매수 실행 흐름:
          1. CA 전송 → 봇이 토큰 정보 + 인라인 버튼으로 응답
          2. Buy 버튼 클릭
          3. 금액 입력

        ⚠️  만약 버튼 클릭이 실패하면:
            BUY_BUTTON_TEXTS 리스트에 실제 버튼 텍스트를 추가하세요
            (봇에 CA 보내서 어떤 버튼이 뜨는지 직접 확인 필요)
        """
        print(f"[매수] Trojan 봇에 CA 전송: {ca}")
        print(f"[매수] 금액: {amount:.4f} SOL ({TRADE_AMOUNT_PCT * 100:.0f}%)")

        try:
            # 1단계: CA 전송
            await self.client.send_message(self.trading_bot_username, ca)
            await asyncio.sleep(3)  # 봇이 토큰 정보 로드하는 시간

            # 2단계: 봇 응답 메시지 (인라인 버튼 포함) 가져오기
            messages = await self.client.get_messages(self.trading_bot_username, limit=1)
            if not messages or not messages[0].buttons:
                print("[오류] 봇 응답 없거나 버튼 없음. CA가 유효한지, 봇이 응답했는지 확인하세요")
                return

            bot_msg = messages[0]
            print(f"[봇 응답] {bot_msg.text[:80] if bot_msg.text else '(텍스트 없음)'}...")

            # 3단계: Buy 버튼 찾아서 클릭
            clicked = False
            for btn_text in BUY_BUTTON_TEXTS:
                try:
                    await bot_msg.click(text=btn_text)
                    print(f"[성공] '{btn_text}' 버튼 클릭")
                    clicked = True
                    break
                except Exception:
                    continue

            if not clicked:
                # 버튼 텍스트 목록 출력 (디버깅용)
                print("[오류] Buy 버튼을 찾지 못했습니다. 봇 버튼 목록:")
                if bot_msg.buttons:
                    for row in bot_msg.buttons:
                        for btn in row:
                            print(f"         - '{btn.text}'")
                print("       BUY_BUTTON_TEXTS에 실제 버튼 텍스트를 추가하세요")
                return

            await asyncio.sleep(2)

            # 4단계: 금액 입력 (봇이 금액 입력 프롬프트를 보내는 경우)
            await self.client.send_message(self.trading_bot_username, f"{amount:.4f}")
            print(f"[성공] 매수 금액 입력 완료: {amount:.4f} SOL")

            # 매수 후 잔액 갱신
            await asyncio.sleep(5)
            await self.update_balance()

        except Exception as e:
            print(f"[오류] 매수 실패: {e}")


if __name__ == '__main__':
    bot = TelegramSignalBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("[시스템] 봇 종료")
