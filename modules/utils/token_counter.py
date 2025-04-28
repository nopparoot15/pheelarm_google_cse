import tiktoken

# นับจำนวน token ที่ใช้ใน messages list
def count_tokens(messages: list, model: str = "gpt-4o-mini") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # fallback encoding

    tokens_per_message = 3  # แต่ละ message มี overhead ประมาณ 3 token
    tokens_per_name = 1     # ถ้ามี name= ใน message ต้องบวกเพิ่ม

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # เพิ่ม system prompt ตรง start / end
    return num_tokens