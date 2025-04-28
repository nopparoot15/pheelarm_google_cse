import discord

async def send_message_to_channel(bot: discord.Client, channel_id: int, message: str):
    """
    ส่งข้อความไปยังห้อง Discord โดยรับ bot จากภายนอก (ไม่ import main)
    """
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(message)
    except Exception as e:
        print(f"[ERROR] ไม่สามารถส่งข้อความไปยัง Discord Channel: {e}")
