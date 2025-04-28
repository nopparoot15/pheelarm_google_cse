import re
from typing import Optional

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

def is_list_item(line: str) -> bool:
    """เช็คว่าบรรทัดนี้น่าจะเป็น bullet หรือหัวข้อ list หรือเปล่า"""
    list_item_pattern = re.compile(r'^\s*(•|-|\d+\.)\s+')
    return bool(list_item_pattern.match(line.strip()))

def clean_output_text(text: str) -> str:
    text, saved_blocks = preserve_blocks(text)

    # ✅ ตอนต้น: เชื่อมเลขข้อกับข้อความ
    text = re.sub(r'(?m)^(\d+)\.\s*\n+(\S)', r'\1. \2', text)

    # ✅ ลบช่องว่างแปลก ๆ
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # ✅ แปลง heading เช่น ### หัวข้อ → **หัวข้อ**
    text = re.sub(r'^#{2,6}\s*(.+)', r'**\1**', text, flags=re.MULTILINE)

    # ✅ bullet: *, -, • → •
    text = re.sub(r'(?m)^[\*\-\u2022]\s+', '• ', text)

    # ✅ ลบ * เดี่ยว ๆ ที่ markdown พัง
    text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
    text = re.sub(r'\*\*(\s|$)', r'\1', text)
    text = re.sub(r'(^|\s)\*\*(?=\s)', r'\1', text)

    # ✅ ลิงก์ markdown: [text](url) → text <url>
    text = re.sub(r'$begin:math:display$([^$end:math:display$]+)\]$begin:math:text$(https?://[^$end:math:text$]+)\)', r'\1 <\2>', text)
    text = re.sub(r'(?<!<)(https?://\S+)(?!>)', r'<\1>', text)

    # ✅ ป้องกันการตัดบรรทัดมั่ว
    safe_starts = r'[\-\*\u2022#>\|0-9]|<:|:.*?:'
    safe_ends = r'[A-Za-z0-9ก-๙\.\!\?\)]'
    text = re.sub(fr'(?<!{safe_ends})\n(?!{safe_starts}|\n)', ' ', text)

    # ✅ แบ่งข้อความใหม่ (~40 คำต่อย่อหน้า)
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

    # ✅ คืน block กลับก่อน
    text = restore_blocks(new_text, saved_blocks)

    # ✅ เชื่อมเลขข้อหลัง restore อีกที
    text = re.sub(r'(?m)^(\d+)\.\s*\n+(\S)', r'\1. \2', text)

    # ✅ จัดรูปแบบ list ให้ไม่มั่ว
    lines = text.splitlines()
    new_lines = []
    inside_list = False

    for line in lines:
        stripped = line.strip()

        if is_list_item(stripped):
            if inside_list:
                new_lines.append(stripped)
            else:
                inside_list = True
                new_lines.append(stripped)
        elif stripped:
            if inside_list:
                # จบ list → เว้นบรรทัด
                new_lines.append('')
                inside_list = False
            new_lines.append(stripped)
        else:
            new_lines.append('')

    return '\n'.join(new_lines).strip()

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