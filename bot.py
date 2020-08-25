import discord
from discord.ext import commands
from discord.utils import get
import random
import youtube_dl
import os
import shutil

PREFIX = '!'
bot = commands.Bot(command_prefix = PREFIX)    # Провозглашаем переменную для бота с префиксом !
ROLE = ''
#bot.remove_command('help')

# ______________Events______________

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Я родился'))
    print('Bot is ready. Logged in as: ' + bot.user.name + '\n')
    
# Сообщение о подключении
@bot.event
async def on_member_join(member):
    print(f'{member} has joined a server.')
    channel = discord.utils.get(member.guild.channels)
    responses = [f'Дикий {member.mention} появился!',
                 f'Ура, {member.mention} теперь с нами!',
                 f'Привет, {member.mention}!',
                 f'Добро пожаловать, {member.mention}!',
                 f'{member.mention} уже здесь. Хотя? кто его звал?',
                 f'{member.mention} уже с нами! Хоть кто-то знает кто это?',
                 f'{member.mention} запрыгивает на сервер.',
                 f'Зашёл {member.mention} - тот самый чел, которому дали ссылку.',
                 f'{member.mention} присоединяется к вашей пати успешных в жизни людей.',
                 f'Рады встрече, {member.mention}. Но только если ты не дотер.',
                 f'Знакомьтесь, это {member.mention}!',
                 f'Рады тебя видеть, {member.mention}!']
    await channel.send(random.choice(responses))

# Сообщение о выходе.
@bot.event
async def on_member_remove(member):
    print(f'{member} has left a server.')
    channel = discord.utils.get(member.guild.channels)
    responses = [f'{member.mention} вышел из сервера.',
                 f'{member.mention} покидает нас.']
    await channel.send(random.choice(responses))

# ______________Commands______________

# ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

