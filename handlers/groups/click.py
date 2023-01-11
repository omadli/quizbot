from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext


@dp.callback_query_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], state='*')
async def cancel_click(call: types.CallbackQuery, state=FSMContext):
    await call.answer(
        text="Qo'liz qichiyaptimi🤨 Bu tugma siz uchun emas! Faqat adminlar uchun",
        show_alert=True
    )
    
