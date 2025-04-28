import httpx

async def get_lottery_results() -> str:
    url = "https://lotto.api.rayriffy.com/latest"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()["response"]

            date_text = data.get("date", "ไม่ทราบวันที่")
            prize1 = next((p["number"][0] for p in data["prizes"] if p["id"] == "prizeFirst"), "ไม่ทราบ")
            last2 = next((r["number"][0] for r in data["runningNumbers"] if r["id"] == "runningNumberBackTwo"), "ไม่ทราบ")
            front3 = next((r["number"] for r in data["runningNumbers"] if r["id"] == "runningNumberFrontThree"), [])
            last3 = next((r["number"] for r in data["runningNumbers"] if r["id"] == "runningNumberBackThree"), [])

            return (
                f"📅 งวดวันที่: {date_text}\n"
                f"🏆 รางวัลที่ 1: {prize1}\n"
                f"🔢 เลขท้าย 2 ตัว: {last2}\n"
                f"🔹 เลขหน้า 3 ตัว: {', '.join(front3) if front3 else 'ไม่ทราบ'}\n"
                f"🔸 เลขท้าย 3 ตัว: {', '.join(last3) if last3 else 'ไม่ทราบ'}"
            )
    except Exception as e:
        return f"❌ พี่หลามดึงผลหวยไม่ได้ตอนนี้ ลองใหม่อีกทีนะ ({e})"
