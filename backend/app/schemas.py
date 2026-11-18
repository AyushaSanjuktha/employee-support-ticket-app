from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator


def normalize_category(value: str) -> str:
    mapping = {
        "hardware": "Hardware",
        "software": "Software",
        "network": "Network",
        "access": "Access",
        "other": "Other",
    }
    key = value.strip().lower()
    if key not in mapping:
        raise ValueError("Category must be one of Hardware, Software, Network, Access, Other.")
    return mapping[key]


def normalize_priority(value: str) -> str:
    mapping = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
    }
    key = value.strip().lower()
    if key not in mapping:
        raise ValueError("Priority must be one of Low, Medium, High.")
    return mapping[key]


def normalize_status(value: str) -> str:
    mapping = {
        "open": "Open",
        "in progress": "In Progress",
        "in_progress": "In Progress",
        "resolved": "Resolved",
        "closed": "Closed",
    }
    key = value.strip().lower().replace("_", " ")
    if key not in mapping:
        raise ValueError("Status must be one of Open, In Progress, Resolved, Closed.")
    return mapping[key]


class UserBase(BaseModel):
    name: str
    email: str
    role: str  # "EMPLOYEE" or "SUPPORT"


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Comment content cannot be empty.")
        return trimmed


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    ticket_id: int
    author_id: int
    created_at: datetime
    author: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TicketBase(BaseModel):
    title: str
    description: str
    category: str = "Hardware"
    priority: str = "Medium"

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Title cannot be empty.")
        if len(trimmed) > 100:
            raise ValueError("Title must be at most 100 characters.")
        return trimmed

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Description cannot be empty.")
        return trimmed

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        return normalize_category(value)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        return normalize_priority(value)


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Title cannot be empty.")
        if len(trimmed) > 100:
            raise ValueError("Title must be at most 100 characters.")
        return trimmed

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Description cannot be empty.")
        return trimmed

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return normalize_category(value)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return normalize_priority(value)


class TicketStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        return normalize_status(value)


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    status: str
    priority: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
    owner: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(TicketResponse):
    comments: List[CommentResponse] = []

    model_config = ConfigDict(from_attributes=True)
