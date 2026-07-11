import discord
from discord.ext import commands
import os

# Cấu hình intents để bot đọc được tin nhắn
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ID Kênh Admin duyệt bài (THAY ID CỦA BẠN VÀO ĐÂY)
ADMIN_CHANNEL_ID = 1525386498739015800  

MP_RULES = {
    "easy": 5, "normal": 10, "hard": 25, "harder": 50, "insane": 100,
    "easy_demon": 250, "medium_demon": 500, "hard_demon": 1000, 
    "insane_demon": 5000, "extreme_demon": 10000
}

class DenyModal(discord.ui.Modal, title='Lý do từ chối'):
    reason = discord.ui.TextInput(label="Nhập lý do tại đây", style=discord.TextStyle.paragraph)
    def __init__(self, user, cap_do):
        super().__init__()
        self.user = user
        self.cap_do = cap_do

    async def on_submit(self, interaction: discord.Interaction):
        await self.user.send(f"❌ Minh chứng `{self.cap_do.upper()}` của bạn bị từ chối.\nLý do: {self.reason}")
        await interaction.response.send_message(f"✅ Đã gửi lý do từ chối cho {self.user.name}.")

class ReviewView(discord.ui.View):
    def __init__(self, user, cap_do, points):
        super().__init__(timeout=None)
        self.user = user
        self.cap_do = cap_do
        self.points = points

    @discord.ui.button(label="✅ Duyệt", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ Đã cộng {self.points} MP cho {self.user.name}")
        await self.user.send(f"🎉 Chúc mừng! Minh chứng `{self.cap_do.upper()}` của bạn đã được duyệt (+{self.points} MP).")
        self.disable_all_items()
        await interaction.message.edit(view=self)

    @discord.ui.button(label="❌ Từ chối", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DenyModal(self.user, self.cap_do))
        self.disable_all_items()
        await interaction.message.edit(view=self)

@bot.event
async def on_ready():
    print(f"Bot đã sẵn sàng: {bot.user}")

@bot.command()
async def duyet(ctx, cap_do: str):
    cap_do = cap_do.lower()
    if cap_do not in MP_RULES:
        return await ctx.send("❌ Cấp độ không hợp lệ!")
    if not ctx.message.attachments:
        return await ctx.send("❌ Vui lòng đính kèm ảnh!")

    admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
    embed = discord.Embed(title="📸 KIỂM DUYỆT PROOF", color=discord.Color.orange())
    embed.add_field(name="Người chơi", value=ctx.author.mention)
    embed.add_field(name="Cấp độ", value=cap_do.upper())
    embed.add_field(name="MP nhận", value=f"{MP_RULES[cap_do]} MP")
    embed.set_image(url=ctx.message.attachments[0].url)

    await admin_channel.send(embed=embed, view=ReviewView(ctx.author, cap_do, MP_RULES[cap_do]))
    await ctx.send("✅ Đã gửi bài của bạn tới Admin duyệt!")

# Chạy bot bằng Token từ biến môi trường của Render
token = os.environ.get('TOKEN')
bot.run(token)

