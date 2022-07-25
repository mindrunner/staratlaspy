import typing
from dataclasses import dataclass
from base64 import b64decode
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class PlayerFactionDataJSON(typing.TypedDict):
    owner: str
    enlisted_at_timestamp: int
    faction_id: int
    bump: int
    padding: list[int]


@dataclass
class PlayerFactionData:
    discriminator: typing.ClassVar = b"/,\xff\x0fgM\x8b\xf7"
    layout: typing.ClassVar = borsh.CStruct(
        "owner" / BorshPubkey,
        "enlisted_at_timestamp" / borsh.I64,
        "faction_id" / borsh.U8,
        "bump" / borsh.U8,
        "padding" / borsh.U64[5],
    )
    owner: PublicKey
    enlisted_at_timestamp: int
    faction_id: int
    bump: int
    padding: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["PlayerFactionData"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp["result"]["value"]
        if info is None:
            return None
        if info["owner"] != str(PROGRAM_ID):
            raise ValueError("Account does not belong to this program")
        bytes_data = b64decode(info["data"][0])
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[PublicKey],
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.List[typing.Optional["PlayerFactionData"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["PlayerFactionData"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "PlayerFactionData":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = PlayerFactionData.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            owner=dec.owner,
            enlisted_at_timestamp=dec.enlisted_at_timestamp,
            faction_id=dec.faction_id,
            bump=dec.bump,
            padding=dec.padding,
        )

    def to_json(self) -> PlayerFactionDataJSON:
        return {
            "owner": str(self.owner),
            "enlisted_at_timestamp": self.enlisted_at_timestamp,
            "faction_id": self.faction_id,
            "bump": self.bump,
            "padding": self.padding,
        }

    @classmethod
    def from_json(cls, obj: PlayerFactionDataJSON) -> "PlayerFactionData":
        return cls(
            owner=PublicKey(obj["owner"]),
            enlisted_at_timestamp=obj["enlisted_at_timestamp"],
            faction_id=obj["faction_id"],
            bump=obj["bump"],
            padding=obj["padding"],
        )
