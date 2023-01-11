import os
import asyncio
from loguru import logger
from typing import List, Union, Dict
from aiogram import types, Dispatcher
from aiogram.utils import exceptions


logger.remove(0)

logger.add(
    "logs.log",  
    format = "<red>[{level}]</red> Message : <green>{message}</green> @ {time}", 
    colorize=False
    )



async def send(method, user, **kwargs):
    user_id = user['user_id']
    try:
        await method(user_id, **kwargs)
    except exceptions.BotBlocked:
        logger.error(f"Target [ID:{user_id}]: Bot blocked by user")
    except exceptions.ChatNotFound:
        logger.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logger.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send(method, user, **kwargs)
    except exceptions.UserDeactivated:
        logger.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: failed")
    else:
        logger.success(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcaster(dp: Dispatcher, admin: int, users: List[Dict], metod: Union[callable, str], **kwargs):
    if isinstance(metod, str):
        metod = getattr(dp.bot, metod)
    m: types.Message = await dp.bot.send_message(chat_id=admin, text="Rassilka boshlandi.")
    count = 0
    try:
        for user in users:
            if await send(metod, user, **kwargs):
                count += 1
            await asyncio.sleep(.05)
    finally:
        logger.info(f"{count} messages successful sent.")
    await m.edit_text(f"{count} ta foydaluvchiga muvaffaqqiyatli yuborildi")
    logger.complete()
    logger.stop()
    with open("./logs.log", "rb") as f:
        await dp.bot.send_document(chat_id=admin, document=f, caption="Loglar")
    os.remove("logs.log")
    return count
