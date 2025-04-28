import httpx
from bs4 import BeautifulSoup
from modules.nlp.openai_utils import summarize_with_gpt

async def get_daily_news(limit: int = 3) -> str:
    """
    ดึงข่าวเด่นในประเทศจาก Google News RSS (TH) และสรุปด้วย GPT พร้อมลิงก์แบบย่อ
    """
    url = "https://news.google.com/rss?hl=th&gl=TH&ceid=TH:th"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "xml")

            items = soup.find_all("item", limit=limit)
            if not items:
                return "❌ ไม่พบข่าวในตอนนี้"

            summarized_news = []

            for item in items:
                title = item.title.text.strip()
                link = item.link.text.strip() if item.link else ""
                raw_desc = item.description.text if item.description else ""
                clean_desc = BeautifulSoup(raw_desc, "html.parser").get_text()

                # สร้างเนื้อหาที่จะส่งไปให้ GPT
                full_text = f"{title}\n{clean_desc}"
                summary = await summarize_with_gpt(full_text)

                news_block = f"📰 {summary}"
                if link:
                    news_block += f"\n🔗 [อ่านต่อ](<{link}>)"

                summarized_news.append(news_block)

            return "🗞️ ข่าวเด่นประจำวัน:\n\n" + "\n\n".join(summarized_news)

    except Exception as e:
        return f"❌ พี่หลามดึงข่าวไม่ได้ ({e})"
