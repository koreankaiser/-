"""
Solana 지갑 관리 모듈
"""

import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from config import WALLET_PRIVATE_KEY, SOLANA_RPC_URL


def load_keypair() -> Keypair:
    """Private Key에서 Keypair 로드"""
    private_key_bytes = base58.b58decode(WALLET_PRIVATE_KEY)
    return Keypair.from_bytes(private_key_bytes)


async def get_sol_balance(client: AsyncClient, pubkey: str) -> float:
    """SOL 잔액 조회 (SOL 단위)"""
    pubkey_obj = Pubkey.from_string(pubkey)
    response = await client.get_balance(pubkey_obj)
    lamports = response.value
    return lamports / 1_000_000_000


def create_rpc_client() -> AsyncClient:
    """Solana RPC 클라이언트 생성"""
    return AsyncClient(SOLANA_RPC_URL)
