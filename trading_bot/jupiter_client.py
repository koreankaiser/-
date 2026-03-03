"""
Jupiter DEX API 클라이언트

Jupiter v6 API를 사용하여 Solana 토큰 스왑 및 가격 조회
"""

import json
import base64
import httpx
from typing import Optional
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from config import (
    JUPITER_QUOTE_URL,
    JUPITER_SWAP_URL,
    JUPITER_PRICE_URL,
    SOL_MINT,
    SOL_DECIMALS,
    SLIPPAGE_BPS,
)


async def get_token_price(mint_address: str) -> Optional[float]:
    """
    Jupiter Price API로 토큰 가격 조회 (USD 기준)
    실패 시 None 반환 (API 키 없거나 네트워크 오류 포함)
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                JUPITER_PRICE_URL,
                params={"ids": mint_address},
            )
            if response.status_code != 200:
                print(f"[Jupiter] 가격 조회 실패 (무시): {response.status_code}")
                return None
            data = response.json()
    except Exception as e:
        print(f"[Jupiter] 가격 조회 오류 (무시): {e}")
        return None

    price_data = data.get("data", {}).get(mint_address)
    if price_data:
        return float(price_data.get("price", 0) or 0) or None
    return None


async def get_quote(
    input_mint: str,
    output_mint: str,
    amount_lamports: int,
) -> Optional[dict]:
    """
    Jupiter에서 스왑 견적 조회

    Args:
        input_mint: 입력 토큰 민트 주소 (SOL이면 SOL_MINT)
        output_mint: 출력 토큰 민트 주소
        amount_lamports: 입력 금액 (lamports 단위)
    """
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount_lamports,
        "slippageBps": SLIPPAGE_BPS,
        "onlyDirectRoutes": "false",
        "asLegacyTransaction": "false",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(JUPITER_QUOTE_URL, params=params)
            if response.status_code != 200:
                print(f"[Jupiter] Quote 실패: {response.status_code} {response.text}")
                return None
            return response.json()
    except Exception as e:
        print(f"[Jupiter] Quote 연결 오류: {e}")
        return None


async def execute_swap(
    keypair: Keypair,
    rpc_client: AsyncClient,
    quote_response: dict,
) -> Optional[str]:
    """
    Jupiter 스왑 트랜잭션 실행

    Returns:
        트랜잭션 서명(signature) 또는 None (실패 시)
    """
    swap_request = {
        "quoteResponse": quote_response,
        "userPublicKey": str(keypair.pubkey()),
        "wrapAndUnwrapSol": True,
        "dynamicComputeUnitLimit": True,
        "prioritizationFeeLamports": "auto",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            JUPITER_SWAP_URL,
            json=swap_request,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            print(f"[Jupiter] Swap 요청 실패: {response.status_code} {response.text}")
            return None
        swap_data = response.json()

    # 트랜잭션 디코딩 및 서명
    swap_transaction_buf = base64.b64decode(swap_data["swapTransaction"])
    transaction = VersionedTransaction.from_bytes(swap_transaction_buf)
    signed_tx = keypair.sign_message(bytes(transaction.message))
    transaction.signatures[0] = signed_tx  # type: ignore

    # 트랜잭션 전송
    raw_tx = bytes(transaction)
    result = await rpc_client.send_raw_transaction(
        raw_tx,
        opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"),
    )

    if result.value:
        return str(result.value)
    return None


async def buy_token(
    keypair: Keypair,
    rpc_client: AsyncClient,
    mint_address: str,
    sol_amount: float,
) -> Optional[str]:
    """
    SOL → 토큰 매수

    Returns:
        트랜잭션 서명 또는 None
    """
    amount_lamports = int(sol_amount * (10 ** SOL_DECIMALS))
    print(f"[Jupiter] 매수 견적 조회: {sol_amount} SOL → {mint_address}")

    quote = await get_quote(SOL_MINT, mint_address, amount_lamports)
    if not quote:
        return None

    out_amount = int(quote.get("outAmount", 0))
    print(f"[Jupiter] 예상 수령 토큰: {out_amount}")

    return await execute_swap(keypair, rpc_client, quote)


async def sell_token(
    keypair: Keypair,
    rpc_client: AsyncClient,
    mint_address: str,
    token_amount: int,
) -> Optional[str]:
    """
    토큰 → SOL 매도

    Args:
        token_amount: 매도할 토큰 수량 (토큰 소수점 포함 raw amount)

    Returns:
        트랜잭션 서명 또는 None
    """
    print(f"[Jupiter] 매도 견적 조회: {token_amount} {mint_address} → SOL")

    quote = await get_quote(mint_address, SOL_MINT, token_amount)
    if not quote:
        return None

    return await execute_swap(keypair, rpc_client, quote)


async def get_token_balance(
    rpc_client: AsyncClient,
    pubkey: str,
    mint_address: str,
) -> Optional[int]:
    """
    특정 토큰의 보유량 조회 (raw amount)
    """
    from solders.pubkey import Pubkey

    owner = Pubkey.from_string(pubkey)
    mint = Pubkey.from_string(mint_address)

    response = await rpc_client.get_token_accounts_by_owner(
        owner,
        {"mint": str(mint)},
        encoding="jsonParsed",
    )

    accounts = response.value
    if not accounts:
        return 0

    token_amount = accounts[0].account.data["parsed"]["info"]["tokenAmount"]["amount"]
    return int(token_amount)
