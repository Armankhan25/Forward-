import os
import asyncio

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import (
    FloodWaitError,
    AuthKeyDuplicatedError,
)


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

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
except (KeyError, ValueError):
    raise RuntimeError(
        "❌ SOURCE invalid hai. Channel ID -100... format me do."
    )

try:
    DESTINATION = int(os.environ["DESTINATION"])
except (KeyError, ValueError):
    raise RuntimeError(
        "❌ DESTINATION invalid hai. Channel ID -100... format me do."
    )


# =========================================================
# TELETHON CLIENT
# =========================================================

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH,
    auto_reconnect=True,
    connection_retries=5,
    retry_delay=5,
)


# =========================================================
# SETTINGS
# =========================================================

COPYING_OLD = True
LAST_ID = 0


# =========================================================
# COPY MESSAGE
# =========================================================

async def copy_message(message):
    global LAST_ID

    try:

        # Service messages ko ignore karo
        if message.action:
            return

        await client.send_message(
            DESTINATION,
            message
        )

        LAST_ID = max(LAST_ID, message.id)

        print(f"✅ Copied: {message.id}")

    except FloodWaitError as e:

        print(
            f"⏳ FloodWait: {e.seconds} seconds"
        )

        await asyncio.sleep(e.seconds)

        await copy_message(message)

    except Exception as e:

        print(
            f"❌ Error {message.id}: {type(e).__name__}: {e}"
        )


# =========================================================
# LIVE MESSAGE HANDLER
# =========================================================

@client.on(events.NewMessage(chats=SOURCE))
async def live_message(event):

    global LAST_ID

    # Old messages copy hone tak live message ignore
    if COPYING_OLD:
        return

    message = event.message

    if message.id <= LAST_ID:
        return

    await copy_message(message)


# =========================================================
# GET LAST DESTINATION MESSAGE
# =========================================================

async def get_destination_last_id():

    global LAST_ID

    try:

        last_message = await client.get_messages(
            DESTINATION,
            limit=1
        )

        if last_message:

            LAST_ID = last_message[0].id

            print(
                f"📌 Destination last message ID: {LAST_ID}"
            )

        else:

            LAST_ID = 0

            print(
                "📌 Destination empty hai."
            )

    except Exception as e:

        print(
            f"⚠️ Destination last message check failed: {e}"
        )

        LAST_ID = 0


# =========================================================
# COPY OLD MESSAGES
# =========================================================

async def copy_old_messages():

    global LAST_ID
    global COPYING_OLD

    print("📦 Old messages copy start...")

    total = 0

    try:

        async for message in client.iter_messages(
            SOURCE,
            reverse=True
        ):

            if message.id <= LAST_ID:
                continue

            await copy_message(message)

            total += 1

            # Small delay
            await asyncio.sleep(0.3)

        print(
            f"📦 Old messages copied: {total}"
        )

    except FloodWaitError as e:

        print(
            f"⏳ FloodWait during history: "
            f"{e.seconds} seconds"
        )

        await asyncio.sleep(e.seconds)

        await copy_old_messages()

        return

    except Exception as e:

        print(
            f"❌ Old message copy error: "
            f"{type(e).__name__}: {e}"
        )

    COPYING_OLD = False

    print("✅ Old messages copy complete.")
    print("🟢 Live forwarding active.")


# =========================================================
# MAIN
# =========================================================

async def main():

    print("🚀 Starting Telethon Userbot...")

    # -----------------------------------------------------
    # CONNECT WITHOUT INTERACTIVE LOGIN
    # -----------------------------------------------------

    try:

        await client.connect()

    except AuthKeyDuplicatedError:

        print(
            "❌ AuthKeyDuplicatedError!"
        )

        print(
            "❌ Ye SESSION_STRING kisi aur IP/process "
            "par bhi use ho rahi hai."
        )

        print(
            "❌ Same session ko multiple Railway "
            "deployments/processes me mat chalao."
        )

        return

    except Exception as e:

        print(
            f"❌ Telegram connection failed: "
            f"{type(e).__name__}: {e}"
        )

        return

    # -----------------------------------------------------
    # AUTH CHECK
    # -----------------------------------------------------

    try:

        authorized = await client.is_user_authorized()

    except AuthKeyDuplicatedError:

        print(
            "❌ SESSION_STRING AuthKeyDuplicated hai."
        )

        return

    except Exception as e:

        print(
            f"❌ Session check failed: "
            f"{type(e).__name__}: {e}"
        )

        return

    if not authorized:

        print(
            "❌ SESSION_STRING authorized nahi hai."
        )

        print(
            "❌ Telethon String Session invalid/expired hai."
        )

        print(
            "❌ Phone login Railway par possible nahi hai."
        )

        return

    print("✅ Telegram connected.")
    print("✅ Telethon session authorized.")


    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

    try:

        me = await client.get_me()

        print(
            f"👤 Logged in as: "
            f"{me.first_name or ''} "
            f"(@{me.username or 'no_username'})"
        )

    except Exception as e:

        print(
            f"❌ Account information error: {e}"
        )

        return


    # -----------------------------------------------------
    # CHECK SOURCE
    # -----------------------------------------------------

    try:

        source_chat = await client.get_entity(SOURCE)

        print(
            f"📥 Source: "
            f"{getattr(source_chat, 'title', SOURCE)}"
        )

    except Exception as e:

        print(
            f"❌ Source channel access error: {e}"
        )

        return


    # -----------------------------------------------------
    # CHECK DESTINATION
    # -----------------------------------------------------

    try:

        destination_chat = await client.get_entity(
            DESTINATION
        )

        print(
            f"📤 Destination: "
            f"{getattr(destination_chat, 'title', DESTINATION)}"
        )

    except Exception as e:

        print(
            f"❌ Destination channel access error: {e}"
        )

        return


    # -----------------------------------------------------
    # GET DESTINATION LAST MESSAGE
    # -----------------------------------------------------

    await get_destination_last_id()


    # -----------------------------------------------------
    # COPY OLD MESSAGES
    # -----------------------------------------------------

    await copy_old_messages()


    # -----------------------------------------------------
    # RUN FOREVER
    # -----------------------------------------------------

    print("🤖 Userbot is running...")
    print("🟢 Waiting for new messages...")

    try:

        await client.run_until_disconnected()

    except AuthKeyDuplicatedError:

        print(
            "❌ AuthKeyDuplicatedError:"
        )

        print(
            "❌ Same Telethon session kisi "
            "dusre IP/process par chal rahi hai."
        )

    except Exception as e:

        print(
            f"❌ Userbot stopped: "
            f"{type(e).__name__}: {e}"
        )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "🛑 Userbot stopped."
        )
