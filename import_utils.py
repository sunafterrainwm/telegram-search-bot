import datetime

from database import OpenableDBSession, Message, User, Chat
from utils import get_text_func

_ = get_text_func()


def strip_user_id(id_):
    id_str = str(id_)
    if id_str.startswith("user"):
        return int(id_str[4:])
    return int(id_str)


def insert_chat_or_do_nothing(session: OpenableDBSession, chat_id: int, title: str):
    target_chat = session.query(Chat).get(chat_id)
    if not target_chat:
        new_chat = Chat(id=chat_id, title=title, enable=False)
        session.add(new_chat)
        session.commit()


def insert_user_or_do_nothing(
    session: OpenableDBSession, user_id: int, fullname: str, username: str
):
    target_user = session.query(User).get(user_id)
    if not target_user:
        new_user = User(id=user_id, fullname=fullname, username=username)
        session.add(new_user)
        session.commit()


def insert_messages(session: OpenableDBSession, chat_id: int, messages: list):
    success_count = 0
    skip_count = 0
    fail_count = 0
    fail_messages = []

    for message in messages:
        if "from_id" not in message or "user" not in message["from_id"]:
            skip_count += 1
            continue

        insert_user_or_do_nothing(
            session, message["from_id"][4:], message["from"], message["from"]
        )
        if isinstance(message["text"], list):
            msg_text = ""
            for obj in message["text"]:
                if isinstance(obj, dict):
                    msg_text += obj["text"]
                else:
                    msg_text += obj
        else:
            msg_text = message["text"]

        if msg_text == "":
            msg_text == _("[other msg]")
        message_date = datetime.strptime(message["date"], "%Y-%m-%dT%H:%M:%S")
        link_chat_id = str(chat_id)[4:]
        from_id = strip_user_id(message["from_id"])
        new_msg = Message(
            id=message["id"],
            link="https://t.me/c/{}/{}".format(link_chat_id, message["id"]),
            text=msg_text,
            video="",
            photo="",
            audio="",
            voice="",
            type="text",
            category="",
            from_id=from_id,
            from_chat=chat_id,
            date=message_date,
        )

        try:
            session.add(new_msg)
            session.commit()
            success_count += 1
        except Exception as e:
            print(e)
            fail_count += 1
            fail_messages.append(str(message))

    return success_count, skip_count, fail_count, fail_messages
