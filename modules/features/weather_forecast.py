import httpx
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

async def get_weather(city: str) -> str:
    if not API_KEY:
        return "❌ ยังไม่ได้ตั้งค่า API key ของ OpenWeatherMap"

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric&lang=th"
    )
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()

            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]

            return (
                f"📍 สภาพอากาศวันนี้ที่ {city.title()}\n"
                f"🌤️ {weather}\n"
                f"🌡️ อุณหภูมิ: {temp}°C\n"
                f"💧 ความชื้น: {humidity}%\n"
                f"💨 ลม: {wind} m/s"
            )

    except Exception as e:
        return f"❌ พี่หลามดึงพยากรณ์อากาศไม่ได้ ({e})"
