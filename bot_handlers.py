from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import settings

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="💬 Chatni Ochish", web_app=WebAppInfo(url=settings.WEBAPP_URL))
        ]]
    )
    await message.answer(f"Xush kelibsiz, {message.from_user.first_name}!", reply_markup=kb)
