import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

API_ID = 12345678
API_HASH = "YOUR_API_HASH"

# Old channel
SOURCE = -1001234567890

# New channel
DESTINATION = -1009876543210

app = Client(
    "forward_userbot",
    api_id=API_ID,
    api_hash=API_HASH
)


async def copy_message(message):
    while True:
        try:
            await message.copy(DESTINATION)
            print(f"Copied: {message.id}")
            break

        except FloodWait as e:
            print(f"FloodWait: {e.value} seconds")
            await asyncio.sleep(e.value)

        except Exception as e:
            print(f"Error {message.id}: {e}")
            break


@app.on_message(filters.chat(SOURCE))
async def new_message(client, message):
    await copy_message(message)


async def main():
    print("Userbot started...")

    # Existing messages
    print("Copying old messages...")

    async for message in app.get_chat_history(SOURCE, reverse=True):
        await copy_message(message)

    print("Old messages completed.")
    print("Waiting for new messages...")

    await asyncio.Event().wait()


app.run(main())
