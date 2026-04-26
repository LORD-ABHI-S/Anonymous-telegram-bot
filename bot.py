import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import aiosqlite

BOT_TOKEN = os.getenv("8615757921:AAEixPSxCYRkXv_S2A37d1D_l3jUbB1gXM0")
ADMIN_ID = int(os.getenv("7499742938"))
CHANNELS = ["@AS_WORKSPACE", "@AS_COMMUNITI"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

waiting_queue = []

# ---------------- MENU ---------------- #

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("/find"), KeyboardButton("/next")],
            [KeyboardButton("/stop")]
        ],
        resize_keyboard=True
    )

# ---------------- DATABASE ---------------- #

async def init_db():
    async with aiosqlite.connect("db.sqlite") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            partner INTEGER,
            status TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)
        await db.commit()

async def create_user(user_id):
    async with aiosqlite.connect("db.sqlite") as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, status) VALUES (?, 'idle')", (user_id,))
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect("db.sqlite") as db:
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update(user_id, field, value):
    async with aiosqlite.connect("db.sqlite") as db:
        await db.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect("db.sqlite") as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            return await cursor.fetchall()

async def set_setting(key, value):
    async with aiosqlite.connect("db.sqlite") as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()

async def get_setting(key):
    async with aiosqlite.connect("db.sqlite") as db:
        async with db.execute("SELECT value FROM settings WHERE key=?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

# ---------------- FORCE SUB ---------------- #

async def is_subscribed(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def join_buttons():
    kb = InlineKeyboardMarkup()
    for ch in CHANNELS:
        kb.add(InlineKeyboardButton("Join Channel", url=f"https://t.me/{ch[1:]}"))
    kb.add(InlineKeyboardButton("✅ I Joined", callback_data="check_sub"))
    return kb

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_sub(call: types.CallbackQuery):
    if await is_subscribed(call.from_user.id):
        await call.message.delete()
        await start(call.message)
    else:
        await call.answer("❌ Join all channels first", show_alert=True)

# ---------------- MATCHING ---------------- #

async def match_user(user_id):
    if user_id in waiting_queue:
        return

    for other in waiting_queue:
        if other != user_id:
            waiting_queue.remove(other)

            await update(user_id, "partner", other)
            await update(other, "partner", user_id)
            await update(user_id, "status", "chat")
