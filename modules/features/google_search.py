import re
import httpx
import logging
from typing import Optional, List, Dict
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# ✅ ตรวจจับคำที่สื่อถึงสื่อ เช่น เพลง คลิป
def is_media_query(query: str) -> bool:
    return re.search(r"(เพลง|mv|คลิป|video|op|ed|opening|ending|ตัวอย่าง|trailer|แนะนำ|ดู)", query, re.IGNORECASE) is not None

# ✅ ตรวจสอบว่า URL เป็นลิงก์รูปภาพหรือไม่
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

def is_direct_image_link(url: str) -> bool:
    return any(url.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)

# ✅ สรุปผล Google แบบย่อหน้า พร้อมเว้นวรรค อ่านง่าย
def summarize_google_results(results: List[Dict], limit=3) -> str:
    summaries = []
    for i, item in enumerate(results[:limit], start=1):
        title = item.get("title", "").strip()
        snippet = item.get("snippet", "").strip()
        link = item.get("link", "").strip()

        if title and snippet and link:
            summaries.append(f"{i}. **{title}**\n{snippet}\n<{link}>\n")

    return "\n".join(summaries).strip()

# ✅ จัดผลลัพธ์จาก Google Search แบบลิงก์ล้วน
def format_google_results(results: List[Dict]) -> str:
    lines = ["📌 ผลลัพธ์จาก Google:"]
    for i, item in enumerate(results[:3], start=1):
        title = item.get("title", "").strip()[:60]
        link = item.get("link", "").strip()
        if title and link:
            lines.append(f"{i}. {title}\n<{link}>")
    return "\n".join(lines)

# ✅ ค้นหาข้อมูลจาก Google แล้วส่งกลับ list ของ dict
async def search_google(query: str, settings) -> List[Dict]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "q": query,
                    "key": settings.GOOGLE_API_KEY,
                    "cx": settings.GOOGLE_CSE_ID,
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("items", [])[:5]
    except httpx.RequestError as e:
        logger.error(f"เกิดข้อผิดพลาดใน Google Search API: {e}")
        return []

# ✅ ค้นหารูปภาพจาก Google
async def search_image(query: str, settings) -> Optional[str]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "q": query,
                    "searchType": "image",
                    "num": 5,
                    "key": settings.GOOGLE_API_KEY,
                    "cx": settings.GOOGLE_CSE_ID
                },
                timeout=10
            )
            response.raise_for_status()
            results = response.json().get("items", [])
            for result in results:
                link = result.get("link", "")
                if is_direct_image_link(link):
                    return link
    except httpx.RequestError as e:
        logger.error(f"เกิดข้อผิดพลาดในการค้นหารูปภาพ: {e}")
    return None
