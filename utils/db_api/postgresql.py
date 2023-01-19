from typing import Union, Optional
from datetime import date, datetime, time  
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config

class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
       CREATE TABLE IF NOT EXISTS Users (
            id SERIAL PRIMARY KEY,
            full_name varchar(255) NOT NULL,
            username varchar(255),
            user_id BIGINT NOT NULL UNIQUE,
            join_date DATE
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    @staticmethod
    def today() -> date:
        now = datetime.now()
        return date(
            year=now.year,
            month=now.month,
            day=now.day
        )
        
    
    async def add_user(self, full_name, username, user_id, join_date=None):
        if join_date is None:
            join_date = self.today()
        
        sql = "INSERT INTO users (full_name, username, user_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, user_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user(self, full_name, username, user_id):
        sql = "UPDATE Users SET full_name=$1, username=$2 WHERE user_id=$3"
        return await self.execute(sql, full_name, username, user_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
        
    async def create_table_quizs(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Quizs (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL, 
            comment VARCHAR(255),
            subject VARCHAR(255) NOT NULL
        );
        """
        return await self.execute(sql, execute=True)
    
    
    async def create_table_questions(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Questions (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL, 
            a TEXT NOT NULL,
            b TEXT NOT NULL,
            c TEXT NOT NULL,
            d TEXT NOT NULL,
            correct_index INT NOT NULL,
            is_long BOOLEAN DEFAULT false,
            level INT,
            quiz INT NOT NULL,
            FOREIGN KEY(quiz) REFERENCES Quizs(id)
        );
        """
        return await self.execute(sql, execute=True)
    
    
    async def add_quiz(self, name: str, subject: str, comment:str = None):
        sql = """
        INSERT INTO Quizs("name", "comment", "subject") VALUES ($1, $2, $3) RETURNING *;
        """
        return await self.execute(sql, name, comment, subject, execute=True)


    async def add_question(self, quiz: int, question: str, a: str, b: str, c: str, d: str, correct_index: int, is_long: bool, level: Optional[int] = None):
        sql = """
        INSERT INTO Questions("question", "a", "b", "c", "d", "correct_index", "is_long", "level", "quiz") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)  RETURNING *;
        """
        return await self.execute(sql, question, a, b, c, d, correct_index, is_long, level, quiz, execute=True)

    def check_question_dict(self, q):
        if q.get('questions', None) is not None:
            questions = q['questions']
            if isinstance(questions, list) and len(questions):
                b1 = 1
                for q1 in questions:
                    b1 = b1 and (q1.get('question', None) is not None)
                    b1 = b1 and (q1.get('correct_index', None) is not None)
                    b1 = b1 and (q1.get('answers', None) is not None)
                    b1 = b1 and (q1.get('type', None) is not None)
                return bool(b1)
        return False
        

    async def create_quiz_with_questions(self, name: str, subject: str, q:dict, comment:str= None):
        if not self.check_question_dict(q):
            raise Exception("Yaroqsiz format!")
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                sql = """
                INSERT INTO Quizs("name", "comment", "subject") VALUES ($1, $2, $3) RETURNING *;
                """
                quiz = await connection.fetchrow(sql, name, comment, subject)
                sql = """
                INSERT INTO Questions("question", "a", "b", "c", "d", "correct_index", "is_long", "level", "quiz") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)  RETURNING *;
                """
                q_id = quiz['id']
                k = 0
                for question in q['questions']:
                    level = int(question['level']) if question.get('level', None) is not None else None
                    await connection.execute(
                        sql,
                        question['question'],
                        question['answers'][0],
                        question['answers'][1],
                        question['answers'][2],
                        question['answers'][3],
                        question['correct_index'],
                        question['type'] == 'long',
                        level,
                        q_id,
                    )
                    k += 1
                return q_id, k
    

    async def get_quiz(self, pk:int):
        sql = """
        SELECT * FROM Quizs WHERE id=$1;
        """
        return await self.execute(sql, pk, fetchrow=True)
    
    
    async def all_quizs(self):
        sql = """
        SELECT * FROM Quizs;
        """
        return await self.execute(sql, fetch=True)
    
    
    async def count_quiz(self):
        sql = """
        SELECT COUNT(*) FROM Quizs;
        """
        return await self.execute(sql, fetchval=True)
    
    
    async def get_questions_from_quiz(self, quiz_id:int):
        sql = """
        SELECT * FROM Questions WHERE quiz=$1;
        """
        return await self.execute(sql, quiz_id, fetch=True)
    
    
    async def get_questions_count_from_quiz(self, quiz_id:int):
        sql = """
        SELECT COUNT(*) FROM Questions WHERE quiz=$1;
        """
        return await self.execute(sql, quiz_id, fetchval=True)
    
    
    async def select_all_users_id(self):
        sql = '''SELECT user_id FROM Users;'''
        return await self.execute(sql, fetch=True)
    