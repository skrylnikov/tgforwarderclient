import logging
import os
import asyncio

from pyrogram import Client, filters, handlers

from dotenv import load_dotenv

load_dotenv()

loop = asyncio.get_event_loop()
queues = {}

CHANNELS_LIST = os.getenv("CHANNELS").split(",")
CHAT_IDS = [int(chat_id) for chat_id in os.getenv("CHAT_IDS").split(",")]
SESSION_STRING = os.getenv("SESSION_KEY", "bot_session")


logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y/%m/%d %H:%M:%S",
    format="%(levelname)s: %(message)s",
)

def send_media_group(client, media_group_id):
    settings = get_settings()

    for chat_id in settings.chats:
        loop.create_task(client.forward_messages(chat_id, *queues[media_group_id]))


async def channel_handler(client, msg):
    if msg.chat.username in CHANNELS_LIST and not msg.edit_date:
        logging.info(msg.chat)

        if hasattr(msg, 'media_group_id') and msg.media_group_id:
            if msg.media_group_id not in queues:
                queues[msg.media_group_id] = (msg.chat.id, [])
                loop.call_later(10, send_media_group, client, msg.media_group_id)

            queues[msg.media_group_id][1].append(msg.message_id)
        else:
            for chat_id in CHAT_IDS:
                await msg.forward(chat_id)


def main():
    app = Client(SESSION_STRING, os.getenv('API_ID'), os.getenv('API_HASH'))
    app.add_handler(handlers.MessageHandler(channel_handler, filters.channel))
    app.run()


if __name__ == "__main__":
    main()
