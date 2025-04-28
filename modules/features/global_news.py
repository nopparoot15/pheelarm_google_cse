import httpx
from bs4 import BeautifulSoup
from modules.nlp.openai_utils import summarize_with_gpt

async def get_global_news(limit: int = 3) -> str:
    """
    ดึงข่าวต่างประเทศจาก Google News RSS และสรุปด้วย GPT พร้อมลิงก์แบบย่อ
    """
    url = "https://news.google.com/rss/search?q=ข่าวต่างประเทศ&hl=th&gl=TH&ceid=TH:th"

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "xml")

            items = soup.find_all("item", limit=limit)
            if not items:
                return "❌ ไม่พบข่าวต่างประเทศในตอนนี้"

            summarized_news = []

            for item in items:
                title = item.title.text.strip()
                link = item.link.text.strip() if item.link else ""
                raw_desc = item.description.text if item.description else ""
                clean_desc = BeautifulSoup(raw_desc, "html.parser").get_text()

                # รวมหัวข้อและเนื้อหาข่าวเพื่อสรุป
                full_text = f"{title}\n{clean_desc}"
                summary = await summarize_with_gpt(full_text)

                news_block = f"🌍 {summary}"
                if link:
                    news_block += f"\n🔗 [อ่านต่อ](<{link}>)"

                summarized_news.append(news_block)

            return "🌐 ข่าวต่างประเทศเด่นวันนี้:\n\n" + "\n\n".join(summarized_news)

    except Exception as e:
        return f"❌ พี่หลามดึงข่าวต่างประเทศไม่ได้เลย ({e})"
