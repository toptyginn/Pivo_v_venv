from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

def now_iso_time() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()

class User(BaseModel):
    id: int
    username: str
    role: Literal["user", "admin"]
    password: str

class DocumentBase(BaseModel):
    title: str
    content: str
    category: str
    is_public: bool = False

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    created_by: int
    created_at: str = Field(default_factory=now_iso_time)
    last_modified: str = Field(default_factory=now_iso_time)

class DocumentListOut(BaseModel):
    id: int
    title: str
    category: str
    is_public: bool
    created_by: int
    created_at: str
    last_modified: str

class DocumentDetailOut(BaseModel):
    id: int
    title: str
    content: str
    category: str
    is_public: bool
    created_by: int
    permission_level: Optional[Literal["read", "write"]]
    created_at: str
    last_modified: str

class PermissionEntry(BaseModel):
    user_id: int
    permission_level: Literal["read", "write"]

class ShareRequest(BaseModel):
    user_id: int
    permission_level: Literal["read", "write"]

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    user_id: int
    username: str
    role: str
    token: Optional[str] = None

class CacheClearResponse(BaseModel):
    message: str
    cleared_keys: Optional[List[str]] = None

class SharedDocumentOut(BaseModel):
    id: int
    title: str
    category: str
    created_by: int
    permission_level: Optional[Literal["read", "write"]]
    shared_at: str
