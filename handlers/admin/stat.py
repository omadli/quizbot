from data.config import ADMINS
from loader import db, dp
from aiogram import types


@dp.message_handler(user_id=ADMINS, commands="stat")
@dp.message_handler(user_id=ADMINS, text="📈Statistika📉")
async def cmd_stat(message: types.Message):
    jami = await db.count_users()
    quizs = await db.count_quiz()
    await message.answer(
        f"📈Statistika📉\n"
        f"👥Jami foydalanuvchilar:  {jami} ta\n"
        f"📝Jami quizlar:  {quizs} ta\n"
    )


