from aiogram.dispatcher.filters.state import State, StatesGroup

class NewQuiz(StatesGroup):
    name = State()
    subject = State()
    comment = State()
    file = State()
