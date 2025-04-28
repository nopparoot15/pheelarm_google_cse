# 🔹 Standard Library
import os
import json
import asyncio
import random
import re
from datetime import datetime
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

# 🔹 Third-Party Packages
import asyncpg
import discord
import pytz
import httpx
import requests
import redis.asyncio as redis
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from openai import AsyncOpenAI

# 🔹 Local Modules
from modules.features.oil_price import get_oil_price_today
from modules.features.gold_price import get_gold_price_today
from modules.features.lottery_checker import get_lottery_results
from modules.features.exchange_rate import get_exchange_rate
from modules.features.weather_forecast import get_weather
from modules.features.daily_news import get_daily_news
from modules.features.global_news import get_global_news
from modules.features.google_search import search_image
from modules.tarot.tarot_reading import draw_cards_and_interpret_by_topic
from modules.nlp.message_matcher import match_topic
from modules.memory.chat_memory import store_chat, build_chat_context_smart
from modules.utils.cleaner import clean_output_text
from modules.utils.thai_to_eng_city import convert_thai_to_english_city
from modules.utils.thai_datetime import get_thai_datetime_now, format_thai_datetime
from modules.core.logger import logger

# ✅ Load environment variables
load_dotenv()

class Settings(BaseSettings):
    DISCORD_TOKEN: str = Field(..., env='DISCORD_TOKEN')
    OPENAI_API_KEY: str = Field(..., env='OPENAI_API_KEY')
    DATABASE_URL: Optional[str] = Field(None, env='DATABASE_URL')
    PG_USER: Optional[str] = Field(None, env='PGUSER')
    PG_PW: Optional[str] = Field(None, env='PGPASSWORD')
    PG_HOST: Optional[str] = Field(None, env='PGHOST')
    PG_PORT: str = Field('5432', env='PGPORT')
    PG_DB: Optional[str] = Field(None, env='PGDATABASE')
    GOOGLE_API_KEY: Optional[str] = Field(None, env='GOOGLE_API_KEY')
    GOOGLE_CSE_ID: Optional[str] = Field(None, env='GOOGLE_CSE_ID')
    REDIS_URL: str = Field('redis://localhost', env='REDIS_URL')

settings = Settings()

CHANNEL_ID = 1350812185001066538
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
redis_instance = None

async def setup_connection():
    global redis_instance

    for _ in range(3):
        try:
            redis_instance = await redis.from_url(settings.REDIS_URL, decode_responses=True)
            await redis_instance.ping()
            logger.info("✅ Redis connected")
            break
        except Exception as e:
            logger.warning(f"🔁 Redis retry failed: {e}")
            await asyncio.sleep(2)
    else:
        logger.error("❌ Redis connection failed")
        redis_instance = None

    try:
        if settings.DATABASE_URL:
            bot.pool = await asyncpg.create_pool(settings.DATABASE_URL)
            logger.info("✅ PostgreSQL connected (DATABASE_URL)")
        elif settings.PG_USER and settings.PG_PW and settings.PG_HOST and settings.PG_DB:
            bot.pool = await asyncpg.create_pool(
                user=settings.PG_USER,
                password=settings.PG_PW,
                host=settings.PG_HOST,
                port=settings.PG_PORT,
                database=settings.PG_DB
            )
            logger.info("✅ PostgreSQL connected (manual credentials)")
        else:
            bot.pool = None
            logger.warning("⚠️ PostgreSQL credentials not provided. Skipping DB setup.")

    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        bot.pool = None

async def create_table():
    if not bot.pool:
        logger.warning("⚠️ ไม่มี pool PostgreSQL, ข้ามการสร้างตาราง")
        return

    try:
        async with bot.pool.acquire() as con:
            await con.execute("""
                CREATE TABLE IF NOT EXISTS context (
                    id BIGINT PRIMARY KEY,
                    chatcontext TEXT[] DEFAULT ARRAY[]::TEXT[] 
                )
            """)
            logger.info("✅ context table ensured")
    except Exception as e:
        logger.error(f"❌ create_table error: {e}")

