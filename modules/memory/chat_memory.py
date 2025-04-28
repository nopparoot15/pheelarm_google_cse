import re
import json
from typing import List, Optional
from redis.asyncio import Redis

from modules.utils.token_counter import count_tokens  # ✅ นับ token ได้
from modules.utils.cleaner import clean_output_text   # ✅ เก็บ raw แต่เวลาสร้าง context จะ clean เบา ๆ

# ✅ เก็บแชทลง Redis (raw ไม่ clean ก่อนเก็บ)
async def store_chat(redis_instance: Redis, user_id: int, message: dict) -> None:
    key = f"chat:{user_id}"
    await redis_instance.rpush(key, json.dumps(message))
    await redis_instance.expire(key, 86400)

# ✅ ดึงแชทย้อนหลัง
async def get_chat_history(redis_instance: Redis, user_id: int, limit: int = 20) -> List[dict]:
    key = f"chat:{user_id}"
    raw_messages = await redis_instance.lrange(key, -limit, -1)
    return [json.loads(m) for m in raw_messages]

# ✅ สร้าง context แบบ "เหมือน ChatGPT" (คุม token limit ฉลาด)
async def build_chat_context_smart(
    redis_instance: Redis,
    user_id: int,
    new_input: str,
    *,
    system_prompt: str,
    model: str = "gpt-4o-mini",
    max_tokens_context: int = 1000,
    initial_limit: int = 6,
) -> List[dict]:
    messages = [{"role": "system", "content": system_prompt}]
    history = await get_chat_history(redis_instance, user_id, limit=initial_limit)

    for entry in history:
        q = entry.get("question")
        r = entry.get("response")
        if q and r:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": r})

    messages.append({"role": "user", "content": new_input})

    # ✅ ตัด context ถ้า token เกิน
    while True:
        token_used = count_tokens(messages, model=model)
        if token_used <= max_tokens_context or len(messages) <= 2:
            break
        messages.pop(1)  # ลบข้อความที่ 1 ออก (หลัง system) เพื่อให้ยังคง "สั้น+ใหม่สุด"

    return messages

# ✅ ดึงข้อความล่าสุด
async def get_previous_message(redis_instance: Redis, user_id: int) -> Optional[str]:
    key = f"chat:{user_id}"
    raw_messages = await redis_instance.lrange(key, -1, -1)
    if not raw_messages:
        return None

    try:
        last = json.loads(raw_messages[0])
        return last.get("question")
    except Exception:
        return None
