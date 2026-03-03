"""
텔레그램 자동화 매매 봇

시그널 채널 감시 → CA 감지 → Trojan 봇에 매수 명령 전송
잔액 10% 복리 매수, TP 20% / SL 30%
"""

import re
import asyncio
from telethon import TelegramClient, events
from config import (
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    SIGNAL_SOURCES,
    TRADE_AMOUNT_PCT,
    TAKE_PROFIT_RATIO,
    STOP_LOSS_RATIO,
)


# Solana CA 패턴 (Base58, 32~44자)
CA_PATTERN = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')

# Trojan 봇이 /wallet 응답에서 보내는 잔액 패턴 예시
# 실제 응답 형태를 확인 후 필요하면 수정하세요
# 예: "💰 Balance: 4.2891 SOL" 또는 "SOL: 4.2891"
BALANCE_PATTERN = re.compile(r'(\d+\.?\d*)\s*SOL', re.IGNORECASE)


class TelegramSignalBot:
    def __init__(self):
        self.client = TelegramClient('bot_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.current_balance_sol = 0.0
        self.trading_bot_username = "@menelaus_trojanbot"
        # 중복 매수 방지: 처리 중인 CA 추적
        self._processing: set[str] = set()

    async def start(self):
        await self.client.start()
        print("[시스템] 텔레그램 자동화 매매 봇 활성화")
        print(f"[설정] 감시 채널: {len(SIGNAL_SOURCES)}개")
        print(f"[설정] 대상 매수 봇: {self.trading_bot_username}")
        print(f"[설정] 투자 비율: {TRADE_AMOUNT_PCT * 100:.0f}% | TP: {TAKE_PROFIT_RATIO * 100:.0f}% | SL: {STOP_LOSS_RATIO * 100:.0f}%")

        # 초기 잔액 조회
        await self.update_balance()

        @self.client.on(events.NewMessage(chats=SIGNAL_SOURCES))
        async def handler(event):
            if event.message.text:
                await self.process_message(event.message.text)

        print("[시스템] 시그널 대기 중...")
        await self.client.run_until_disconnected()

    async def update_balance(self) -> float:
        """
        Trojan 봇에 /wallet 명령을 보내고 응답에서 SOL 잔액을 파싱합니다.

        ⚠️ 실제 봇의 응답 형태에 맞게 BALANCE_PATTERN을 수정하세요.
        확인 방법: 봇에 /wallet 직접 입력 후 응답 메시지 형태 확인
        """
        print("[잔액] Trojan 봇에 잔액 조회 중...")
        try:
            await self.client.send_message(self.trading_bot_username, "/wallet")
            await asyncio.sleep(3)  # 봇 응답 대기

            # 봇으로부터 가장 최근 수신 메시지 읽기
            messages = await self.client.get_messages(self.trading_bot_username, limit=3)
            for msg in messages:
                if not msg.text:
                    continue
                match = BALANCE_PATTERN.search(msg.text)
                if match:
                    self.current_balance_sol = float(match.group(1))
                    print(f"[잔액] 현재 잔액: {self.current_balance_sol:.4f} SOL")
                    return self.current_balance_sol

            # 파싱 실패 시 기존 잔액 유지
            print(f"[잔액] 파싱 실패 - 기존 잔액 유지: {self.current_balance_sol:.4f} SOL")
            print(f"[잔액] 봇 응답 확인 필요. BALANCE_PATTERN을 봇 응답 형태에 맞게 수정하세요.")

        except Exception as e:
            print(f"[잔액] 조회 오류: {e}")

        return self.current_balance_sol

    async def process_message(self, text: str):
        """수신 메시지에서 CA 감지 후 매수 실행"""
        match = CA_PATTERN.search(text)
        if not match:
            return

        ca = match.group(0)

        # 중복 처리 방지
        if ca in self._processing:
            return
        self._processing.add(ca)

        try:
            print(f"\n[시그널] CA 감지: {ca}")

            # 최신 잔액으로 갱신
            await self.update_balance()

            buy_amount = self.current_balance_sol * TRADE_AMOUNT_PCT

            if buy_amount < 0.01:
                print(f"[취소] 잔액 부족: {buy_amount:.4f} SOL (최소 0.01 SOL 필요)")
                return

            await self.send_buy_command(ca, buy_amount)

        finally:
            # 처리 완료 후 목록에서 제거 (5분 후)
            await asyncio.sleep(300)
            self._processing.discard(ca)

    async def send_buy_command(self, ca: str, amount: float):
        """
        Trojan 봇에 매수 명령 전송

        ⚠️ 명령어 형식은 봇마다 다릅니다. 아래 중 실제 봇이 지원하는 형식을 확인하세요:

        형식 A (명령어 방식):  /buy {ca} {amount:.4f}
        형식 B (CA만 전송):   {ca}  → 봇이 인라인 버튼으로 응답 → 버튼 클릭 필요
        형식 C (설정 후 매수): /settings → TP/SL 설정 후 /buy {ca} {amount:.4f}

        현재는 형식 A를 사용합니다. 봇 /help 명령으로 지원 명령어를 확인하세요.
        """
        tp_pct = int(TAKE_PROFIT_RATIO * 100)  # 예: 0.20 → 20
        sl_pct = int(STOP_LOSS_RATIO * 100)    # 예: 0.30 → 30

        # ── 아래 command 형식을 실제 봇 명령어에 맞게 수정하세요 ──
        command = f"/buy {ca} {amount:.4f} -tp {tp_pct} -sl {sl_pct}"

        print(f"[매수] {self.trading_bot_username}에게 전송: {command}")
        print(f"[매수] 금액: {amount:.4f} SOL | TP: {tp_pct}% | SL: {sl_pct}%")

        try:
            await self.client.send_message(self.trading_bot_username, command)
            print("[성공] 매수 명령 전송 완료")

            # 매수 후 잔액 갱신
            await asyncio.sleep(5)
            await self.update_balance()

        except Exception as e:
            print(f"[오류] 명령어 전송 실패: {e}")


if __name__ == '__main__':
    bot = TelegramSignalBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("[시스템] 봇 종료")
