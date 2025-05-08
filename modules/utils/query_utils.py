import re
from modules.core.openai_client import client as openai_client
from modules.core.logger import logger

# 🔧 Keywords ใช้ได้
COMMON_GREETINGS = [
    "สวัสดี", "หวัดดี", "ดีครับ", "ดีจ้า", "เฮลโหล", "hello", "hi", "ทัก", "ฮัลโหล", "โย่"
]

def is_greeting(text: str) -> bool:
    return any(greet in text.lower() for greet in COMMON_GREETINGS)

def is_question(text: str) -> bool:
    QUESTION_HINTS = ["คือ", "อะไร", "ใคร", "ยังไง", "เพราะอะไร", "ทำไม", "หรอ", "?"]
    return any(hint in text for hint in QUESTION_HINTS) or text.strip().endswith("?")

def is_about_bot(text: str) -> bool:
    patterns = [
        r"\b(พี่หลาม|พรี่หลาม|bot|บอท|gpt|คุณหลาม)\b",
        r"ชื่อ.*(บอท|พี่หลาม)",
        r"(พี่หลาม|บอท).*(ทำงาน|ตอบ|เรียนรู้|เกิด|สร้าง|มีชีวิต|พูด|รู้|รู้จัก|คือ)",
        r"(ใคร.*(สร้าง|เขียน|ตั้งชื่อ))",
    ]
    text = text.lower()
    return any(re.search(p, text) for p in patterns)

async def get_openai_response(
    messages: list,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1800,
    temperature: float = 0.6,
    top_p: float = 1.0,
    frequency_penalty: float = 0.2,
    presence_penalty: float = 0.3,
) -> str:
    try:
        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        # ✅ log token usage (ถ้ามี usage object)
        if hasattr(response, "usage") and response.usage:
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            logger.info(f"🧮 Token Usage → Input: {input_tokens} | Output: {output_tokens} | Total: {total_tokens}")

        # ✅ ดึง content ออกอย่างปลอดภัย
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            content = response.choices[0].message.content.strip()
            return content
        else:
            logger.warning("⚠️ No valid choices returned from OpenAI")
            return "⚠️ พี่หลามงงเลย ตอบไม่ได้จริง ๆ จ้า"

    except Exception as e:
        logger.error(f"❌ GPT Error: {e}")
        return "⚠️ พี่หลามขัดข้องชั่วคราว ขออภัยด้วยครับ"
