# 🤖 พี่หลาม – Discord Bot ภาษาไทยสุดฉลาด

**พี่หลาม** คือ Discord Bot ภาษาไทยที่สามารถโต้ตอบกับผู้ใช้ได้อย่างชาญฉลาด โดยใช้ GPT, ระบบจำข้อความ, วิเคราะห์โทนเสียง และทำนายไพ่ยิปซีแบบแม่นยำ พร้อมความสามารถรายงานข่าว พยากรณ์อากาศ ราคาทอง ฯลฯ

---

## 🚀 ฟีเจอร์เด่น
- 💬 โต้ตอบด้วย GPT + ความจำข้อความ (Context Memory)
- 🧠 วิเคราะห์เจตนา (Intent Detection) ด้วย GPT
- 🗣️ วิเคราะห์โทนเสียง (Tone Detection) เช่น soft, troll, savage
- 🌦 ข่าว, พยากรณ์อากาศ, ราคาทอง, ตรวจหวย, อัตราแลกเปลี่ยน
- 🔮 ทำนายดวงด้วยไพ่ยิปซี พร้อมความหมายแยกตามหัวข้อ
- 🔍 ค้นหาข้อมูลผ่าน Google / Search Tools

---

## 📁 โครงสร้างโปรเจกต์

```bash
pheelarm-main/
├── main.py
├── requirements.txt
├── README.md
├── modules/
│   ├── core/              # config, openai client, logger
│   ├── memory/            # ระบบจำข้อความ (Redis)
│   ├── nlp/               # smart_reply, intent, message matcher
│   ├── personality/       # tone_manager
│   ├── features/          # ข่าว, ทอง, อากาศ ฯลฯ
│   ├── utils/             # ฟังก์ชันเสริม
│   └── tarot/             # ไพ่ยิปซี
```

---

## 📦 ติดตั้งไลบรารีที่ใช้

```bash
pip install -r requirements.txt
```

---

## ▶️ วิธีรันบอท

1. สร้างไฟล์ `.env` ที่ root:

```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_key
REDIS_URL=redis://localhost:6379
```

2. รันบอท:

```bash
python main.py
```

---

## ⚙️ ใช้ Docker? (กำลังมาเร็ว ๆ นี้)
สามารถรันได้ด้วย Docker + docker-compose พร้อม Redis, PostgreSQL

---

## 📞 ติดต่อผู้พัฒนา

Salty6ix
