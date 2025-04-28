import httpx

CURRENCIES = ["USD", "EUR", "JPY", "CNY"]

async def get_exchange_rate() -> str:
    url = "https://open.er-api.com/v6/latest/THB"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()

            if data.get("result") != "success":
                return "❌ พี่หลามดึงอัตราแลกเปลี่ยนไม่ได้"

            rates = data.get("rates", {})
            result = []
            for cur in CURRENCIES:
                rate = rates.get(cur)
                if rate:
                    result.append(f"💱 1 THB ≈ {rate:.2f} {cur}")

            return "📊 อัตราแลกเปลี่ยนวันนี้ (THB):\n" + "\n".join(result)

    except Exception as e:
        return f"❌ พี่หลามดึงอัตราแลกเปลี่ยนไม่ได้ ({e})"
