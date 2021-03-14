import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import ID
from discord.utils import get
import sqlite3
import os
from pathlib import Path

load_dotenv(verbose=True)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
COBot = commands.Bot(command_prefix="!CO!", intents=intents)
token = os.getenv("COBOT_TOKEN")


# Database
def create_db():
    COcursor.execute(
        "CREATE TABLE IF NOT EXISTS registerTable (username TEXT, ad TEXT, soyad TEXT, email TEXT, telefon INTEGER )")
    COdb.commit()


def add_value(username, dataset):
    COcursor.execute("INSERT INTO registerTable VALUES(?,?,?,?,?)",
                     (username, dataset[0], dataset[1], dataset[2], dataset[3]))
    COdb.commit()


def sql_execute(execute_text):
    COcursor.execute(execute_text)
    COdb.commit()


FILENAME = "bootcampregisterdata.db"
dataList = ["Ad: ", "Soyad: ", "Email: ", "Telefon No (isteğe bağlı): "]

COdb = sqlite3.connect(FILENAME)

COcursor = COdb.cursor()


@COBot.event
async def on_ready():
    create_db()
    await COBot.change_presence(status=discord.Status.online, activity=discord.Game("github.com/buraaksenturk"))
    print("""
    ########################################
    #                                      #
    #    COBot DeepLab için diriliyor...   #
    #                                      #
    ########################################
    """)


# Register
@COBot.event
async def on_message(message):
    if message.author != COBot.user:
        await COBot.process_commands(message)

        channel = message.channel
        register_page = ID.registerPageID(message.guild.id)

        if channel.id == register_page:
            dataset = list()
            try:
                dataset = [co.split(":")[1].strip() for co in message.content.split("\n")]
                if len(dataset) != 4:
                    raise Exception
            except:
                await message.delete()
                error_message = f"{message.author.mention} Bir hata oluştu kopyala yapıştır yapar mısın? \N{THINKING FACE}"
                await channel.send(error_message, delete_after=10)
                if len(dataset) == 5:
                    await channel.send(
                        "Hatalı işlem yapıldı. Bir satır fazla yazmış olabilir misin? \N{THINKING FACE}",
                        delete_after=10)
                if len(dataset) == 1:
                    await channel.send("Satır satır yazmaya ne dersin \N{THINKING FACE}", delete_after=10)
                return

            username = f"{message.author.name}#{message.author.discriminator}"

            data_zip = '\n'.join([c + o for c, o in zip(dataList, dataset)])

            confirm_message_text = f"""{message.author.mention} Bilgilerini onaylıyorsan 10 saniye içerisinde 👍 tepkisini verebilirsin"""

            CO_bot_message = await channel.send(confirm_message_text, delete_after=10)
            await CO_bot_message.add_reaction("\N{THUMBS UP SIGN}")

            def check(reaction, user):
                return user == message.author and str(reaction.emoji) == '👍'

            try:
                await COBot.wait_for('reaction_add', timeout=10.0, check=check)
            except asyncio.TimeoutError:
                await channel.send('Zaman aşımına uğradı', delete_after=10)
            else:
                await CO_bot_message.delete()

                data_channel = COBot.get_channel(ID.dataPageID(message.guild.id))
                await data_channel.send(
                    f"{username} {message.author.mention} Sunucuya kayıt oldu!\nKullanıcı bilgileri:\n{data_zip}")
                role = get(message.author.guild.roles, name="Member")
                await message.author.add_roles(role)
                await channel.send(f'{message.author.mention} Kayıt başarılı!', delete_after=10)
                await message.author.edit(nick=dataset[0] + " " + dataset[1])
                add_value(username, dataset)
            await message.delete()


# Social
class Social:
    INSTAGRAM = 'https://instagram.com/'
    TWITTER = 'https://twitter.com/'
    LINKEDIN = 'https://www.linkedin.com/in/'


all_socialmedia = {
    'INSTAGRAM': 'burak.senturkkk',
    'TWITTER': 'burak_senturkk',
    'LINKEDIN': 'buraaksenturk'
}

ROOM = 0


@COBot.command()
@commands.has_role("Management")
async def socialpush(ctx, room: discord.TextChannel):
    global ROOM
    ROOM = room
    social_media_push.start()


