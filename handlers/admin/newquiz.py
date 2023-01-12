import io, json
from loader import db, dp
from aiogram import types
from data.config import ADMINS
from states.newquiz import NewQuiz
from aiogram.dispatcher import FSMContext


@dp.message_handler(chat_id=ADMINS, commands='cancel', chat_type=types.ChatType.PRIVATE, state=NewQuiz.states)
async def cancel_handler(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Bekor qilindi!")


@dp.message_handler(chat_id=ADMINS, commands=['newquiz'], chat_type=types.ChatType.PRIVATE)
async def new_quiz_handler(msg: types.Message, state: FSMContext):
    await NewQuiz.name.set()
    await msg.answer(
        "Yaxshi endi yangi quiz uchun nom bering!"
    )


@dp.message_handler(chat_id=ADMINS, state=NewQuiz.name, chat_type=types.ChatType.PRIVATE)
async def new_quiz_name_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if len(msg.text) > 255:
            await msg.answer("Nomi uzunlik qilyapti! Boshqa nom bering")
            return
        data['name'] = msg.text
        await msg.answer(
            "Qabul qilindi. Bu quiz qaysi fandan?"
        )
        await NewQuiz.next()


@dp.message_handler(chat_id=ADMINS, state=NewQuiz.subject, chat_type=types.ChatType.PRIVATE)
async def new_quiz_subject_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if len(msg.text) > 255:
            await msg.answer("Uzunlik qilyapti! Boshqatdan kiriting")
            return
        data['subject'] = msg.text
        await msg.answer(
            "Qabul qilindi. Qo'shimcha izohlarni yoki quiz tavsifini yuboring"
        )
        await NewQuiz.next()



@dp.message_handler(chat_id=ADMINS, state=NewQuiz.comment, chat_type=types.ChatType.PRIVATE)
async def new_quiz_comment_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = msg.text
        await msg.answer(
            "Qabul qilindi. Endi savollarni json fayl ko'rinishida yuboring!"
        )
        await NewQuiz.next()


@dp.message_handler(chat_id=ADMINS, state=NewQuiz.file, chat_type=types.ChatType.PRIVATE, content_types=types.ContentTypes.DOCUMENT)
async def new_quiz_file_handler(msg: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            f: io.BytesIO = io.BytesIO()
            await msg.document.download(destination_file=f)
            q = json.loads(f.read())
            f.close()
            q_id, k = await db.create_quiz_with_questions(
                name=data['name'],
                subject=data['subject'],
                q=q,
                comment=data['comment']
            )
            await msg.answer(
                text=f"Test tuzildi. Test raqami #n{q_id}\nJami {k} ta savol qo'shildi!"
            )
            await msg.answer(
                text=f"<b>{data['name']}</b>\n"
                    f"<b>{data['subject']}</b> fanidan\n"
                    f"<i>{data['comment']}</i>",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="▶️Guruhda testni boshlash", url=f"https://t.me/tatu_quiz_bot?startgroup={q_id}")]
                    ]
                )
            )
            await state.finish()
    except Exception as e:
        print("Xatolik!", e)
        await msg.answer(f"Xatolik {e}")
        await msg.answer("Boshqatdan urining yoki bekor qilish uchun /cancel bosing")
            


