from typing import Any
import os
import asyncio

import dotenv
from aiogram.filters import Command
from aiogram import Router
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


dotenv.load_dotenv(dotenv.find_dotenv())


router = Router()

class WeatherStates(StatesGroup):
    start_point = State()
    end_point = State()
    forecast_interval = State()


async def set_default_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        commands=[
            BotCommand(
                command=k,
                description=v,
            ) for k, v in {
                "/start": "Приветствие пользователя",
                "/help": "Предоставление списка доступных команд и краткой инструкции по их использованию",
                "/weather": "Получить прогноз погоды",
            }.items()
        ],
        scope=BotCommandScopeDefault(),
    )

@router.message(Command("start"))
async def start_command(message: types.Message) -> None:
    await message.answer("Привет! Я бот для прогнозов и маршрутов. Давай посмотрим что там по погоде!")

@router.message(Command("help"))
async def help_command(message: types.Message) -> None:
    await message.answer("Используй:\n/start для приветствия\n/help для помощи\n/weather для получения прогноза: выбери начальную, конечную точки маршрута, выбери временной промежуток и в путь!")

@router.message(Command("weather"))
async def weather_command(message: types.Message, state: FSMContext) -> None:
    await state.set_state(WeatherStates.start_point)
    await message.answer("Введите начальную точку маршрута:")

@router.message(WeatherStates.start_point)
async def process_start_point(message: types.Message, state: FSMContext) -> None:
    await state.update_data(start_point=message.text)
    await state.set_state(WeatherStates.end_point)
    await message.answer("Введите конечную точку маршрута:")

@router.message(WeatherStates.end_point)
async def process_end_point(message: types.Message, state: FSMContext) -> None:
    await state.update_data(end_point=message.text)

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Прогноз на 3 дня", callback_data="forecast_3d")],
        [InlineKeyboardButton(text="Прогноз на неделю", callback_data="forecast_7d")]
    ])

    await state.set_state(WeatherStates.forecast_interval)
    await message.answer("Выберите временной интервал прогноза:", reply_markup=inline_kb)

@router.callback_query(WeatherStates.forecast_interval)
async def process_forecast_interval(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    intervals = {
        "forecast_3d": "Прогноз на 3 дня",
        "forecast_7d": "Прогноз на неделю",
    }
    forecast = intervals.get(str(callback_query.data), "Неизвестный интервал!")

    data = await state.get_data()
    start_point = data.get("start_point")
    end_point = data.get("end_point")

    response = (
        f"Ваш запрос для прогноза:\n"
        f"Начальная точка: {start_point}\n"
        f"Конечная точка: {end_point}\n"
        f"{forecast}"
    )
    await callback_query.message.answer(response) # type: ignore
    await callback_query.answer()

    await state.clear()

async def run() -> None:
    bot = Bot(token=os.getenv("BOT_TOKEN", ""))
    dp = Dispatcher(
        bot=bot,
        storage=MemoryStorage(),
    )
    dp.include_router(router)
    await set_default_commands(bot)
    await dp.start_polling(bot)