# join
@bot.command(aliases = ['j', 'joi'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f'[JOIN] The bot has connected to {channel}')

    await ctx.send(f'Зашёл в {channel}')

#leave
@bot.command(aliases = ['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)
    
    if voice and voice.is_connected():
        await voice.disconnect()
        print(f'[LEAVE] The bot has left {channel}')
        await ctx.send(f'Вышел из {channel}')
    else:
        print('[LEAVE] Bot was told to leave voice channel, but was not in one')
        await ctx.send('Не думаю, что я сейчас нахожусь в голосовом канале')
        
#play
@bot.command(aliases = ['p', 'pla'])
async def play(ctx, url: str):

    def check_queue():
        Queue_infile = os.path.isdir('./Queue')
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath('Queue'))
            lenght = len(os.listdir(DIR))
            still_q = lenght - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print('[PLAY] No more queued song(s)\n')
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath('Queue') + '\\' + first_file)
            if lenght != 0:
                print('[PLAY] Song done, playing next queued\n')
                print(f'[PLAY] Songs still in queue: {still_q}')
                song_there = os.path.isfile('song.mp3')
                if song_there:
                    os.remove('song.mp3')
                shutil.move(song_path, main_location)
                for file in os.listdir('./'):
                    if file.endswith('.mp3'):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print('[PLAY] No songs were queued before the ending of the last song\n')

    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
            queues.clear()
            print('[PLAY] Removed old song file')
    except PermissionError:
        print('[PLAY] Trying to delete song file, bit it is being played')
        await ctx.send('ОШИБКА: Трек играет')
        return

    Queue_infile = os.path.isdir('./Queue')
    try:
        Queue_folder = './Queue'
        if Queue_infile is True:
            print('[PLAY] Removed old Queue Folder')
            shutil.rmtree(Queue_folder)
    except:
        print('[PLAY] No old Queue folder')

    await ctx.send('Трек загружается, ждите...')

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format' : 'bestaudio/best',
        'quiet' : True,
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('[PLAY] Downloading audio now\n')
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            print(f'[PLAY] Renamed File: {file}\n')
            os.rename(file, 'song.mp3')

    voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    await ctx.send(f'Играю трек')

    print('playing\n')

#pause
@bot.command(aliases = ['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_playing():
        print('[PAUSE] Music paused')
        voice.pause()
        await ctx.send('Трек на паузе')
    else:
        print('[PAUSE] Music not playing falied pause')
        await ctx.send('Трек не играет, пауза невозможна')

#resume
@bot.command(aliases = ['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_paused():
        print('[RESUME] Resumed music')
        voice.resume()
        await ctx.send('Трек возобновился')
    else:
        print('[RESUME] Music is not paused')
        await ctx.send('Трек не стоит на паузе')
        
#stop
@bot.command(aliases = ['st', 'sto'])
async def stop(ctx):            

    voice = get(bot.voice_clients, guild = ctx.guild)

    queues.clear()

    queue_infile = os.path.isdir('./Queue')
    if queue_infile is True:
        shutil.rmtree('./Queue')

    if voice and voice.is_playing():
        print('[STOP] Music stopped')
        voice.stop()
        await ctx.send('Музыка прекратилась')
    else:
        print('[STOP] No music playing failed to stop')
        await ctx.send('Нет играющей музыки чтобы прекратить её')

#queue
queues = {}

@bot.command(aliases = ['q', 'que'])
async def queue(ctx, url: str): 
    Queue_infile = os.path.isdir('./Queue')
    if Queue_infile is False:
        os.mkdir('Queue')
    DIR = os.path.abspath(os.path.relpath('Queue'))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num
    
    queue_path = os.path.abspath(os.path.realpath('Queue') + f'\song{q_num}.%(ext)s')

    ydl_opts = {
        'format' : 'bestaudio/best',
        'quiet' : True,
        'outtmpl' : queue_path,
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('[QUEUE] Downloading audio now\n')
        ydl.download([url])
    await ctx.send('Добавляю песню ' + str(q_num) + ' в очередь')

    print('[QUEUE] Song added to queue')

#next
@bot.command(aliases = ['n', 'nex', 'skip', 'sk'])
async def next(ctx):            

    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_playing():
        print('[NEXT] Playing next song')
        voice.stop()
        await ctx.send('Следующий трек')
    else:
        print('[NEXT] No music playing failed to play next song')
        await ctx.send('Нет играющей музыки чтобы переключить её')

# шар предсказанний
@bot.command(aliases = ['шар', '8шар', '8ball', 'ball'])
async def _8ball(ctx, *, question):
    responses = ['Бесспорно.',
                 'Предрешено.',
                 'Никаких сомнений.',
                 'Определённо да.',
                 'Можешь быть уверен в этом.',
                 'Мне кажется - да.',
                 'Вероятнее всего.',
                 'Хорошие перспективы.',
                 'Знаки говорят - да.',
                 'Да.',
                 'Пока не ясно, попробуй снова.',
                 'Спроси позже.',
                 'Лучше не рассказывать.',
                 'Сейчас нельзя предсказать.',
                 'Сконцентрируйся и спроси опять.',
                 'Даже не думай.',
                 'Мой ответ - нет.',
                 'По моим данным - нет.',
                 'Перспективы не очень хорошие.',
                 'Весьма сомнительно.']
    await ctx.send(f'Вопрос: {question}\nОтвет: {random.choice(responses)}')

# Clear message
@bot.command()
@commands.has_permissions(administrator = True)
async def clear(ctx, amount = 1):
    await ctx.channel.purge(limit = amount + 1)

# Kick
@bot.command(aliases = ['кик'])
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, *, reason = None):
    await ctx.channel.purge(limit = 1)
    await member.kick(reason = reason)
    await ctx.send(f'{member.mention} был кикнут.')

# Ban
@bot.command(aliases = ['бан'])
@commands.has_permissions(administrator = True)
async def ban(ctx, member: discord.Member, *, reason = None):
    await ctx.channel.purge(limit = 1)
    await member.ban(reason = reason)
    await ctx.send(f'{member.mention} был забанен.')

# Unban
@bot.command(aliases = ['анбан'])
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member):
    await ctx.channel.purge(limit = 1)

    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user       #получаем Name#1234 без упоминания @
        await ctx.guild.unban(user)
        await ctx.send(f'{user.mention} был разбанен.')
        return

# Банан
@bot.command(aliases = ['банан'])
async def banan(ctx):
    cm = random.randint(3, 25)
    if cm < 7:
        reaction = ':clown:'
    elif cm < 12:
        reaction = ':joy:'
    elif cm < 20:
        reaction = ':smirk:'
    else:
        reaction = ':scream:'    
    await ctx.send('У {0.author.mention} банан {1} см {2}'.format(ctx, cm, reaction))

'''# Command help
@bot.command()
async def help(ctx):
    await ctx.channel.purge(limit = 1)
    emb = discord.Embed(title = 'Навигация по командам', 
                        colour = discord.Color.red())

    emb.add_field(name = '{}clear'.format(PREFIX),
                  value = 'Очистка чата.')
    emb.add_field(name = '{}kick'.format(PREFIX), 
                  value = 'Кикнуть участника.')
    emb.add_field(name = '{}ban'.format(PREFIX), 
                  value = 'Забанить участника.')
    emb.add_field(name = '{}unban'.format(PREFIX), 
                  value = 'Разбанить участника.')

    await ctx.send(embed = emb)
'''

# Connect
token = open('token.txt', 'r').readline()
bot.run(token)