async def send_long_reply(message: discord.Message, content: str):
    chunks = re.split(r'(?<=\n\n)', content)
    current_chunk = ""

    for paragraph in chunks:
        if len(current_chunk) + len(paragraph) < 2000:
            current_chunk += paragraph
        else:
            if current_chunk:
                await message.channel.send(current_chunk.strip())
            current_chunk = paragraph

    if current_chunk.strip():
        await message.channel.send(current_chunk.strip())

async def smart_reply(message: discord.Message, content: str):
    content = clean_output_text(content)

    # ลบ markdown [text](url) -> text <url>
    content = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'\1 <\2>', content)
    # ลบลิงก์เปล่า ๆ
    content = re.sub(r'(?<!<)(https?://\S+)(?!>)', r'<\1>', content)
    # ลบ ** เดี่ยว ๆ ที่หลงมา
    content = re.sub(r'(?<!\*)\*\*(?!\*)', '', content)

    if len(content) > 2000:
        await send_long_reply(message, content)
    else:
        try:
            await message.reply(content)
        except discord.HTTPException:
            await message.channel.send(content)

async def process_message(user_id: int, text: str) -> str:
    base_prompt = (
        "คุณคือ 'พี่หลาม' หรือ 'พรี่หลาม' เป็นบอทผู้ช่วยที่พูดจาเป็นกันเองเหมือนมนุษย์ไทย "
        "ใช้ภาษาพูดธรรมดา ไม่เป็นทางการมาก มีอารมณ์ขันบ้างแต่ไม่เกรียน "
        "ตอบคำถามด้วยความจริงใจ เข้าใจง่าย และไม่แสดงตัวว่าเป็น AI เว้นแต่มีคนถามตรง ๆ "
        "ปรับน้ำเสียงให้เข้ากับข้อความที่ได้รับ เช่น หากผู้ใช้ดูเศร้าให้ปลอบใจ หากผู้ใช้ดูขำให้คุยกวน ๆ "
    ).strip()
    return clean_output_text(base_prompt)

async def should_search(question: str) -> bool:
    prompt = f"""
ประเมินคำถามนี้:
- ถ้าตอบได้จากความรู้ทั่วไป (ไม่ต้องค้นหาเว็บ) ตอบ "no_search"
- ถ้าต้องค้นข้อมูลล่าสุดจากเว็บ เช่น ข่าว ราคาสินค้า อากาศ ตอบ "need_search"
อย่าตอบอย่างอื่น

คำถาม: {question}
ตอบ:
""".strip()

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=5,
    )

    decision = response.choices[0].message.content.strip().lower()
    return decision == "need_search"

async def search_google_cse(query: str) -> List[str]:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": settings.GOOGLE_API_KEY,
        "cx": settings.GOOGLE_CSE_ID,
        "q": query,
        "num": 3,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    results = []
    if "items" in data:
        for item in data["items"]:
            snippet = f"{item['title']}: {item['snippet']}"
            results.append(snippet)
    return results

async def generate_reply(user_id: int, text: str) -> str:
    system_prompt = await process_message(user_id, text)
    timezone = await redis_instance.get(f"timezone:{user_id}") or "Asia/Bangkok"
    now = datetime.now(pytz.timezone(timezone))
    system_prompt += f"\n\n⏰ timezone: {timezone}\n🕒 {format_thai_datetime(now)}"

    if await should_search(text):
        logger.info("🌐 ต้องค้นหาเว็บ")
        search_results = await search_google_cse(text)
        search_context = "\n".join(search_results)
        text = f"""ข้อมูลจากการค้นหาเว็บ:\n{search_context}\n\nคำถาม: {text}"""
    else:
        logger.info("🧠 ตอบได้เลย ไม่ต้องค้นหา")

    messages = await build_chat_context_smart(
        redis_instance,
        user_id,
        text,
        system_prompt=system_prompt,
        model="gpt-4o-mini",
        max_tokens_context=1200,
        initial_limit=4
    )

    response = await get_openai_response(
        messages,
        model="gpt-4o-mini",
        temperature=0.5,
    )
    return response
    
