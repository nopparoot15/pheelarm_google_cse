import re
from typing import Optional, Dict, List
from modules.core.logger import logger

# 🔍 รวม pattern ที่ compile แล้วสำหรับการ match หัวข้อ
TOPIC_PATTERNS: Dict[str, List[re.Pattern]] = {
    topic: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for topic, patterns in {
        "oil": [
            r"ราคาน้ำมัน",
            r"น้ำมัน.*วันนี้",
            r"น้ำมันเท่าไหร่",
            r"ตอนนี้.*น้ำมัน",
            r"เบนซิน",
            r"ดีเซล"
        ],
        "gold": [
            r"ราคาทอง",
            r"ทอง.*วันนี้",
            r"ทองขึ้น",
            r"ทองลง",
            r"ทองคำแท่ง",
            r"gold"
        ],
        "lotto": [
            r"(ตรวจ(ผล)?(หวย|สลากกินแบ่ง))",
            r"(หวย|สลากกินแบ่ง).*(งวด|วันนี้|ล่าสุด|ออก.*อะไร)",
            r"(เลข(เด็ด|ออก|ดัง))",
            r"(ผลหวย|ผลสลาก)",
        ],
        "exchange": [
            r"แลกเงิน",
            r"อัตราแลกเปลี่ยน",
            r"ค่าเงิน",
            r"เรทเงิน",
            r"exchange"
        ],
        "weather": [
            r"อากาศ",
            r"พยากรณ์อากาศ",
            r"ฝนตก",
            r"อุณหภูมิ",
            r"ฟ้า",
            r"weather"
        ],
        "global_news": [
            r"ข่าวต่างประเทศ",
            r"ข่าวจากต่างประเทศ",
            r"ข่าวทั่วโลก",
            r"ข่าวเมืองนอก",
            r"ข่าวโลก",
            r"international news",
            r"world news"
        ],
        "news": [
            r"(ข่าวด่วน|ข่าววันนี้|ข่าวเด่น|ข่าวล่าสุด|อัปเดตข่าว)",
            r"ข่าว(?:เกี่ยวกับ|ของ|ล่าสุด|ในหัวข้อ|เกี่ยวข้องกับ)\s.+",
            r"ขอสรุปข่าว",
            r"ช่วยอัปเดตข่าว",
            r"เล่าเหตุการณ์วันนี้"
        ],
        "tarot": [
            r"เปิดไพ่ทาโร่",
            r"เปิดไพ่\s*",
            r"ไพ่ยิปซี",
            r"ไพ่ทาโร่",
            r"ดูไพ่",
            r"ดูไพ่ยิปซี",
            r"ดูไพ่ทาโร่"
        ]
    }.items()
}

# ✅ ฟังก์ชันจับหัวข้อจากข้อความ
def match_topic(text: str) -> Optional[str]:
    text = text.strip()
    for topic, patterns in TOPIC_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                logger.info(f"✅ หัวข้อที่ match: '{topic}' ด้วย pattern '{pattern.pattern}'")
                return topic
    logger.info("❌ ไม่พบหัวข้อที่ match กับข้อความ")
    return None

# ✅ DEBUG: ยืนยันว่าไฟล์โหลดสำเร็จ
if __name__ == "__main__":
    test_texts = [
        "อยากรู้ราคาน้ำมันวันนี้",
        "ข่าวต่างประเทศวันนี้",
        "ขอรูปแมวตลก",
        "ช่วยตรวจหวยให้หน่อย",
        "สวัสดีตอนเช้า"
    ]
    for txt in test_texts:
        result = match_topic(txt)
        print(f"'{txt}' => หัวข้อที่ได้: {result}")
    print("✅ message_matcher.py โหลดสำเร็จ")
