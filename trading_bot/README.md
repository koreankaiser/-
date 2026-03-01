# Solana 밈코인 자동매매 봇

텔레그램 시그널을 받아 Solana DEX(Jupiter)에서 자동으로 매매하는 봇입니다.

## 기능

- 텔레그램 봇/채널에서 **NEW-LAUNCH SIGNAL** 자동 감지
- Jupiter Aggregator를 통한 최적 경로 **자동 매수**
- **+30% 익절 / -30% 손절** 자동 매도 (설정 가능)
- 실시간 포지션 손익 모니터링

## 설치 방법

```bash
cd trading_bot

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 값 입력
```

## 환경 변수 설정 (.env)

### 1. Telegram API 자격증명 발급
1. https://my.telegram.org 접속
2. "API development tools" 클릭
3. 앱 생성 후 `api_id`와 `api_hash` 복사

### 2. Solana 지갑 Private Key
- Phantom 지갑: 설정 → 보안 및 개인정보 → Private Key 내보내기
- **주의**: Private Key는 절대 공유하지 마세요!

### 3. 시그널 소스 (SIGNAL_SOURCE)
- 시그널을 보내는 봇의 username (예: `onchaincrime_bot`)
- `@` 없이 username만 입력

## 실행

```bash
python main.py
```

첫 실행 시 텔레그램 전화번호 인증이 필요합니다.

## 감지하는 시그널 형식

```
🚀 NEW-LAUNCH SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━
Token: - $WarGPT
├ 6JFvA3ZKEfi3wDnzEVB3jzMGsLfcqVr4oqi3BzXHpump
└ 👾 #SOL
...
```

## 주의사항

- **밈코인 투자는 극도로 위험**합니다. 원금 손실 가능성이 있습니다.
- RPC 속도를 위해 **Helius** 또는 **QuickNode** 유료 RPC 사용을 강력 권장합니다.
- 봇 운영 중에는 충분한 SOL 잔액을 유지하세요 (가스비 포함).
- Private Key는 `.env` 파일에만 보관하고 절대 공유하지 마세요.

## 파일 구조

```
trading_bot/
├── main.py              # 진입점
├── config.py            # 설정
├── signal_parser.py     # 시그널 파싱
├── jupiter_client.py    # Jupiter DEX API
├── solana_wallet.py     # 지갑 관리
├── position_manager.py  # 포지션 & TP/SL
├── telegram_listener.py # 텔레그램 리스너
├── requirements.txt
└── .env.example
```
