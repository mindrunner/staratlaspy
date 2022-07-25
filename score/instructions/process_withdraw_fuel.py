from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class ProcessWithdrawFuelArgs(typing.TypedDict):
    staking_bump: int
    scorevars_bump: int
    scorevars_ship_bump: int
    escrow_auth_bump: int
    escrow_bump: int


layout = borsh.CStruct(
    "staking_bump" / borsh.U8,
    "scorevars_bump" / borsh.U8,
    "scorevars_ship_bump" / borsh.U8,
    "escrow_auth_bump" / borsh.U8,
    "escrow_bump" / borsh.U8,
)


class ProcessWithdrawFuelAccounts(typing.TypedDict):
    player_account: PublicKey
    ship_staking_account: PublicKey
    score_vars_account: PublicKey
    score_vars_ship_account: PublicKey
    fuel_token_account_escrow: PublicKey
    fuel_token_account_return: PublicKey
    fuel_mint: PublicKey
    escrow_authority: PublicKey
    token_program: PublicKey
    clock: PublicKey
    ship_mint: PublicKey


def process_withdraw_fuel(
    args: ProcessWithdrawFuelArgs, accounts: ProcessWithdrawFuelAccounts
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["player_account"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["ship_staking_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["score_vars_account"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["score_vars_ship_account"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["fuel_token_account_escrow"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["fuel_token_account_return"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=accounts["fuel_mint"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["escrow_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["clock"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["ship_mint"], is_signer=False, is_writable=False),
    ]
    identifier = b"-\x93\x93\xa3 \xdd\xa1\xb0"
    encoded_args = layout.build(
        {
            "staking_bump": args["staking_bump"],
            "scorevars_bump": args["scorevars_bump"],
            "scorevars_ship_bump": args["scorevars_ship_bump"],
            "escrow_auth_bump": args["escrow_auth_bump"],
            "escrow_bump": args["escrow_bump"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
