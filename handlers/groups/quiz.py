import random
import time
import asyncio
from loader import dp, db
from aiogram import types
from aiogram.dispatcher.filters import AdminFilter, Regexp, IDFilter
from aiogram.dispatcher import FSMContext
from typing import List, Dict
from data.config import GROUPS



@dp.message_handler(AdminFilter(), chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], regexp=r'\/stop(@tatu_quiz_bot)?', state='*')
async def stop_quiz(msg: types.Message):
    state: str = await dp.storage.get_state(chat=msg.chat.id)
    if state is not None and str(state).startswith('quiz'):
        if state == 'quiz':
            await finish_quiz(msg.chat.id)
        else:
            data = await dp.storage.get_data(chat=msg.chat.id)
            if data.get('msg', None) is not None:
                try:
                    await dp.bot.delete_message(
                        chat_id=msg.chat.id,
                        message_id=data['msg']
                    )
                except Exception as e:
                    print(e)
            await dp.storage.finish(chat=msg.chat.id)
            await msg.answer(
                "To'xtatildi!"
            )
        

@dp.message_handler(AdminFilter(), chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], regexp=r'\/start(@tatu_quiz_bot)? [0-9]+', state='*')
async def start_quiz(msg: types.Message):
    if msg.chat.id not in GROUPS:
        return await msg.answer("Bu bot faqat @tatu_tuit_hub guruhi uchun. Test ishlamoqchi bo'lsangiz shu guruhga qo'shiling!")
    
    state: str = await dp.storage.get_state(chat=msg.chat.id)
    if state is not None and str(state).startswith('quiz'):
        await msg.delete()
        return await dp.bot.send_message(
            chat_id=msg.from_user.id,
            text=f"{msg.chat.full_name} guruhida quiz ketyapti halal bermang🤫"
        )
    q_id = msg.get_args()
    if not q_id.isdigit():
        return await msg.answer("Quiz raqami xato!")
    q_id = int(q_id)
    quiz = await db.get_quiz(q_id)
    if quiz is None:
        return await msg.answer("Quiz topilmadi!")
    l = await db.get_questions_count_from_quiz(q_id)
    if not l:
        return await msg.answer("Ushbu quizda savollar yo'qku")
    data = dict()
    data['quiz_id'] = q_id
    data['quiz'] = dict(quiz)
    data['quiz_count'] = l
    m = await msg.answer(
        f"{quiz['subject']} fanidan {quiz['name']} testiga tayyorlaning!\n"
        f"Jami savollar soni {l} ta, nechtasini yechamiz?",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text='Barchasiga', callback_data='count:all')],
                [types.InlineKeyboardButton(text='10', callback_data='count:10'), types.InlineKeyboardButton(text='20', callback_data='count:20'), types.InlineKeyboardButton(text='25', callback_data='count:25')],
                [types.InlineKeyboardButton(text='30', callback_data='count:30'), types.InlineKeyboardButton(text='40', callback_data='count:40'), types.InlineKeyboardButton(text='50', callback_data='count:50')],
            ]
        )
    )
    data['msg'] = m.message_id
    await dp.storage.set_data(chat=msg.chat.id, data=data)
    await dp.storage.set_state(chat=msg.chat.id, state="quiz_count")
    

