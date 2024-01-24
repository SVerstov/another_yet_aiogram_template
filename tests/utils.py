from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.methods import SendMessage
from aiogram.types import Message, Update, Chat, CallbackQuery, User as TgUser

from tests.mocked_bot import MockedBot


async def get_expected_answer(
    bot: MockedBot, dp: Dispatcher, update: Update
) -> SendMessage | None:
    await dp.feed_update(bot, update)
    return bot.to_send


class FakeUpdateMaker:
    update_id_counter = 1
    message_id_counter = 1

    def __init__(
        self, user_id: int =123, chat_id: int | None = None, first_name: str | None = None
    ):
        self.user_id = user_id
        self.chat_id = chat_id or user_id
        self.tg_user = TgUser(
            id=user_id, is_bot=False, first_name=first_name or "Tester"
        )
        self.chat = Chat(id=self.chat_id, is_bot=False, type="private")

    def message(self, text):
        """Создает фейковый Update с сообщением."""
        message = Message(
            message_id=FakeUpdateMaker.message_id_counter,
            from_user=self.tg_user,
            date=datetime.now(),
            chat=self.chat,
            text=text,
            sender_chat=self.chat,
        )
        update = Update(update_id=FakeUpdateMaker.update_id_counter, message=message)

        FakeUpdateMaker.update_id_counter += 1
        FakeUpdateMaker.message_id_counter += 1
        return update

    def callback(self, callback_data):
        """Создает фейковый Update с callback_query."""
        callback_query = CallbackQuery(
            id=str(FakeUpdateMaker.update_id_counter),
            chat_instance="some_chat_id",
            from_user=self.tg_user,
            message=Message(
                message_id=FakeUpdateMaker.message_id_counter,
                chat=Chat(id=self.chat_id, type="private"),
                date=datetime.now(),
                text="text",
            ),
            data=callback_data,
        )
        update = Update(
            update_id=FakeUpdateMaker.update_id_counter, callback_query=callback_query
        )

        # Инкрементируем счетчики
        FakeUpdateMaker.update_id_counter += 1
        FakeUpdateMaker.message_id_counter += 1

        return update
