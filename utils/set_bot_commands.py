from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish/Quiz boshlash"),
            types.BotCommand("stop", "Mavjud quizni to'xtatish"),
            types.BotCommand("help", "Yordam"),
            types.BotCommand("newquiz", "Yangi quiz tuzish"),
        ]
    )
