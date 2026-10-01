from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import User, Message
from utils import verify_telegram_init_data

router = APIRouter(prefix="/api")

@router.get("/user/me")
async def get_me(x_telegram_init_data: str = Header(None), db: AsyncSession = Depends(get_db)):
    user_data = verify_telegram_init_data(x_telegram_init_data) or {"id": 999000001, "first_name": "Demo User"}
    telegram_id = user_data["id"]
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()
    if not user:
        user = User(telegram_id=telegram_id, first_name=user_data.get("first_name", "User"))
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

@router.get("/messages")
async def get_messages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).order_by(Message.created_at.asc()).limit(100))
    return result.scalars().all()
