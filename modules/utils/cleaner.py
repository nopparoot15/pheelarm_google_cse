import re
from typing import Optional

search_tool = {
    "type": "function",
    "function": {
        "name": "search_google",
        "description": "ค้นหาข้อมูลจาก Google",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "คำค้นหาที่ต้องการค้นจาก Google"
                }
            },
            "required": ["query"]
        }
    }
}

def preserve_blocks(raw: str) -> tuple[str, dict]:
    code_blocks = {}

    def replacer(match):
        key = f"__BLOCK_{len(code_blocks)}__"
        code_blocks[key] = match.group(0)
        return key

    raw = re.sub(r"```.*?```", replacer, raw, flags=re.DOTALL)
    raw = re.sub(r"`[^`\n]+`", replacer, raw)
    raw = re.sub(r"^\s*\|.+\|.*$", replacer, raw, flags=re.MULTILINE)

    return raw, code_blocks

def restore_blocks(text: str, blocks: dict) -> str:
    for key, value in blocks.items():
        text = text.replace(key, value)
    return text

def clean_output_text(text: str) -> str:
    text, saved_blocks = preserve_blocks(text)

    # ✅ เชื่อมเลขข้อกับข้อความที่โดนเว้นบรรทัด
    text = re.sub(r'(?m)^(\d+)\.\s*\n+(\S)', r'\1. \2', text)
    text = re.sub(r'(?m)^(\d+)\.\s*$', r'\1.\n', text)

    # ✅ ลบช่องว่างท้ายบรรทัด
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # ✅ Headings เช่น ### หัวข้อ → **หัวข้อ**
    text = re.sub(r'^#{2,6}\s*(.+)', r'**\1**', text, flags=re.MULTILINE)

    # ✅ Bullet point: *, -, • → • 
    text = re.sub(r'(?m)^[\*\-\u2022]\s+', '• ', text)

    # ✅ ลบ * หรือ ** เดี่ยว ๆ ที่พัง
    text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
    text = re.sub(r'\*\*(\s|$)', r'\1', text)
    text = re.sub(r'(^|\s)\*\*(?=\s)', r'\1', text)

    # ✅ แก้ลิงก์ markdown → text <url>
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'\1 <\2>', text)
    text = re.sub(r'(?<!<)(https?://\S+)(?!>)', r'<\1>', text)

    # ✅ ตัดบรรทัดไม่ให้ตัดมั่ว
    safe_starts = r'[\-\*\u2022#>\|0-9]|<:|:.*?:'
    safe_ends = r'[A-Za-z0-9ก-๙\.\!\?\)]'
    text = re.sub(fr'(?<!{safe_ends})\n(?!{safe_starts}|\n)', ' ', text)

    # ✅ เว้นบรรทัดหลังหัวข้อ 1. 2. 3. แต่ไม่เว้น 2.5, 3.14
    text = re.sub(r'(?<=\n)(\d+)\.\s+(?=[^\d\s])', r'\1.\n\n', text)

    # ✅ แบ่งย่อหน้า (~40 คำ)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    new_text, current_length = '', 0
    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > 40:
            new_text = new_text.strip() + "\n\n" + sentence.strip() + " "
            current_length = sentence_length
        else:
            new_text += sentence.strip() + " "
            current_length += sentence_length

    text = restore_blocks(new_text, saved_blocks)

    # ✅ เว้นบรรทัดหลังรายการ bullet (•)
    lines = text.splitlines()
    final_lines = []
    inside_list = False

    for line in lines:
        stripped = line.strip()
        if re.match(r'^\d+\.', stripped) or stripped.startswith('•'):
            inside_list = True
            final_lines.append(stripped)
        elif stripped:
            if inside_list:
                final_lines.append('')
                inside_list = False
            final_lines.append(stripped)
        else:
            final_lines.append('')

    return '\n'.join(final_lines).strip()

def clean_url(url: Optional[str]) -> str:
    if not isinstance(url, str):
        return ""
    return re.sub(r'[\n\r]', '', url)

def format_response_markdown(text: str) -> str:
    lines = text.split("\n")
    formatted_lines = []

    bullet_pattern = re.compile(r'^[•\-\*\u2022]\s*')
    for line in lines:
        line = line.strip()
        if bullet_pattern.match(line):
            content = bullet_pattern.sub('', line).strip()
            formatted_lines.append(f"• {content}")
        else:
            formatted_lines.append(line)

    formatted_text = "\n".join(formatted_lines)
    formatted_text = re.sub(r'\*\*(.+?)\*\*', r'**\1**', formatted_text)

    return formatted_text.strip()
