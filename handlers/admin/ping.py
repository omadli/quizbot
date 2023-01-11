from aiogram import types
from loader import dp
from data.config import ADMINS
import time


@dp.message_handler(chat_id=ADMINS, commands=['ping'])
@dp.message_handler(chat_id=ADMINS, text="🚀Tezlik")
async def ping_test(message: types.Message):
	t1 = time.time()
	m = await message.reply("Pong")
	t2 = time.time()
	ping = int((t2 - t1) * 1000)
	await m.edit_text(f"Ping: {ping}ms")
