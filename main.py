import os
from time import sleep

import openai
import random
import discord
import os
from sys import platform
import asyncio
import voiceHandler
import openHandler
from discord.ext import commands

voiceHandler = voiceHandler.voiceHandler()
openHandler = openHandler.openHandler()

# get keys
f = open("discordKey.txt", "r")
try:
    key = ''.join(f.readlines())
except:
    print("Discord key not found!")
print("discordKey: " + key)
f.close()

# discord stuff
description = 'Current default: ' + openHandler.getBehavior()
GUILD_VC_TIMER = {}
intents = discord.Intents.default()
intents.message_content = True
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", description=description, intents=intents)
voice_channel = None
vc = None
isPlaying = False
dictate = 0
styles = ['angry', 'chat', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified',
                  'unfriendly', 'whispering']
currentStyle = None
q = asyncio.Queue()


#  -----------------------------------------MAIN--------------------------------------------- #

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=(discord.Game(name='immensely powerful')))


@bot.event
async def on_message(msg):

    if msg.author == bot.user:
        return

    if bot.user in msg.mentions:
        print("THING DETECTED FREAK OUT, THIS GUYUS SAID THE THING: " + msg.author.name)
        print(currentStyle)

        if currentStyle is None:
            style = random.choice(styles)
            openHandler.setStyle(style)
            voiceHandler.setStyle(style)
        else:
            openHandler.setStyle(currentStyle)
            voiceHandler.setStyle(currentStyle)
        chat_response = openHandler.genMessage(msg)

        if dictate != 0:
            await msg.channel.send(chat_response, reference=msg)
        else:
            await q.put(chat_response)
            if not isPlaying:
                await play(await bot.get_context(msg))

    await bot.process_commands(msg)


async def play(ctx):
    print('starting to speak!')
    event = asyncio.Event()
    event.set()
    global isPlaying
    isPlaying = True

    #initial stuffs needed
    await event.wait()
    event.clear()
    if q.empty():
        print('empty queue, returning')
        isPlaying = False
        return
    msg = await q.get()

    # discord stuff
    try:
        global voice_channel
        voice_channel = ctx.author.voice.channel
    except:
        await ctx.channel.send("`Author not in voice channel - sending to chat instead`\n")
        await ctx.channel.send(msg)
    voiceHandler.generateVoice(msg)
    if voice_channel != None:
        try:
            global vc
            vc = await voice_channel.connect()
        except:
            print("already connected!")
        if sys.platform.startswith("win32"):
            source = discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source="audio.wav")
        else:
            source = discord.FFmpegPCMAudio(source="audio.wav")
        await ctx.reply(msg)
        vc.play(source, after = lambda e: asyncio.run_coroutine_threadsafe(play(ctx), bot.loop))
        #after = lambda e: await speak(ctx)
    else:
        return

 # The same thing without sending the message to chat
async def playNoChat(ctx):
    print('starting to speak!')
    event = asyncio.Event()
    event.set()
    global isPlaying
    isPlaying = True

    #initial stuffs needed
    await event.wait()
    event.clear()
    if q.empty():
        print('empty queue, returning')
        isPlaying = False
        return
    msg = await q.get()

    # discord stuff
    try:
        global voice_channel
        voice_channel = ctx.author.voice.channel
    except:
        return
    voiceHandler.generateVoice(msg)
    if voice_channel != None:
        try:
            global vc
            vc = await voice_channel.connect()
        except:
            print("already connected!")
        if sys.platform.startswith("win32"):
            source = discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source="audio.wav")
        else:
            source = discord.FFmpegPCMAudio(source="audio.wav")
        vc.play(source, after = lambda e: asyncio.run_coroutine_threadsafe(playNoChat(ctx), bot.loop))
        #after = lambda e: await speak(ctx)
    else:
        return

    #  -----------------------------------------COMMANDS--------------------------------------------- #

@bot.command()
async def behavior(ctx, *args):
    "Sets the personality of discort. chatGPT default is: 'helpful AI assistant'."
    openHandler.setBehavior(*args)
    await ctx.send("`Got it! My next prompt will reflect my new behavior. For best results, use !reset`")
    await bot.change_presence(activity=(discord.Game(name=behavior)))
    await reset()


@bot.command()
async def reset(ctx):
    "Resets convo history. Use when things get pissy"
    openHandler.reset()
    await ctx.send("`Successfully reset conversation history.`")


@bot.command()
async def dictate(ctx):
    "Toggles bot to dictate mode"
    global dictate
    global voice_channel
    if dictate == 0:
        dictate = 1
        await ctx.send("`Successfully switched to chat mode.`")
    else:
        dictate = 0
        await ctx.send("`Successfully switched to voice mode.`")
        await speak(ctx)
    print(dictate)


@bot.command()
async def fuckoff(ctx):
    "Disconnect from the voice chat"
    print(voice_channel)
    try:
        await vc.disconnect()
        await dictate()
        await reset()
        await ctx.send('`Bot disconnected, switching back to chat mode.`')
    except:
        await ctx.send('`Bot not in channel!`')


@bot.command()
async def skip(ctx):
    "Skip the currently playing prompt"
    await vc.stop()

@bot.command()
async def speak(ctx, *args):
    "Say a message out loud"
    if currentStyle is None:
        voiceHandler.setStyle(random.choice(styles))
    else:
        voiceHandler.setStyle(currentStyle)
    arg = ""
    for ele in args:
        arg += (ele + " ")
    await q.put(arg)
    await playNoChat(ctx)

@bot.command()
async def history(ctx):
    await ctx.send(openHandler.getHistory())

@bot.command()
async def style(ctx, arg):
    global currentStyle
    if arg in styles:
        currentStyle = arg
        await ctx.send("Changed style to: `" + arg + "`")
    else:
        return await ctx.send("Voice does not exist. Available voices are: `" + '` `'.join(styles) + '`')

@bot.command()
async def voice(ctx, arg):
    try:
        await ctx.send("Changed voice to: " + voiceHandler.setVoice(arg))
    except NameError as e:
        await ctx.send(e)

    #  -----------------------------------------EVENTS--------------------------------------------- #

# this event runs when user leave / join / defen / mute
@bot.event
async def on_voice_state_update(member, before, after):
    # if event is triggered by the bot? return
    if member.id == bot.user.id:
        return

    # when before.channel != None that means user has left a channel
    if before.channel != None:
        voice = discord.utils.get(bot.voice_clients, channel__guild__id=before.channel.guild.id)

        # voice is voiceClient and if it's none? that means the bot is not in an y VC of the Guild that triggerd this event
        if voice == None:
            return

        # if VC left by the user is not equal to the VC that bot is in? then return
        if voice.channel.id != before.channel.id:
            return

        # if VC has only 1 member (including the bot)
        if len(voice.channel.members) <= 1:

            GUILD_VC_TIMER[before.channel.guild.id] = 0

            while True:
                print("Time", str(GUILD_VC_TIMER[before.channel.guild.id]), "Total Members",
                      str(len(voice.channel.members)))

                await asyncio.sleep(1)

                GUILD_VC_TIMER[before.channel.guild.id] += 1

                # if vc has more than 1 member or bot is already disconnectd ? break
                if len(voice.channel.members) >= 2 or not voice.is_connected():
                    break

                # if bot has been alone in the VC for more than 60 seconds ? disconnect
                if GUILD_VC_TIMER[before.channel.guild.id] >= 60:
                    await voice.disconnect()
                    openHandler.resetBehavior()
                    return



bot.run(key)
