from functools import lru_cache

from prisma import Prisma


@lru_cache
def get_prisma() -> Prisma:
    return Prisma()


async def get_prisma_async() -> Prisma:
    prisma = Prisma()
    await prisma.connect()
    try:
        yield prisma
    finally:
        await prisma.disconnect() 