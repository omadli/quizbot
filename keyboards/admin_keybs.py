from aiogram import types

admin_forward_keyb = types.InlineKeyboardMarkup(row_width=1)
admin_forward_keyb.add(types.InlineKeyboardButton(text="©️Copy", callback_data="broadcast_copy_message"))
admin_forward_keyb.add(types.InlineKeyboardButton(text="⏩Forward", callback_data="broadcast_forward_message"))
admin_forward_keyb.add(types.InlineKeyboardButton(text="❌Bekor qilish", callback_data="home"))


admin_panel_keyb = types.ReplyKeyboardMarkup(
    keyboard=[
        # [types.KeyboardButton(text="👤Qidirish")],
        # [types.KeyboardButton(text="👥Barcha foydalanuvchilar")],
        [types.KeyboardButton(text="🖇Reklama yuborish")],
        [types.KeyboardButton(text="📈Statistika📉")],
        [types.KeyboardButton(text="🚀Tezlik")],
        [types.KeyboardButton(text="🔙Orqaga")],
    ],
    resize_keyboard=True
)
