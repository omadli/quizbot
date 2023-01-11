from loader import db, dp
from aiogram import types
from data.config import ADMINS


@dp.message_handler(chat_id=ADMINS, commands=['quizzes'], chat_type=types.ChatType.PRIVATE)
async def new_quiz_handler(msg: types.Message):
    quizs = await db.all_quizs()
    if not quizs or not len(quizs):
        return await msg.answer("Hech nima topilmadi!")
        
    for quiz in quizs:
        await msg.answer(
            text=f"<b>{quiz['name']}</b>\n"
                f"<b>{quiz['subject']}</b> fanidan\n"
                f"<i>{quiz['comment']}</i>",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="▶️Guruhda testni boshlash", url=f"https://t.me/tatu_quiz_bot?startgroup={quiz['id']}")]
                ]
            )
        )
        
    
    
    