import httpx
import json
from datetime import datetime
import pytz

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

async def get_oil_price_today() -> str:
    url = "https://oil-price.bangchak.co.th/ApiOilPrice2/th"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()

            if not isinstance(data, list) or not data:
                return "❌ โครงสร้างข้อมูลผิดปกติ"

            oil_list_raw = data[0].get("OilList")
            if not oil_list_raw:
                return "❌ ไม่พบรายการราคาน้ำมัน"

            oil_list = json.loads(oil_list_raw)

            target_names = {
                "แก๊สโซฮอล์ 95 S EVO": "แก๊สโซฮอล์ 95",
                "แก๊สโซฮอล์ 91 S EVO": "แก๊สโซฮอล์ 91",
                "ไฮดีเซล S": "ดีเซล"
            }

            result = []
            for item in oil_list:
                raw_name = item.get("OilName", "")
                if raw_name in target_names:
                    display_name = target_names[raw_name]
                    price = item.get("PriceToday", "-")
                    result.append(f"⛽ {display_name}: {price} บาท/ลิตร")

            if not result:
                return "❌ ไม่พบข้อมูลราคาน้ำมันที่ต้องการ"

            today = datetime.now(pytz.timezone("Asia/Bangkok"))
            day_thai = thai_days[today.strftime("%A")]
            month_thai = thai_months[today.strftime("%B")]
            thai_date = today.strftime(f"วัน{day_thai}ที่ %-d {month_thai} %Y")

            return f"📅 ราคาน้ำมันประจำ{thai_date}\n" + "\n".join(result)

    except Exception as e:
        return f"❌ พี่หลามดึงราคาน้ำมันไม่ได้ตอนนี้ ลองใหม่อีกทีนะ ({e})"
