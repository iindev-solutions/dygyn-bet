from __future__ import annotations

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo


def _keyboard(web_app_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть голосование", web_app=WebAppInfo(url=web_app_url))],
            [InlineKeyboardButton(text="Статистика", web_app=WebAppInfo(url=f"{web_app_url.rstrip('/')}/#stats"))],
        ]
    )


async def run_polling(bot_token: str, web_app_url: str) -> None:
    bot = Bot(bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer(
            "Привет! Это голосование по Играм Дыгына. "
            "Здесь нет денежных ставок: только голосование, очки уверенности и статистика болельщиков.",
            reply_markup=_keyboard(web_app_url),
        )

    @dp.message(Command("app"))
    async def app_cmd(message: Message) -> None:
        await message.answer("Открывай Mini App:", reply_markup=_keyboard(web_app_url))

    @dp.message(Command("rules"))
    async def rules(message: Message) -> None:
        await message.answer(
            "Правила:\n"
            "1. Один Telegram-аккаунт может выбрать до трёх участников на событие.\n"
            "2. Выбор можно менять до закрытия события.\n"
            "3. Очки уверенности виртуальные, денег и выигрышей нет.\n"
            "4. После сохранения можно скачать карточку для сторис.\n"
            "5. После внесения результата начисляются очки рейтинга."
        )

    @dp.message(F.web_app_data)
    async def web_app_data(message: Message) -> None:
        await message.answer("Данные из Mini App получены. Основные действия идут через API внутри TMA.")

    await dp.start_polling(bot)