@dp.callback_query_handler(AdminFilter(), Regexp(r"count:((all)|([0-9]+))"), chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], state='*')
async def get_quiz_count(call: types.CallbackQuery):
    state = await dp.storage.get_state(chat=call.message.chat.id)
    if state != "quiz_count":
        await call.message.delete()
        return
    data = await dp.storage.get_data(chat=call.message.chat.id, )
    t = call.data.replace("count:", '')
    qc = data['quiz_count']
    if t.isdigit():
        c = int(t)
    elif t == 'all':
        c = qc
    else:
        return await call.answer("Nomalum xatolik!", show_alert=True)
    if c > qc:
        return await call.answer(
            text=f"Bu quizda buncha savol mavjud emasku!\n"
                f"{qc} yoki undan kichik sonni tanlang",
            show_alert=True
        )
    data['count'] = c
    questions = await db.get_questions_from_quiz(quiz_id=data['quiz_id'])
    questions: List[Dict] = [dict(row) for row in questions]
    random_questions = random.sample(questions, c)
    random.shuffle(random_questions)
    data['questions'] = random_questions
    await dp.storage.update_data(chat=call.message.chat.id, data=data)
    await call.answer(
        text=f"{c} ta quiz o'ynaladi!",
        show_alert=True
    )
    quiz = data['quiz']
    await call.message.edit_text(
        text=f"{quiz['subject']} fanidan {quiz['name']} testiga tayyorlaning!\n"
            f"{c} ta test!\nSavollar orasidagi vaqt qancha bo'lsin?",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text='10 soniya', callback_data='time:10'), types.InlineKeyboardButton(text='20 soniya', callback_data='time:20'), types.InlineKeyboardButton(text='30 soniya', callback_data='time:30')],
                [types.InlineKeyboardButton(text='45 soniya', callback_data='time:45'), types.InlineKeyboardButton(text='60 soniya', callback_data='time:60'), types.InlineKeyboardButton(text='100 soniya', callback_data='time:100')],
            ]
        )
    )
    await dp.storage.set_state(chat=call.message.chat.id, state='quiz_time')
 
   
   
@dp.callback_query_handler(AdminFilter(), Regexp(r"time:([0-9]+)"), chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], state='*')
async def get_quiz_time(call: types.CallbackQuery):
    state = await dp.storage.get_state(chat=call.message.chat.id)
    if state != "quiz_time":
        await call.message.delete()
        return
    t = call.data.replace("time:", '')
    if t.isdigit():
        c = int(t)
    else:
        return await call.answer("Nomalum xatolik!", show_alert=True)
    await dp.storage.update_data(chat=call.message.chat.id, data={'quiz_time': c})
    await call.answer(
        text=f"{c} soniya vaqt belgilandi",
        show_alert=True
    )
    for i in ["3️⃣", "2️⃣", "1️⃣", "Go🚀"]:
        await call.message.edit_text(
            text=i,
            reply_markup=None
        )
        await asyncio.sleep(1)
    await dp.storage.set_state(chat=call.message.chat.id, state='quiz')
    await call.message.delete()
    await dp.storage.update_data(chat=call.message.chat.id, data={'msg': None})
    await send_next_quiz(call.message.chat.id)
    

async def send_quiz(question: dict, group, INTERVAL, index, count) -> int:
    if question.get('is_long', True):
        options = "\n".join(
            [f"{i}) {opt}" for opt, i in zip(question['options'], list("ABCD"))]
        )
        m:types.Message = await dp.bot.send_message(
            chat_id=group,
            text=f"<b>{question['question']}</b>\n"
                f"{options}\n\n"
                f"<i>{question['explanation']}</i>"
        )
        p: types.Message = await m.reply_poll(
            question=f"[{index}/{count}] Javob:",
            options=list("ABCD"),
            type=types.PollType.QUIZ,
            correct_option_id=question['correct_index'],
            is_anonymous=False,
            allows_multiple_answers=False,
            open_period=INTERVAL,
            explanation=question['explanation'],
            explanation_parse_mode=types.ParseMode.HTML
        )
    else:
        p: types.Message = await dp.bot.send_poll(
            chat_id=group,
            question=f"[{index}/{count}] {question['question']}",
            options=question['options'],
            type=types.PollType.QUIZ,
            correct_option_id=question['correct_index'],
            is_anonymous=False,
            allows_multiple_answers=False,
            open_period=INTERVAL,
            explanation=question['explanation'],
            explanation_parse_mode=types.ParseMode.HTML
        )
    t = time.time()
    await dp.storage.update_data(chat=p.poll.id, data={'correct_index': question['correct_index'], 'time': t, 'group': group})
    return p.poll.id


