import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_API_ID = int(os.environ["TELEGRAM_API_ID"])
TELEGRAM_API_HASH = os.environ["TELEGRAM_API_HASH"]

# 다중 채널 지원: 쉼표로 구분된 채널 username 목록
# 예: rich_adul,au_call,MetaGambler
_raw_sources = os.environ.get("SIGNAL_SOURCES", os.environ.get("SIGNAL_SOURCE", ""))
SIGNAL_SOURCES: list[str] = [s.strip() for s in _raw_sources.split(",") if s.strip()]

# Solana
WALLET_PRIVATE_KEY = os.environ["WALLET_PRIVATE_KEY"]
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

# 매매 설정
TRADE_AMOUNT_PCT = float(os.getenv("TRADE_AMOUNT_PCT", "0.10"))     # 자산의 10% 복리식
TAKE_PROFIT_RATIO = float(os.getenv("TAKE_PROFIT_RATIO", "0.20"))   # +20% 익절
STOP_LOSS_RATIO = float(os.getenv("STOP_LOSS_RATIO", "0.30"))       # -30% 손절
PRICE_CHECK_INTERVAL = int(os.getenv("PRICE_CHECK_INTERVAL", "30"))

# 슬리피지 허용치 (bps, 100 = 1%)
SLIPPAGE_BPS = int(os.getenv("SLIPPAGE_BPS", "300"))                # 슬리피지 3%

# 예상 왕복 수수료 추정 (bps): 매수 + 매도 네트워크/우선순위 수수료
# 실제 익절/손절 P&L 표시에 반영 (트리거 기준은 원가 기준 유지)
FEE_ESTIMATE_BPS = int(os.getenv("FEE_ESTIMATE_BPS", "100"))        # 수수료 추정 ~1%

# Jupiter API (v1 - 신규 엔드포인트)
JUPITER_QUOTE_URL = "https://api.jup.ag/swap/v1/quote"
JUPITER_SWAP_URL = "https://api.jup.ag/swap/v1/swap"
JUPITER_PRICE_URL = "https://api.jup.ag/price/v2"

# SOL 토큰 민트 주소
SOL_MINT = "So11111111111111111111111111111111111111112"

# SOL 소수점 (lamports)
SOL_DECIMALS = 9
