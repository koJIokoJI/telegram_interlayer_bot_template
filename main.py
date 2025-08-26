import asyncio
import logging
import os
import sys

from config.config import settings
from app.bot import bot


logging.basicConfig(level=settings.logs.level, format=settings.logs.format)

if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

asyncio.run(bot())