async def finish_quiz(group):
    def user_url(user_id: int, u: dict):
        if u['username'] is not None:
            return f"@{u['username']}"
        return f"<a href='tg://user?id={user_id}'>{u['full_name']}</a>"
    
    def to_time(seconds: float):
        minutes = seconds // 60
        seconds = seconds - (minutes)*60
        res = ""
        if minutes:
            res = f"{minutes} daqiqa "
        seconds = round(seconds, 2)
        if seconds.is_integer():
            seconds = int(seconds)
        res += f"{seconds} soniya"
        return res
    
    
    users: dict = await dp.storage.get_data(chat=group, user='users')
    if not users or not len(users):
        await dp.bot.send_message(
            chat_id=group,
            text=f"🏁 <b>“{quiz_name}”</b> testi yakunlandi!\n\n"
                f"<i>{c} ta savolga javob berildi</i>\n\n"
                f"<b>Testda hech kim ishtirok etmadi!</b>"
            )
    else:
        times = [[key, value['correct'], value['time']] for key, value in users.items()]
        times = sorted(sorted(times, key=lambda x: x[2]), key=lambda x: x[1], reverse=True)
        txt = ""
        for user, i in zip(times[:3], ["🥇", "🥈", "🥉"]):
            txt += f"{i} " + user_url(user[0], users.get(f"{user[0]}")) + " - " + f"<b>{user[1]}</b> (" + to_time(user[2]) + ")\n"
        data = await dp.storage.get_data(chat=group)
        c = data['i']
        quiz_name = data['quiz']['name']
        await dp.bot.send_message(
            chat_id=group,
            text=f"🏁 <b>“{quiz_name}”</b> testi yakunlandi!\n\n"
                f"<i>{c} ta savolga javob berildi</i>\n\n"
                f"{txt}\n"
                f"🏆 Gʻoliblarni tabriklaymiz!"
                
        )
    await dp.storage.finish(chat=group)
    await dp.storage.finish(chat=group, user='users')


def make_question(question: dict):
    q = dict()
    q['question'] = question['question']
    opts = [question['a'], question['b'], question['c'], question['d']]
    correct_i = question['correct_index']
    correct = opts[correct_i]
    random.shuffle(opts)
    index = opts.index(correct)
    q['options'] = opts
    q['correct_index'] = index
    q['is_long'] = question['is_long']
    q['explanation'] = "@tuit_quizlar & @tuit_team"
    if question.get('level', False):
        q['explanation'] = f"Qiyinlik darajasi: {question['level']}\n{q['explanation']}"
    return q


async def send_next_quiz(group):
    data = await dp.storage.get_data(chat=group)
    if data is None or not data:
        return
    count = data['count']
    interval = data['quiz_time']
    i = data.get('i', 0)
    i += 1
    if i > count:
        # tugatish
        await finish_quiz(group)
        return
    else:
        question = data['questions'][i-1]
        question = make_question(question)
        data['i'] = i
        data['correct_index'] = question['correct_index']
        await dp.storage.update_data(chat=group, data=data)
        poll_id = await send_quiz(question, group, interval, i, count)
        await asyncio.sleep(interval)
        await dp.storage.finish(chat=poll_id)
        return await send_next_quiz(group)
        

@dp.poll_answer_handler()
async def answer_handler(pa: types.PollAnswer):
    t = time.time()
    poll_id = pa.poll_id
    data = await dp.storage.get_data(chat=poll_id)
    if data is not None:
        delta = t - data['time']
        data2 = await dp.storage.get_data(chat=data['group'], user='users')
        data3 = data2.get(f"{pa.user.id}", {
            "username": pa.user.username,
            "full_name": pa.user.full_name,
            "time": 0,
            "correct": 0
        })
        data3['time'] += delta
        correct_index = data['correct_index']
        if correct_index == pa.option_ids[0]:
            data3['correct'] += 1
        await dp.storage.update_data(chat=data['group'], user='users', data={f"{pa.user.id}": data3})
        
