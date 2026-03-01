import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_API_ID = int(os.environ["TELEGRAM_API_ID"])
TELEGRAM_API_HASH = os.environ["TELEGRAM_API_HASH"]
SIGNAL_SOURCE = os.environ["SIGNAL_SOURCE"]

# Solana
WALLET_PRIVATE_KEY = os.environ["WALLET_PRIVATE_KEY"]
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

# 매매 설정
TRADE_AMOUNT_SOL = float(os.getenv("TRADE_AMOUNT_SOL", "0.5"))
TAKE_PROFIT_RATIO = float(os.getenv("TAKE_PROFIT_RATIO", "0.30"))
STOP_LOSS_RATIO = float(os.getenv("STOP_LOSS_RATIO", "0.30"))
PRICE_CHECK_INTERVAL = int(os.getenv("PRICE_CHECK_INTERVAL", "30"))
SLIPPAGE_BPS = int(os.getenv("SLIPPAGE_BPS", "300"))

# Jupiter API
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"
JUPITER_PRICE_URL = "https://price.jup.ag/v4/price"

# SOL 토큰 민트 주소
SOL_MINT = "So11111111111111111111111111111111111111112"

# SOL 소수점 (lamports)
SOL_DECIMALS = 9
