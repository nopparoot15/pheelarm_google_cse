import os
from redis.asyncio import from_url
from modules.utils.cleaner import clean_output_text
from modules.core.logger import logger

redis_instance = from_url(os.getenv("REDIS_URL"), decode_responses=True)

# ✅ system prompt ใหม่: สั้น กระชับ แต่คงบุคลิกพี่หลาม
async def process_message(user_id: int, text: str) -> str:
    base_prompt = (
        "คุณคือ 'พี่หลาม' หรือ 'พรี่หลาม' บอทผู้ช่วยพูดจาเป็นกันเอง ใช้ภาษาธรรมชาติแบบคนไทยทั่วไป "
        "คุยเหมือนเพื่อนวัยรุ่น มีมุกบ้างเป็นธรรมชาติ ไม่เน้นความเป็นทางการ "
        "ปรับน้ำเสียงตามลักษณะข้อความของผู้พูด เช่น ถ้าเศร้าให้ปลอบ ถ้ากวนให้คุยกวน "
        "แต่ไม่ต้องดัดแปลงตัวตนหลักของพี่หลาม "
        "อย่าแสดงตัวว่าเป็น AI เว้นแต่ถูกถามตรง ๆ\n\n"
    )

    return clean_output_text(base_prompt)

# ✅ ฟังก์ชันสร้างตาราง context (ไม่ต้องแก้)
async def create_table():
    try:
        async with bot.pool.acquire() as con:
            await con.execute("""
                CREATE TABLE IF NOT EXISTS context (
                    id BIGINT PRIMARY KEY,
                    chatcontext TEXT[] DEFAULT ARRAY[]::TEXT[]
                )
            """)
            logger.info("✅ ตรวจสอบและสร้างตาราง context แล้ว")
    except Exception as e:
        logger.error(f'เกิดข้อผิดพลาดในการสร้างตาราง: {e}')
