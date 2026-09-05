import os
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# =========================
# ENV VARIABLES
# =========================

try:
    API_ID = int(os.environ["API_ID"])
except (KeyError, ValueError):
    raise RuntimeError(
        "API_ID missing or invalid. Railway Variables me valid numeric API_ID add karo."
    )

API_HASH = os.environ.get("API_HASH", "").strip()
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()

if not API_HASH:
    raise RuntimeError("API_HASH Railway Variables me missing hai.")

if not SESSION_STRING:
    raise RuntimeError("SESSION_STRING Railway Variables me missing hai.")

try:
    SOURCE = int(os.environ["SOURCE"])
    DESTINATION = int(os.environ["DESTINATION"])
except (KeyError, ValueError):
    raise RuntimeError(
        "SOURCE ya DESTINATION missing/invalid hai. Telegram channel ID (-100...) use karo."
    )


# =========================
# PYROGRAM CLIENT
# =========================

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


# =========================
# SETTINGS
# =========================

LAST_ID = 0


# =========================
# COPY MESSAGE
# =========================

async def copy_msg(msg):
    global LAST_ID

    try:
        await msg.copy(DESTINATION)

        LAST_ID = max(LAST_ID, msg.id)

        print(f"✅ Copied message: {msg.id}")

    except FloodWait as e:
        print(f"⏳ FloodWait: sleeping {e.value} seconds")

        await asyncio.sleep(e.value)

        await copy_msg(msg)

    except Exception as e:
        print(f"❌ Error copying {msg.id}: {e}")


# =========================
# LIVE FORWARD
# =========================

@app.on_message(filters.chat(SOURCE))
async def live(_, msg):

    if msg.id > LAST_ID:
        await copy_msg(msg)


# =========================
# OLD MESSAGE COPY
# =========================

async def copy_old_messages():

    global LAST_ID

    print("📦 Starting old message copy...")

    count = 0

    # Pyrogram history normally comes newest -> oldest.
    # Store messages first, then reverse them so they are copied
    # from oldest -> newest.

    messages = []

    async for msg in app.get_chat_history(SOURCE):

        messages.append(msg)

    print(f"📦 Found {len(messages)} messages.")

    for msg in reversed(messages):

        if msg.id <= LAST_ID:
            continue

        await copy_msg(msg)

        count += 1

        # Small delay to reduce flood limits
        await asyncio.sleep(0.3)

    print(f"✅ Old message copy completed. Copied: {count}")


# =========================
# MAIN
# =========================

async def main():

    global LAST_ID

    print("🚀 Starting Pyrogram Userbot...")

    # IMPORTANT:
    # Client is started before get_chat_history() is called.

    async with app:

        print("✅ Telegram client connected.")

        me = await app.get_me()

        print(
            f"👤 Logged in as: "
            f"{me.first_name or ''} "
            f"(@{me.username or 'no_username'})"
        )

        # Check source/destination access
        try:
            source_chat = await app.get_chat(SOURCE)
            destination_chat = await app.get_chat(DESTINATION)

            print(f"📥 Source: {source_chat.title or source_chat.first_name}")
            print(f"📤 Destination: {destination_chat.title or destination_chat.first_name}")

        except Exception as e:
            print(f"❌ Channel access error: {e}")
            return

        # Copy old messages first
        await copy_old_messages()

        print("🟢 Live forwarding is now active.")

        # Keep the client running
        await asyncio.Event().wait()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    asyncio.run(main())
