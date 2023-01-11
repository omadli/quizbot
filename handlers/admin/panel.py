from data.config import ADMINS
from loader import dp
from aiogram import types
from keyboards import admin_panel_keyb


@dp.message_handler(user_id=ADMINS, commands="panel")
async def cmd_panel(message: types.Message):
    await message.answer("Admin panelga xush kelibsiz", reply_markup=admin_panel_keyb)


