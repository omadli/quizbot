import asyncio

from aiogram import types
from loader import dp, db
from data.config import ADMINS
from keyboards import admin_forward_keyb, admin_panel_keyb
from utils.broadcast import broadcaster
from aiogram.dispatcher import FSMContext


@dp.message_handler(chat_id=ADMINS, is_forwarded=True, content_types=types.ContentTypes.ANY)
async def admin_forwarded_message(message: types.Message):
    await message.reply(text="Ushbu xabarni barcha foydalanuvchilarga qay tarzda yuborib chiqaymi?",
                       reply_markup=admin_forward_keyb)


@dp.callback_query_handler(chat_id=ADMINS, text_startswith="broadcast_")
async def call_broadcast(call: types.CallbackQuery):
    metod = call.data[10:]
    admin = call.from_user.id
    kwargs = {
        'from_chat_id': call.message.reply_to_message.chat.id,
        'message_id': call.message.reply_to_message.message_id
    }
    await call.message.edit_text("Bajaryapman")
    asyncio.create_task(broadcaster(dp, admin, await db.select_all_users_id(), metod, **kwargs))


@dp.message_handler(chat_id=ADMINS, text="🖇Reklama yuborish")
async def rassilka(message: types.Message, state: FSMContext):
    await state.set_state("rassilka")
    await message.answer("Yubormoqchi bo'lgan xabaringizni yuboring.\nBekor qilmoqchi bo'lsangiz /cancel")


@dp.message_handler(chat_id=ADMINS, commands='cancel', state='rassilka')
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Rassilka bekor qilindi", reply_markup=admin_panel_keyb)


@dp.message_handler(chat_id=ADMINS, state="rassilka", content_types="any")
async def rassilka_msg(message: types.Message, state: FSMContext):
    await message.reply(text="Ushbu xabarni barcha foydalanuvchilarga qay tarzda yuborib chiqay?",
                        reply_markup=admin_forward_keyb)
    await state.finish()
