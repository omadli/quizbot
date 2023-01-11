from loader import dp
from aiogram import types


@dp.message_handler(commands=['newquiz'])
async def new_quiz_handler(msg: types.Message):
    await msg.reply(
        "Yangi quiz tuzish faqat adminlar uchun!"
    )
