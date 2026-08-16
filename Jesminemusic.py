# ============================================================
# JASMINE X MUSIC
# Corrected clean version
# ============================================================

import asyncio
import os
import sqlite3
import sys
import time

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL


# ============================================================
# CONFIG
# ============================================================

API_ID = 30672609

# IMPORTANT:
# The credentials you previously posted were exposed.
# Put your NEW credentials here.
API_HASH = "7b1d2b631725691a89df22a377f3c53a"
BOT_TOKEN = "8835783533:AAGnnXZXxACuN9s6Pgj-Ku16drdoPOI3mm4"
SESSION_STRING = "1BVtsOJ8Bu3_uu1j7BKSQQKEwlxZTDKoeiPafFWpSLteCvqem886-IwLU_CzEEvpZiovba5LtFQC_wIN9JWqDa2iiXfys35n3HbTowfqL5J3qJoARvo1ODvPes0whQCuqV0l6s--_y6WnO35L12fe4IXJBY70IYhTejshOUxF_D01ylgvGxAAQICJQHVOIySV12Reu-_PFdIBMi_sDfUqlKbUdQA7xD5k6yYoL7XOjr7-YgWrlXNSGzSDpxWxK0cc5B2wOPGrmrYyMMhN4vtOX_k4pqDalRk7eiKtn8Vx67-Ukx5ffQcz7gTPvf8NE2U6erK1fpnEdabpCOJ7NJ5PVPFReiblE18="

OWNER_ID = 7499742938

# Initial bot admin
INITIAL_ADMINS = {
    6239941845,
}

BOT_NAME = "JASMINE X MUSIC"
BOT_USERNAME = "JasmineXmusicbot"


# ============================================================
# SUPPORT / CHANNELS
# ============================================================

SUPPORT_GROUP = "https://t.me/+rSUEvBcRswkwYThh"
SUPPORT_GROUP_ID = -1004462544512

SUPPORT_CHANNEL = "https://t.me/AS_WORKSPACE"
SUPPORT_CHANNEL_ID = -1003598183958

UPDATE_CHANNEL = "https://t.me/Jasminesupport"
UPDATE_CHANNEL_ID = -1004402662430


# ============================================================
# START MESSAGE + PHOTO
# ============================================================

# Put the Telegram photo file_id here.
# Example:
# START_PHOTO = "AgACAgUAAxkBAA..."
#
# Leave it as "" if you don't want a photo.
START_PHOTO = ""

START_MESSAGE = """🎵 **JASMINE X MUSIC**

Welcome to JASMINE X MUSIC.

🎧 Music • 🎬 Video • ⚡ Fast Playback

Use /help to see all commands.
"""


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "jasmine_music.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False)
db.row_factory = sqlite3.Row

db.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        added_at INTEGER
    )
    """
)

db.execute(
    """
    CREATE TABLE IF NOT EXISTS groups (
        chat_id INTEGER PRIMARY KEY,
        title TEXT,
        added_at INTEGER
    )
    """
)

db.execute(
    """
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        added_by INTEGER,
        added_at INTEGER
    )
    """
)

db.commit()


def save_user(user):
    if not user:
        return

    db.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, first_name, username, added_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user.id,
            user.first_name or "",
            user.username or "",
            int(time.time()),
        ),
    )
    db.commit()


def save_group(chat):
    if not chat:
        return

    db.execute(
        """
        INSERT OR IGNORE INTO groups
        (chat_id, title, added_at)
        VALUES (?, ?, ?)
        """,
        (
            chat.id,
            chat.title or "",
            int(time.time()),
        ),
    )
    db.commit()


def add_admin(user_id, added_by):
    db.execute(
        """
        INSERT OR REPLACE INTO admins
        (user_id, added_by, added_at)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            added_by,
            int(time.time()),
        ),
    )
    db.commit()


def remove_admin(user_id):
    db.execute(
        "DELETE FROM admins WHERE user_id = ?",
        (user_id,),
    )
    db.commit()


