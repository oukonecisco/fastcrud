import typing
import asyncio


async def run_async_or_sync(func: typing.Callable, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return func(*args, **kwargs)
