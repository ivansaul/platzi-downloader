import asyncio
import hashlib
import inspect
import pickle
import shutil
from functools import wraps
from pathlib import Path

import aiofiles

from .constants import CACHE_DIR


class Cache:
    @staticmethod
    def _cache_dir() -> Path:
        return CACHE_DIR

    @classmethod
    def _path(cls, id: str) -> Path:
        return cls._cache_dir() / f"{id}.pkl"

    @classmethod
    def _make_id(cls, func, args, kwargs) -> str:
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        key_data = (func.__module__, func.__qualname__, bound.arguments)
        key_bytes = repr(key_data).encode("utf-8")
        return hashlib.sha256(key_bytes).hexdigest()

    @classmethod
    async def get(cls, id: str) -> object | None:
        path = cls._path(id)
        try:
            async with aiofiles.open(path, "rb") as file:
                data = await file.read()
                return await asyncio.to_thread(pickle.loads, data)
        except Exception:
            return None

    @classmethod
    async def set(cls, id: str, content: object) -> None:
        path = cls._path(id)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = await asyncio.to_thread(pickle.dumps, content)
            async with aiofiles.open(path, "wb") as file:
                await file.write(data)
        except Exception:
            pass

    @classmethod
    def clear(cls):
        if cls._cache_dir().exists():
            shutil.rmtree(cls._cache_dir())

    @classmethod
    def cache_async(cls, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_id = cls._make_id(func, args, kwargs)
            if cached := await cls.get(cache_id):
                return cached
            result = await func(*args, **kwargs)
            await cls.set(cache_id, result)
            return result

        return wrapper
