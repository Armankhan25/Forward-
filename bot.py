import os
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# =========================
# ENV VARIABLES
# =========================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

SOURCE = int(os.environ["SOURCE"])
DESTINATION = int(os.environ["DESTINATION"])


# =========================
# PYROGRAM CLIENT
# =========================

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


# Last copied message ID
LAST_ID = 0


# =========================
# COPY MESSAGE
# =========================

async def copy_msg(msg):
    global LAST_ID

    try:
        await msg.copy(DESTINATION)

        LAST_ID = max(LAST_ID, msg.id)

        print(f"Copied: {msg.id}")

    except FloodWait as e:
        print(f"FloodWait: sleeping {e.value} seconds")
        await asyncio.sleep(e.value)

        await copy_msg(msg)

    except Exception as e:
        print(f"Error copying {msg.id}: {e}")


# =========================
# LIVE NEW MESSAGES
# =========================

@app.on_message(filters.chat(SOURCE))
async def live(_, msg):

    if msg.id > LAST_ID:
        await copy_msg(msg)


# =========================
# MAIN
# =========================

async def main():
    global LAST_ID

    print("Starting old message copy...")

    # Pyrogram returns history newest -> oldest.
    # We collect the messages first, then reverse them
    # so they are copied oldest -> newest.

    messages = []

    async for msg in app.get_chat_history(SOURCE):

        messages.append(msg)

    print(f"Found {len(messages)} messages.")

    # Oldest -> newest
    messages.reverse()

    for msg in messages:

        if msg.id > LAST_ID:
            await copy_msg(msg)

    print("Old messages copied successfully.")
    print("Live forwarding started.")

    # Keep userbot running
    await asyncio.Event().wait()


# =========================
# START
# =========================

app.run(main())
