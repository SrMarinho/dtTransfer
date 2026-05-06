from src.interfaces.bot import telegram as tg

_REPLY_KEYBOARD = {
    "keyboard": [
        [{"text": "/status"}, {"text": "/jobs"}, {"text": "/help"}],
    ],
    "resize_keyboard": True,
    "persistent": True,
}


def handle(args, user_id=None, chat_id=None):
    tg.send_message(chat_id, "DataReplicator Bot pronto.", reply_markup=_REPLY_KEYBOARD)
