THAI_TO_ENGLISH_CITY = {
    "กรุงเทพ": "Bangkok",
    "กรุงเทพฯ": "Bangkok",
    "กรุงเทพมหานคร": "Bangkok",
    "เชียงใหม่": "Chiang Mai",
    "ขอนแก่น": "Khon Kaen",
    "ชลบุรี": "Chonburi",
    "นครราชสีมา": "Nakhon Ratchasima",
    "โคราช": "Nakhon Ratchasima",
    "พิษณุโลก": "Phitsanulok",
    "เชียงราย": "Chiang Rai",
    "อุดรธานี": "Udon Thani",
    "อุบลราชธานี": "Ubon Ratchathani",
    "นครศรีธรรมราช": "Nakhon Si Thammarat",
    "สุราษฎร์ธานี": "Surat Thani",
    "ภูเก็ต": "Phuket",
    "หาดใหญ่": "Hat Yai",
    "พัทยา": "Pattaya",
    # เพิ่มจังหวัดอื่น ๆ ได้ตามต้องการ
}


def convert_thai_to_english_city(city_name: str) -> str:
    city_name = city_name.strip()
    return THAI_TO_ENGLISH_CITY.get(city_name, city_name)
