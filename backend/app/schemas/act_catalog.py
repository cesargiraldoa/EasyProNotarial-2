from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, validator


class ActCatalogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    label: str
    roles_json: str
    is_active: bool


class ActItemIn(BaseModel):
    code: str
    label: str
    act_order: int
    roles_json: str = "[]"

    @validator("roles_json", pre=True)
    def clean_roles_json(cls, v):
        if isinstance(v, list):
            return json.dumps(v, ensure_ascii=False)
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return json.dumps(parsed, ensure_ascii=False)
            except Exception:
                return "[]"
        return "[]"


class CaseActOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    act_code: str
    act_label: str
    act_order: int
    roles_json: str


class CaseActsPayload(BaseModel):
    acts: list[ActItemIn]
