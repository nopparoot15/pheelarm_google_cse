import httpx
from datetime import datetime
import pytz

# ตัวแปลงวันภาษาอังกฤษเป็นไทย
thai_days = {
    "Monday": "จันทร์",
    "Tuesday": "อังคาร",
    "Wednesday": "พุธ",
    "Thursday": "พฤหัสบดี",
    "Friday": "ศุกร์",
    "Saturday": "เสาร์",
    "Sunday": "อาทิตย์"
}

thai_months = {
    "January": "มกราคม",
    "February": "กุมภาพันธ์",
    "March": "มีนาคม",
    "April": "เมษายน",
    "May": "พฤษภาคม",
    "June": "มิถุนายน",
    "July": "กรกฎาคม",
    "August": "สิงหาคม",
    "September": "กันยายน",
    "October": "ตุลาคม",
    "November": "พฤศจิกายน",
    "December": "ธันวาคม"
}

async def get_gold_price_today() -> str:
    url = "https://api.chnwt.dev/thai-gold-api/latest"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            result = data.get("response", {})
            date_text = result.get("date", "ไม่ทราบวันที่")
            update_time = result.get("update_time", "ไม่ทราบเวลา")
            gold_bar = result.get("price", {}).get("gold_bar", {})
            sell_price = gold_bar.get("sell", "ไม่ทราบ")
            buy_price = gold_bar.get("buy", "ไม่ทราบ")

            # วันที่ภาษาไทย
            bangkok_tz = pytz.timezone("Asia/Bangkok")
            today = datetime.now(bangkok_tz)
            
            day_thai = thai_days[today.strftime("%A")]
            month_thai = thai_months[today.strftime("%B")]
            thai_date = today.strftime(f"{day_thai}ที่ %-d {month_thai} %Y")

            return (
                f"📅 วัน{thai_date}\n"
                f"🕒 อัปเดตเมื่อ: {update_time} ({date_text})\n"
                f"🏷️ ราคาทองคำแท่ง 96.5%\n"
                f"💰 รับซื้อ: {buy_price} บาท\n"
                f"💸 ขายออก: {sell_price} บาท"
            )
    except Exception as e:
        return f"❌ พี่หลามดึงราคาทองไม่ได้ตอนนี้ ลองใหม่อีกทีนะ ({e})"
