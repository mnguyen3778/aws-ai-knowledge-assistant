import json
from typing import Any, Protocol


class ContractSerializable(Protocol):
    def to_dict(self) -> dict[str, Any]:
        ...


def dumps_contract_json(value: ContractSerializable | dict[str, Any]) -> str:
    if hasattr(value, "to_dict"):
        payload = value.to_dict()
    else:
        payload = value

    return json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
