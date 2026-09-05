import os
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

SOURCE = int(os.environ["SOURCE"])
DESTINATION = int(os.environ["DESTINATION"])

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

LAST_ID = 0

async def copy_msg(msg):
    global LAST_ID
    try:
        await msg.copy(DESTINATION)
        LAST_ID = msg.id
        print(f"Copied: {msg.id}")
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await copy_msg(msg)
    except Exception as e:
        print(e)

@app.on_message(filters.chat(SOURCE))
async def live(_, msg):
    if msg.id > LAST_ID:
        await copy_msg(msg)

async def main():
    global LAST_ID
    async for msg in app.get_chat_history(SOURCE, reverse=True):
        await copy_msg(msg)
    await asyncio.Event().wait()

app.run(main())
