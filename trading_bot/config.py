import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API
TELEGRAM_API_ID = int(os.environ["TELEGRAM_API_ID"])
TELEGRAM_API_HASH = os.environ["TELEGRAM_API_HASH"]

# 시그널 감시 채널 목록
SIGNAL_SOURCES = [
    "rich_adul", "au_call", "MetaGambler", "DegenSeals",
    "theosjournal1", "TrissysEdge", "PowsGemCalls",
    "fttrenches_sol", "fttrenches_volsm", "missorplays",
]

# Trojan 봇 유저네임
TROJAN_BOT = "menelaus_trojanbot"

# 매매 설정
TRADE_AMOUNT_PCT     = float(os.getenv("TRADE_AMOUNT_PCT",    "0.10"))  # 잔액의 10%
TAKE_PROFIT_RATIO    = float(os.getenv("TAKE_PROFIT_RATIO",   "0.20"))  # +20% 익절
STOP_LOSS_RATIO      = float(os.getenv("STOP_LOSS_RATIO",     "0.30"))  # -30% 손절
PRICE_CHECK_INTERVAL = float(os.getenv("PRICE_CHECK_INTERVAL","30"))    # 초
SLIPPAGE_BPS         = int(os.getenv("SLIPPAGE_BPS",          "300"))
FEE_ESTIMATE_BPS     = int(os.getenv("FEE_ESTIMATE_BPS",      "100"))