@bot.event
async def on_ready():
    await setup_connection()
    await create_table()
    await bot.tree.sync()
    logger.info(f"🚀 {bot.user} is ready!")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.channel.id != CHANNEL_ID or message.content.startswith("!"):
        return

    text = message.content.strip()
    lowered = text.lower()

    topic = match_topic(lowered)

    if topic == "image":
        query = re.sub(r"^(ดูรูป|ค้นรูป|หารูป|ขอรูป)[:,\s]*", "", lowered)
        if not query:
            prev_query = await redis_instance.get(f"last_image_query:{message.author.id}")
            query = prev_query
        if query:
            await redis_instance.set(f"last_image_query:{message.author.id}", query, ex=300)
            image_url = await search_image(query, settings)
            return await message.channel.send(image_url or f"😿 ไม่พบรูปเกี่ยวกับ “{query}”")
        return await message.channel.send("📷 พิมพ์ว่า `ดูรูป: แมว` ลองดูสิ")

    elif topic == "lotto":
        return await message.channel.send(await get_lottery_results())

    elif topic == "exchange":
        return await message.channel.send(await get_exchange_rate())

    elif topic == "gold":
        return await message.channel.send(await get_gold_price_today())

    elif topic == "oil":
        return await message.channel.send(await get_oil_price_today())

    elif topic == "news":
        return await message.channel.send(await get_daily_news())

    elif topic == "global_news":
        return await message.channel.send(await get_global_news())

    elif topic == "weather":
        match = re.search(r"(ที่|จังหวัด|เมือง)\s+(.+)", lowered)
        city = match.group(2).strip() if match else None
        if city:
            eng_city = convert_thai_to_english_city(city)
            return await message.channel.send(await get_weather(eng_city))
        return await message.channel.send("📍 พิมพ์ว่า `อากาศที่ เชียงใหม่`")

    elif topic == "tarot":
        return await message.channel.send("🔮 อยากดูดวงเรื่องอะไรดี? พิมพ์: ความรัก, การงาน, การเงิน, สุขภาพ")

    elif lowered in ["ความรัก", "การงาน", "การเงิน", "สุขภาพ"]:
        return await message.channel.send(await draw_cards_and_interpret_by_topic(lowered))

    elif any(kw in lowered for kw in ["วันนี้วันอะไร", "วันอะไรวันนี้"]):
        return await message.channel.send(f"📅 วันนี้คือ {get_thai_datetime_now()}")

    elif any(kw in lowered for kw in ["กี่โมง", "เวลากี่โมง"]):
        return await message.channel.send(f"🕒 ขณะนี้คือ {get_thai_datetime_now()}")

    async with message.channel.typing():
        try:
            reply = await generate_reply(message.author.id, text)
        except Exception as e:
            logger.error(f"❌ GPT Error: {e}")
            return await message.channel.send("⚠️ พี่หลามงงเลย ตอบไม่ได้จริง ๆ จ้า")

        cleaned = clean_output_text(reply)
        await smart_reply(message, cleaned)

        await store_chat(redis_instance, message.author.id, {
            "question": text,
            "response": reply
        })

async def main():
    await setup_connection()
    if redis_instance:
        if bot.pool is None:
            logger.warning("⚠️ PostgreSQL ไม่เชื่อมต่อ แต่ Redis ติดตั้งแล้ว จะเริ่มบอทแบบใช้เฉพาะ Redis")
        await bot.start(settings.DISCORD_TOKEN)
    else:
        logger.error("❌ ไม่สามารถเริ่มบอทได้ เพราะเชื่อมต่อ Redis ไม่สำเร็จ")

if __name__ == "__main__":
    asyncio.run(main())
