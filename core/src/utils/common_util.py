import string
import sys
import traceback
import uuid
from datetime import datetime, time, timezone
from functools import wraps
from typing import Any, Callable, List, Literal, Optional

from deep_translator import GoogleTranslator
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import update
from src.common.common_exc import IntervalServerErrorHttpException
from src.utils.db_util import get_session
from src.utils.log_util import logger, traceback_logger


async def get_current_time(
    tz: timezone = timezone.utc,
    with_ms_flag: bool = False,
) -> datetime:
    with_ms = datetime.now(tz=tz)

    with_no_ms = datetime(
        with_ms.year,
        with_ms.month,
        with_ms.day,
        with_ms.hour,
        with_ms.minute,
        with_ms.second,
        tzinfo=tz,
    )

    # with_ms = with_ms.replace(tzinfo=None)

    return with_ms if with_ms_flag else with_no_ms


async def correct_time_to_utc(
    time: time,
):
    if time.tzinfo is None:
        return ValueError("Time must be timezone-aware")

    dt = datetime.combine(datetime(1970, 1, 1).date(), time)
    utc_dt = dt.astimezone(timezone.utc)

    return utc_dt.timetz()


async def remove_tz_and_ms_from_time(
    time: time,
):
    if time.tzinfo is None:
        return time

    return time.replace(tzinfo=None, microsecond=0)


async def list_to_str(
    lst: List[str],
    separator: str = ", ",
) -> str:
    if lst == []:
        return ""

    return " ".join([str(x) for x in lst]).replace(" ", separator)


async def str_to_list(
    string: str,
    sep: str = ",",
    to_type_func: Callable = str,
) -> List[str]:
    if string in ["", None]:
        return []

    return [
        to_type_func(x.strip()) for x in string.split(sep) if x.strip() != ""
    ]

async def merge_lists(
    lists: List[List[Any]],
) -> List[Any]:
    merged = []
    for lst in lists:
        merged.extend(lst)
    return merged


async def uuid_gen() -> str:
    return str(uuid.uuid4())


async def log(
    text: str,
    mode: Literal["info", "error"] = "info",
    user_id: int | None = -1,
):
    if not isinstance(text, str):
        text = str(text)

    if mode == "info":
        logger.info(
            f"{await get_current_time()} - user_id: {user_id} - " + text
        )

    if mode == "error":
        logger.error(
            f"{await get_current_time()} - user_id: {user_id} - " + text
        )


def timeit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = datetime.now()
        result = await func(*args, **kwargs)
        duration = datetime.now() - start
        logger.info(
            f"{await get_current_time()} - {func.__qualname__} took: {duration}"  # noqa
        )
        return result

    return wrapper


def try_rollback(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user_in_kwargs = kwargs.get("_", None)

        '''user: Optional[UserSchema] = (
            user_in_kwargs
            if user_in_kwargs and isinstance(user_in_kwargs, UserSchema)
            else None
        )'''

        try:
            return await func(*args, **kwargs)
        except Exception as e:
            user_id = -1 #user.id if user else -1
            log_text = f"{func.__qualname__} - {type(e).__name__} - {e}"

            if not isinstance(e, HTTPException):
                tb_text = "".join(
                    traceback.format_list(
                        traceback.extract_tb(
                            sys.exc_info()[2],
                        ),
                    )
                )
                traceback_logger.error(
                    f"{await get_current_time()} - user_id: {user_id} - "
                    + f"{log_text}\n{tb_text}"
                )

            await log(
                user_id=user_id,
                text=log_text,
                mode="error",
            )

            if isinstance(e, HTTPException):
                raise e

            raise IntervalServerErrorHttpException(msg=str(e))

    return wrapper
