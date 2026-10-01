import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import settings
from database import init_db, get_db
from models import Message, User
from bot_handlers import router as bot_router
from api_routes import router as api_router
from websocket_manager import manager

# Bot va Dispatcher yaratish
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(bot_router)

# Lifespan: Server ishga tushganda va to'xtaganda bajariladigan amallar
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ma'lumotlar bazasini yaratish
    await init_db()
    
    # Webhook va Menu Button sozlash
    webhook_url = f"{settings.WEBAPP_URL}/webhook"
    await bot.set_webhook(url=webhook_url, secret_token=settings.WEBHOOK_SECRET)
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Open Chat", 
            web_app=WebAppInfo(url=settings.WEBAPP_URL)
        )
    )
    yield
    # Server to'xtatilganda webhookni o'chirish
    await bot.delete_webhook()

app = FastAPI(lifespan=lifespan)

# Statik fayllar va shablonlar
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# API yo'nalishlarini ulash
app.include_router(api_router)

@app.post("/webhook")
async def webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != settings.WEBHOOK_SECRET:
        return {"status": "unauthorized"}
    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# Asosiy sahifa (Jinja2 xatosiz varianti)
@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# WebSocket orqali real-vaqt rejimida muloqot
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: AsyncSession = Depends(get_db)):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            new_msg = Message(sender_id=user_id, text=data.get("text"))
            db.add(new_msg)
            await db.commit()
            await db.refresh(new_msg)
            
            res = await db.execute(select(User).where(User.telegram_id == user_id))
            user = res.scalars().first()
            
            payload = {
                "id": new_msg.id,
                "sender_id": user_id,
                "sender_name": user.first_name if user else "User",
                "text": new_msg.text,
                "created_at": new_msg.created_at.strftime("%H:%M")
            }
            await manager.broadcast(payload)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
