from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands='cancel', state='*')
async def cancel_handler(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.reply("Oxirgi amal bekor qilindi!")