def is_bot_admin(user_id):
    if user_id == OWNER_ID:
        return True

    row = db.execute(
        "SELECT user_id FROM admins WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    return row is not None


def admin_list():
    rows = db.execute(
        "SELECT user_id FROM admins ORDER BY added_at"
    ).fetchall()

    return [row["user_id"] for row in rows]


for admin_id in INITIAL_ADMINS:
    add_admin(admin_id, OWNER_ID)


# ============================================================
# PYROGRAM + PYTGCALLS
# ============================================================

bot = Client(
    "jasmine_x_music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

user = Client(
    "jasmine_x_music_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

calls = PyTgCalls(user)


# ============================================================
# PLAYBACK QUEUES
# ============================================================

queues = {}


# ============================================================
# YOUTUBE
# ============================================================

def youtube_search(query):
    options = {
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "noplaylist": True,
        "skip_download": True,
        "format": "best",
    }

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(query, download=False)

    if not info:
        raise RuntimeError("No result found.")

    if "entries" in info:
        entries = info.get("entries") or []

        if not entries:
            raise RuntimeError("No result found.")

        info = entries[0]

    webpage = info.get("webpage_url")

    if not webpage:
        webpage = info.get("original_url")

    if not webpage:
        webpage = query

    return {
        "title": info.get("title", "Unknown"),
        "url": webpage,
    }


# ============================================================
# START KEYBOARD
# ============================================================

def start_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎵 Commands",
                    callback_data="commands",
                ),
                InlineKeyboardButton(
                    "➕ Add Me",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📢 Updates",
                    url=UPDATE_CHANNEL,
                ),
                InlineKeyboardButton(
                    "💬 Support",
                    url=SUPPORT_GROUP,
                ),
            ],
        ]
    )


# ============================================================
# START
# ============================================================

@bot.on_message(filters.command("start"))
async def start_command(_, message: Message):
    if message.from_user:
        save_user(message.from_user)

    keyboard = start_keyboard()

    if START_PHOTO:
        await message.reply_photo(
            START_PHOTO,
            caption=START_MESSAGE,
            reply_markup=keyboard,
        )
    else:
        await message.reply_text(
            START_MESSAGE,
            reply_markup=keyboard,
        )


# ============================================================
# HELP
# ============================================================

@bot.on_message(filters.command("help"))
async def help_command(_, message: Message):
    text = """🎵 **JASMINE X MUSIC**

**Music**
/play <song>
/vplay <video>
/skip
/pause
/resume
/stop
/queue
/song
/shuffle
/clear

**Bot Admin**
/admins
/addadmin <user_id>
/deladmin <user_id>
/stats
/ping
/broadcast <message>
/broadcast_groups <message>
/panel
/restart
"""
    await message.reply_text(text)


# ============================================================
# CALLBACK: COMMANDS
# ============================================================

