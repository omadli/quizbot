from typing import Dict, Any
from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loader import db
    
class DatabaseMiddleware(BaseMiddleware):    
    async def on_process_message(self, message: types.Message, data: Dict, *args: Any) -> None:
        user = types.User.get_current()
        user_db = await db.select_user(user_id=user.id)
        if user_db is None:
            user_db = await db.add_user(
                full_name=user.full_name,
                user_id=user.id,
                username=user.username
            )
            
        if user_db['full_name'] != user.full_name or user_db['username'] != user.username:
            user_db = await db.update_user(
                full_name=user.full_name,
                user_id=user.id,
                username=user.username
            )
            
        data["db_user"] = user_db
    
    
    async def on_process_callback_query(self, call: types.CallbackQuery, data: Dict, *args: Any) -> None:
        user = types.User.get_current()
        user_db = await db.select_user(user_id=user.id)
        if user_db is None:
            user_db = await db.add_user(
                full_name=user.full_name,
                user_id=user.id,
                username=user.username
            )
            
        if user_db['full_name'] != user.full_name or user_db['username'] != user.username:
            user_db = await db.update_user(
                full_name=user.full_name,
                user_id=user.id,
                username=user.username
            )
            
        data["db_user"] = user_db
        
    async def on_process_poll_answer(self, poll_answer: types.PollAnswer, data: Dict, *args: Any) -> None:
        if poll_answer.user is not None:
            user = poll_answer.user
            user_db = await db.select_user(user_id=user.id)
            if user_db is None:
                user_db = await db.add_user(
                    full_name=user.full_name,
                    user_id=user.id,
                    username=user.username
                )
                
            if user_db['full_name'] != user.full_name or user_db['username'] != user.username:
                user_db = await db.update_user(
                    full_name=user.full_name,
                    user_id=user.id,
                    username=user.username
                )
            
            data["db_user"] = user_db
            