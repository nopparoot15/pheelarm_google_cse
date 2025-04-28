import re

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

# 🧠 ยังมี match_topic() อยู่ เพื่อหา topic เฉพาะ เช่น ดูรูป, ทอง, ดวง
def match_topic(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["ดูรูป", "หารูป", "ขอรูป", "ค้นรูป"]):
        return "image"
    if "หวย" in lowered or "ลอตเตอรี่" in lowered:
        return "lotto"
    if "แลกเงิน" in lowered or "อัตราแลกเปลี่ยน" in lowered:
        return "exchange"
    if "ราคาทอง" in lowered or "ทองคำ" in lowered:
        return "gold"
    if "ราคาน้ำมัน" in lowered or "น้ำมัน" in lowered:
        return "oil"
    if "ข่าววันนี้" in lowered or "ข่าว" in lowered:
        return "news"
    if "ข่าวโลก" in lowered or "ข่าวต่างประเทศ" in lowered:
        return "global_news"
    if "อากาศ" in lowered or "พยากรณ์อากาศ" in lowered:
        return "weather"
    if "ดูดวง" in lowered or "ไพ่ทาโรต์" in lowered or "ทาโรต์" in lowered:
        return "tarot"
    return ""