@bot.on_callback_query(filters.regex("^commands$"))
async def commands_callback(_, query: CallbackQuery):
    await query.answer()

    await query.message.edit_text(
        """🎵 **JASMINE X MUSIC**

▶️ `/play song`
🎬 `/vplay video`
⏭ `/skip`
⏸ `/pause`
▶️ `/resume`
⏹ `/stop`
📜 `/queue`
🎵 `/song`
🔀 `/shuffle`
🗑 `/clear`

Use /help for more commands.
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="back_start",
                    )
                ]
            ]
        ),
    )


@bot.on_callback_query(filters.regex("^back_start$"))
async def back_start_callback(_, query: CallbackQuery):
    await query.answer()
    await query.message.delete()

    if START_PHOTO:
        await bot.send_photo(
            query.message.chat.id,
            START_PHOTO,
            caption=START_MESSAGE,
            reply_markup=start_keyboard(),
        )
    else:
        await bot.send_message(
            query.message.chat.id,
            START_MESSAGE,
            reply_markup=start_keyboard(),
        )


# ============================================================
# SAVE USERS + GROUPS
# ============================================================

@bot.on_message(filters.incoming)
async def database_handler(_, message: Message):
    try:
        if message.from_user:
            save_user(message.from_user)

        if message.chat.type in (
            ChatType.GROUP,
            ChatType.SUPERGROUP,
        ):
            save_group(message.chat)

    except Exception:
        pass


# ============================================================
# CHECK GROUP ADMIN
# ============================================================

async def group_admin_required(message):
    if not message.from_user:
        return False

    if is_bot_admin(message.from_user.id):
        return True

    try:
        member = await bot.get_chat_member(
            message.chat.id,
            message.from_user.id,
        )

        return str(member.status) in (
            "administrator",
            "owner",
        )

    except Exception:
        return False


# ============================================================
# PLAY HELPER
# ============================================================

async def play_item(chat_id, item):
    # Audio playback
    await calls.play(
        chat_id,
        MediaStream(
            item["url"],
            video_flags=MediaStream.Flags.IGNORE,
        ),
    )


# ============================================================
# /PLAY
# ============================================================

@bot.on_message(filters.command("play"))
async def play_command(_, message: Message):
    if message.chat.type not in (
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    ):
        await message.reply_text(
            "❌ Use /play inside a group."
        )
        return

    if len(message.command) < 2:
        await message.reply_text(
            "🎵 Usage:\n`/play song name`"
        )
        return

    query = " ".join(message.command[1:])

    status = await message.reply_text(
        "🔎 **Searching...**"
    )

    try:
        item = await asyncio.to_thread(
            youtube_search,
            query,
        )
    except Exception as exc:
        await status.edit_text(
            f"❌ Search failed.\n\n`{str(exc)[:500]}`"
        )
        return

    chat_id = message.chat.id

    if chat_id not in queues:
        queues[chat_id] = []

    queues[chat_id].append(item)

    if len(queues[chat_id]) > 1:
        await status.edit_text(
            f"✅ **Added to queue**\n\n"
            f"🎵 {item['title']}\n"
            f"📍 Position: `{len(queues[chat_id])}`"
        )
        return

    try:
        await play_item(chat_id, item)

        await status.edit_text(
            f"🎵 **Now Playing**\n\n"
            f"**{item['title']}**"
        )

    except Exception as exc:
        queues.pop(chat_id, None)

        await status.edit_text(
            f"❌ Playback failed.\n\n`{str(exc)[:500]}`"
        )


# ============================================================
# /VPLAY
# ============================================================

@bot.on_message(filters.command("vplay"))
async def vplay_command(_, message: Message):
    if message.chat.type not in (
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    ):
        await message.reply_text(
            "❌ Use /vplay inside a group."
        )
        return

    if len(message.command) < 2:
        await message.reply_text(
            "🎬 Usage:\n`/vplay video name`"
        )
        return

    query = " ".join(message.command[1:])

    status = await message.reply_text(
        "🎬 **Searching video...**"
    )

    try:
        item = await asyncio.to_thread(
            youtube_search,
            query,
        )
    except Exception as exc:
        await status.edit_text(
            f"❌ Video search failed.\n\n`{str(exc)[:500]}`"
        )
        return

    chat_id = message.chat.id

    if chat_id not in queues:
        queues[chat_id] = []

    queues[chat_id].append(item)

    if len(queues[chat_id]) > 1:
        await status.edit_text(
            f"🎬 **Video added to queue**\n\n"
            f"🎥 {item['title']}\n"
            f"📍 Position: `{len(queues[chat_id])}`"
        )
        return

    try:
        await calls.play(
            chat_id,
            MediaStream(
                item["url"],
                video_flags=MediaStream.Flags.AUTO_DETECT,
            ),
        )

        await status.edit_text(
            f"🎬 **Now Playing**\n\n"
            f"**{item['title']}**"
        )

    except Exception as exc:
        queues.pop(chat_id, None)

        await status.edit_text(
            f"❌ Video playback failed.\n\n`{str(exc)[:500]}`"
        )


# ============================================================
# /SKIP
# ============================================================

@bot.on_message(filters.command("skip"))
async def skip_command(_, message: Message):
    if not await group_admin_required(message):
        await message.reply_text("❌ Admin only.")
        return

    chat_id = message.chat.id

    if chat_id not in queues or not queues[chat_id]:
        await message.reply_text("📭 Queue is empty.")
        return

    queues[chat_id].pop(0)

    if not queues[chat_id]:
        try:
            await calls.leave_call(chat_id)
        except Exception:
            pass

        await message.reply_text("⏹ **Queue finished.**")
        return

    item = queues[chat_id][0]

    try:
        await play_item(chat_id, item)

        await message.reply_text(
            f"🎵 **Now Playing**\n\n**{item['title']}**"
        )
    except Exception as exc:
        await message.reply_text(
            f"❌ Playback failed.\n`{str(exc)[:500]}`"
        )


# ============================================================
# /PAUSE
# ============================================================

@bot.on_message(filters.command("pause"))
async def pause_command(_, message: Message):
    if not await group_admin_required(message):
        await message.reply_text("❌ Admin only.")
        return

    try:
        await calls.pause(message.chat.id)
        await message.reply_text("⏸ **Paused.**")
    except Exception as exc:
        await message.reply_text(
            f"❌ `{str(exc)[:500]}`"
        )


# ============================================================
# /RESUME
# ============================================================

@bot.on_message(filters.command("resume"))
async def resume_command(_, message: Message):
    if not await group_admin_required(message):
        await message.reply_text("❌ Admin only.")
        return

    try:
        await calls.resume(message.chat.id)
        await message.reply_text("▶️ **Resumed.**")
    except Exception as exc:
        await message.reply_text(
            f"❌ `{str(exc)[:500]}`"
        )


# ============================================================
# /STOP
# ============================================================

@bot.on_message(filters.command("stop"))
async def stop_command(_, message: Message):
    if not await group_admin_required(message):
        await message.reply_text("❌ Admin only.")
        return

    chat_id = message.chat.id
    queues.pop(chat_id, None)

    try:
        await calls.leave_call(chat_id)
    except Exception:
        pass

    await message.reply_text(
        "⏹ **Playback stopped.**"
    )


# ============================================================
# /QUEUE
# ============================================================

@bot.on_message(filters.command("queue"))
async def queue_command(_, message: Message):
    chat_id = message.chat.id

    if chat_id not in queues or not queues[chat_id]:
        await message.reply_text("📭 **Queue is empty.**")
        return

    lines = ["📜 **JASMINE X MUSIC QUEUE**", ""]

    for index, item in enumerate(queues[chat_id], 1):
        lines.append(
            f"`{index}.` 🎵 {item['title']}"
        )

    await message.reply_text(
        "\n".join(lines)
    )


# ============================================================
# /SONG
# ============================================================

@bot.on_message(filters.command("song"))
async def song_command(_, message: Message):
    chat_id = message.chat.id

    if chat_id not in queues or not queues[chat_id]:
        await message.reply_text(
            "📭 Nothing is playing."
        )
        return

    item = queues[chat_id][0]

    await message.reply_text(
        f"🎵 **Current Track**\n\n"
        f"**{item['title']}**\n\n"
        f"🔗 {item['url']}"
    )


# ============================================================
# /SHUFFLE
# ============================================================

@bot.on_message(filters.command("shuffle"))
async def shuffle_command(_, message: Message):
    if not await group_admin_required(message):
        await message.reply_text("❌ Admin only.")
        return

    chat_id = message.chat.id

    if chat_id not in queues or len(queues[chat_id]) < 3:
        await message.reply_text(
            "❌ Not enough songs to shuffle."
        )
        return

    import random

    current = queues[chat_id][0]
    remaining = queues[chat_id][1:]

    random.shuffle(remaining)

    queues[chat_id] = [current] + remaining

    await message.reply_text(
        "🔀 **Queue shuffled!**"
    )


# ============================================================
# /CLEAR
# ============================================================

@bot.on_message(filters.command("clear"))
async def clear_command(_, message: Message):
    if not await group_admin_required(message):
        await message.reply_text("❌ Admin only.")
        return

    chat_id = message.chat.id

    if chat_id not in queues or not queues[chat_id]:
        await message.reply_text(
            "📭 Queue is already empty."
        )
        return

    queues[chat_id] = [queues[chat_id][0]]

    await message.reply_text(
        "🗑 **Queue cleared.**"
    )


# ============================================================
# /ADDMIN
# ============================================================

@bot.on_message(filters.command("addadmin"))
async def addadmin_command(_, message: Message):
    if not message.from_user or message.from_user.id != OWNER_ID:
        await message.reply_text("❌ Owner only.")
        return

    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n`/addadmin USER_ID`"
        )
        return

    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text(
            "❌ Invalid user ID."
        )
        return

    add_admin(user_id, message.from_user.id)

    await message.reply_text(
        f"✅ `{user_id}` is now a bot admin."
    )


# ============================================================
# /DELADMIN
# =====
