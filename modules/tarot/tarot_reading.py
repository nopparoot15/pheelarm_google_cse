import random
from modules.tarot.tarot_meanings_by_topic import TAROT_MEANINGS_BY_TOPIC
from modules.nlp.openai_utils import summarize_tarot_reading

def draw_multiple_cards(n=3):
    all_card_names = list(TAROT_MEANINGS_BY_TOPIC.keys())
    selected_names = random.sample(all_card_names, k=n)
    return [(name, random.choice([True, False])) for name in selected_names]

async def draw_cards_and_interpret_by_topic(topic: str) -> str:
    cards = draw_multiple_cards(3)

    card_blocks = []
    gpt_input_lines = []

    for name, is_reversed in cards:
        card_data = TAROT_MEANINGS_BY_TOPIC.get(name, {})
        meaning = card_data.get(topic, "❌ ไม่พบคำทำนายในหัวข้อนี้")
        direction = "กลับหัว" if is_reversed else "ปกติ"

        card_blocks.append(
            f"🔹 **{name}** ({direction})\n💬 _{meaning}_"
        )
        gpt_input_lines.append(f"{name} ({direction}): {meaning}")

    reading_text = "\n".join(gpt_input_lines)
    summary = await summarize_tarot_reading(reading_text, topic)

    return (
        f"🔮 **คำทำนายเรื่อง {topic} ของคุณ:**\n\n"
        f"🃏 ไพ่ที่คุณได้:\n\n" + "\n\n".join(card_blocks) + "\n\n"
        f"📝 **สรุปคำทำนาย:**\n{summary}"
    )
