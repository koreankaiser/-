import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# 1. Telegram 계정 설정
# ==========================================================
TELEGRAM_API_ID = int(os.environ["TELEGRAM_API_ID"])
TELEGRAM_API_HASH = os.environ["TELEGRAM_API_HASH"]

# ==========================================================
# 2. 시그널 채널 및 매수 봇 설정
# ==========================================================
SIGNAL_SOURCES = [
    "rich_adul", "au_call", "MetaGambler", "DegenSeals",
    "theosjournal1", "TrissysEdge", "PowsGemCalls",
    "fttrenches_sol", "fttrenches_volsm", "missorplays",
]

# Trojan 봇 유저네임
TRADING_BOT_USERNAME = "@menelaus_trojanbot"

# ==========================================================
# 3. 자동 매매 전략 설정
# ==========================================================
TRADE_AMOUNT_PCT = float(os.getenv("TRADE_AMOUNT_PCT", "0.10"))    # 잔액의 10%
TAKE_PROFIT_RATIO = float(os.getenv("TAKE_PROFIT_RATIO", "0.20"))  # 익절 +20%
STOP_LOSS_RATIO = float(os.getenv("STOP_LOSS_RATIO", "0.30"))      # 손절 -30%
