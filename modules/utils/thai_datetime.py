from datetime import datetime
import pytz
from redis.asyncio import Redis

# แปลงชื่อวันและเดือนเป็นภาษาไทย
thai_days = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
thai_months = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def format_thai_datetime(dt: datetime) -> str:
    """ แปลง datetime เป็นข้อความภาษาไทย """
    day_name = thai_days[dt.weekday()]
    day = dt.day
    month = thai_months[dt.month]
    year = dt.year + 543  # แปลงเป็น พ.ศ.
    time_str = dt.strftime("%H:%M")
    return f"{day_name}ที่ {day} {month} {year} เวลา {time_str} น."

def get_thai_datetime_now() -> str:
    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)
    return format_thai_datetime(now)

async def get_thai_datetime_by_user(redis_instance: Redis, user_id: int) -> str:
    """ คืนค่าเวลาตาม timezone ของผู้ใช้ (ถ้าไม่กำหนดจะใช้ Asia/Bangkok) """
    zone = await redis_instance.get(f"timezone:{user_id}") or "Asia/Bangkok"
    tz = pytz.timezone(zone)
    now = datetime.now(tz)
    return format_thai_datetime(now)
