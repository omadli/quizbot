from aiogram import types
from loader import dp, db
from data.config import ADMINS


def chunks(_l, n):
    n = max(1, n)
    return (_l[i:i+n] for i in range(0, len(_l), n))


@dp.message_handler(chat_id=ADMINS, commands=['users'])
@dp.message_handler(chat_id=ADMINS, text="👥Barcha foydalanuvchilar")
async def cmd_users(message: types.Message):
    await message.answer("Barcha foydalanuvchilar")
    users = await db.select_all_users()
    chunk = 50
    for users1 in chunks(users, chunk):
        txt = "\n".join(
            map(lambda x: f"{x[0]}) <a href='tg://user?id={x[3]}'>{x[1]}</a> {'@' + x[2] if x[2] else None} -"
                          f" {x[4] if x[4] else 'NONE'}", users1))
        await message.answer(txt)

