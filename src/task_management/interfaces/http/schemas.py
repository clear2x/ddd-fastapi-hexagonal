from __future__ import annotations

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator


class CreateTaskRequest(BaseModel):
    """创建任务请求模型。description 会执行空值归一化。"""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("标题不能为空")
        return normalized

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        """把未传、null 和全空白字符串统一归一化为 None。"""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class AssignTaskRequest(BaseModel):
    assignee_id: str = Field(min_length=1, max_length=128)

    @field_validator("assignee_id")
    @classmethod
    def validate_assignee_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("指派人不能为空")
        return normalized


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    assignee_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class HealthResponse(BaseModel):
    status: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[dict[str, object]] = Field(default_factory=list)


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    data: T


class ErrorResponse(BaseModel):
    error: ErrorBody
