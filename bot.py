import os
import asyncio

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError


# =========================
# RAILWAY VARIABLES
# =========================

try:
    API_ID = int(os.environ["API_ID"])
except (KeyError, ValueError):
    raise RuntimeError("❌ API_ID missing ya invalid hai.")

API_HASH = os.environ.get("API_HASH", "").strip()
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()

if not API_HASH:
    raise RuntimeError("❌ API_HASH missing hai.")

if not SESSION_STRING:
    raise RuntimeError("❌ SESSION_STRING missing hai.")

try:
    SOURCE = int(os.environ["SOURCE"])
    DESTINATION = int(os.environ["DESTINATION"])
except (KeyError, ValueError):
    raise RuntimeError(
        "❌ SOURCE ya DESTINATION invalid hai. "
        "Channel ID -100... format me do."
    )


# =========================
# TELETHON CLIENT
# =========================

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)


# =========================
# SETTINGS
# =========================

LAST_ID = 0
COPYING_OLD = True


# =========================
# COPY MESSAGE
# =========================

async def copy_message(message):
    global LAST_ID

    try:
        await client.send_message(
            DESTINATION,
            message
        )

        LAST_ID = max(LAST_ID, message.id)

        print(f"✅ Copied: {message.id}")

    except FloodWaitError as e:
        print(f"⏳ FloodWait: {e.seconds} seconds")

        await asyncio.sleep(e.seconds)

        await copy_message(message)

    except Exception as e:
        print(f"❌ Error {message.id}: {e}")


# =========================
# LIVE MESSAGES
# =========================

@client.on(events.NewMessage(chats=SOURCE))
async def live_message(event):

    global LAST_ID

    # Old messages copy hone tak live message ko ignore
    # karenge; baad me history cutoff ke baad live copy hoga.
    if COPYING_OLD:
        return

    if event.message.id > LAST_ID:
        await copy_message(event.message)


# =========================
# OLD MESSAGE COPY
# =========================

async def copy_old_messages():
    global LAST_ID
    global COPYING_OLD

    print("📦 Old messages copy start...")

    messages = []

    async for message in client.iter_messages(
        SOURCE,
        reverse=True
    ):
        messages.append(message)

    print(f"📦 Total messages found: {len(messages)}")

    for message in messages:

        if message.id <= LAST_ID:
            continue

        await copy_message(message)

        # Flood limit avoid karne ke liye
        await asyncio.sleep(0.3)

    COPYING_OLD = False

    print("✅ Old messages copy complete.")
    print("🟢 Live forwarding active.")


# =========================
# MAIN
# =========================

async def main():

    print("🚀 Starting Telethon Userbot...")

    await client.start()

    print("✅ Telegram connected.")

    me = await client.get_me()

    print(
        f"👤 Logged in as: "
        f"{me.first_name or ''} "
        f"(@{me.username or 'no_username'})"
    )

    # Check source
    try:
        source_chat = await client.get_entity(SOURCE)
        print(f"📥 Source: {getattr(source_chat, 'title', SOURCE)}")
    except Exception as e:
        print(f"❌ Source channel access error: {e}")
        await client.disconnect()
        return

    # Check destination
    try:
        destination_chat = await client.get_entity(DESTINATION)
        print(
            f"📤 Destination: "
            f"{getattr(destination_chat, 'title', DESTINATION)}"
        )
    except Exception as e:
        print(f"❌ Destination channel access error: {e}")
        await client.disconnect()
        return

    # Copy old messages
    await copy_old_messages()

    print("🤖 Userbot is running...")

    # Keep running
    await client.run_until_disconnected()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    asyncio.run(main())
