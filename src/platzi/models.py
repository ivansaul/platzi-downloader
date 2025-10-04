from enum import Enum

from humps import camelize
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class User(BaseModel):
    model_config = ConfigDict(alias_generator=camelize)

    avatar: str
    name: str
    username: str
    email: str
    user_id: int
    plan: str
    is_authenticated: bool
    user_type: str
    phone_number: str


class TypeUnit(str, Enum):
    LECTURE = "lecture"
    VIDEO = "video"
    QUIZ = "quiz"


class Video(BaseModel):
    id: int | None = None
    url: str
    subtitles_url: list[str] | None = None


class Resource(BaseModel):
    files_url: list[str] = Field(default_factory=list)
    readings_url: list[str] = Field(default_factory=list)
    summary: str | None = None


class Unit(BaseModel):
    id: int | None = None
    type: TypeUnit
    title: str
    url: str
    slug: str
    video: Video | None = None
    resources: Resource | None = None


class Chapter(BaseModel):
    id: int | None = None
    name: str
    slug: str
    description: str | None = None
    units: list[Unit]


class Course(BaseModel):
    id: int | None = None
    name: str
    slug: str
    url: str
    description: str | None = None
    chapters: list[Chapter]
