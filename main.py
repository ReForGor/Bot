import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
from dotenv import load_dotenv
from myserver import server_on
import yt_dlp
import os
import asyncio

def load_opus():
    if not discord.opus.is_loaded():
        possible_paths = ["/usr/lib/libopus.so", "/usr/lib/x86_64-linux-gnu/libopus.so"]
        for path in possible_paths:
            try:
                discord.opus.load_opus(path)
                print(f"✅ โหลด Opus สำเร็จจาก {path}")
                return
            except Exception as e:
                continue
        print("❌ ไม่สามารถโหลด Opus ได้: ตรวจสอบว่าติดตั้ง `libopus-dev` แล้ว")

load_opus()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
FFMPEG_PATH = "ffmpeg"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ บอท {bot.user} ออนไลน์และซิงค์คำสั่งเรียบร้อยแล้ว!")

@tree.command(name="ping", description="เช็คความเร็วของบอท")
async def slash_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Latency: {latency}ms", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency}ms")

@tree.command(name="info", description="แสดงข้อมูลเซิร์ฟเวอร์")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"ข้อมูลของ {guild.name}", color=discord.Color.blue())
    embed.add_field(name="📌 ชื่อเซิร์ฟเวอร์", value=guild.name, inline=False)
    embed.add_field(name="👑 เจ้าของ", value=guild.owner, inline=False)
    embed.add_field(name="👥 สมาชิกทั้งหมด", value=guild.member_count, inline=False)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await interaction.response.send_message(embed=embed)

@bot.command()
async def info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"ข้อมูลของ {guild.name}", color=discord.Color.blue())
    embed.add_field(name="📌 ชื่อเซิร์ฟเวอร์", value=guild.name, inline=False)
    embed.add_field(name="👑 เจ้าของ", value=guild.owner, inline=False)
    embed.add_field(name="👥 สมาชิกทั้งหมด", value=guild.member_count, inline=False)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await ctx.send(embed=embed)

@bot.command()
async def sync(ctx):
    await tree.sync()
    await ctx.send("✅ ซิงค์คำสั่ง Slash Commands สำเร็จแล้ว!")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"🔊 เข้าห้อง {channel.name} แล้ว!")
    else:
        await ctx.send("❌ คุณต้องอยู่ในห้องเสียงก่อน!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ออกจากห้องเสียงแล้ว!")
    else:
        await ctx.send("❌ บอทยังไม่ได้อยู่ในห้องเสียง!")

@bot.command()
async def play(ctx, url: str):
    if not discord.opus.is_loaded():
        await ctx.send("❌ ไม่พบ Opus! โปรดตรวจสอบว่า Opus ถูกติดตั้งแล้ว")
        return

    if not ctx.voice_client:
        await ctx.invoke(join)
    
    await ctx.send(f"🎵 กำลังดาวน์โหลดเพลงจาก: {url}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.mp3'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    
    source = FFmpegPCMAudio("song.mp3")
    voice_client.play(source)
    
    await ctx.send(f"🎶 กำลังเล่น: {info['title']}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ หยุดเพลงแล้ว!")
    else:
        await ctx.send("❌ ไม่มีเพลงที่กำลังเล่นอยู่!")

server_on()
bot.run(TOKEN)