@COBot.command()
@commands.has_role("Management")
async def socialpushstop(ctx, room: discord.TextChannel):
    global ROOM
    ROOM = room
    social_media_push.stop()


def getSocials() -> str:
    return f"""
{Social.INSTAGRAM}{all_socialmedia.get('INSTAGRAM')}
{Social.TWITTER}{all_socialmedia.get('TWITTER')}
{Social.LINKEDIN}{all_socialmedia.get('LINKEDIN')}
    """


@tasks.loop(minutes=1)
@commands.has_role("Management")
async def social_media_push():
    await ROOM.send(getSocials())


@COBot.command()
@commands.has_role("Management")
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


# SQL Query
@COBot.command()
@commands.has_role("Management")
async def sqlquery(ctx):
    query = COcursor.execute("SELECT * FROM registerTable")
    query_fetch = query.fetchall()
    await ctx.send(query_fetch)


# Help
COBot.remove_command("help")


@COBot.group(invoke_without_command=True)
@commands.has_role("Management")
async def help(ctx):
    cohelp = discord.Embed(title="COBot Help Komutu",
                           description="Komutlar hakkında daha detaylı bilgi için !CO!help <komut ismi> kullanın!",
                           color=ctx.author.color)
    cohelp.add_field(name="Social Media",
                     value="Daha detaylı bilgi almak için -> <!CO!help socialmediahelp> komutunu kullanabilirsiniz.")
    cohelp.add_field(name="Clear",
                     value="Daha detaylı bilgi almak için -> <!CO!help clearhelp> komutunu kullanabilirsiniz.")
    cohelp.add_field(name="SQL Sorgu",
                     value="Daha detaylı bilgi almak için -> <!CO!help sqlqueryhelp> komutunu kullanabilirsiniz.")
    cohelp.set_image(url='https://cdn.discordapp.com/avatars/819326992222650469/c0e018065f542566a929a80dd176c079.png')

    await ctx.send(embed=cohelp)


@help.command()
@commands.has_role("Management")
async def socialmediahelp(ctx):
    cohelp = discord.Embed(title="Social Media",
                           description="Sosyal medya paylaşımı yapmak için kullanılacak olan komutlar.",
                           color=ctx.author.color)
    cohelp.add_field(name="Social Push",
                     value="Paylaşımı başlatmak için kullanılacak olan komut -> !CO!socialpush #kanalismi")
    cohelp.add_field(name="Social Push Stop",
                     value="Paylaşımı sonlandırmak için kullanılacak olan komut (kanalismi kısmına paylaşımı başlattığımız kanalın ismi yazılacak) -> !CO!socialpushstop #kanalismi")
    cohelp.set_image(url='https://cdn.discordapp.com/avatars/819326992222650469/c0e018065f542566a929a80dd176c079.png')
    await ctx.send(embed=cohelp)


@help.command()
@commands.has_role("Management")
async def clearhelp(ctx):
    cohelp = discord.Embed(title="Clear",
                           description="Sayfaya yazılan yazıları temizleme işlemidir.",
                           color=ctx.author.color)
    cohelp.add_field(name="Clear",
                     value="Mesajları silmek için kullanılan komuttur.(Sayı girmezseniz manuel olarak 5 mesajı siler) -> !CO!clear silmekistediğiniz sayı")
    cohelp.set_image(url='https://cdn.discordapp.com/avatars/819326992222650469/c0e018065f542566a929a80dd176c079.png')
    await ctx.send(embed=cohelp)


@help.command()
@commands.has_role("Management")
async def sqlqueryhelp(ctx):
    cohelp = discord.Embed(title="SQL Sorgu",
                           description="SQLite veritabanına alınan verileri listelemeye yarar.",
                           color=ctx.author.color)
    cohelp.add_field(name="SQL Sorgu",
                     value="SQLite veritabanına alınan verileri listelemeye yarar. -> !CO!sqlquery")
    cohelp.set_image(url='https://cdn.discordapp.com/avatars/819326992222650469/c0e018065f542566a929a80dd176c079.png')
    await ctx.send(embed=cohelp)


COBot.run(token)
