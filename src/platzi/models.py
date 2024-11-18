from enum import Enum

from humps import camelize
from pydantic import BaseModel
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
    subtitles_url: str | None = None


class Resource(BaseModel):
    name: str
    url: str


class Unit(BaseModel):
    id: int | None = None
    type: TypeUnit
    title: str
    url: str
    slug: str
    video: Video | None = None
    resources: list[Resource] | None = None


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
