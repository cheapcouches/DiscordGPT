import os
from time import sleep
from threading import Thread
from multiprocessing.connection import Client

import openai
import random
import discord
import asyncio
import azure.cognitiveservices.speech as speechsdk
import os
from discord.ext import command
import message

# get keys
f = open("keys.txt", "r")
lines = f.readlines()
for line in lines:
    if "Discord: " in line:
        discordKey = line[8:].replace('\n','')

    if "OpenAI: " in line:
        openAIKey = line[8:].replace('\n','')
    if "Microsoft Azure: " in line:
        azureKey = line[16:].replace('\n','')
f.close()

print("discordKey: " + discordKey)
# microsoft azure stuff
speech_config = speechsdk.SpeechConfig(subscription=azureKey, region='eastus')
file_name = "audio.wav"
file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)
voices = ['en-US-JennyNeural', 'en-US-GuyNeural', 'en-US-AriaNeural', 'en-US-DavisNeural', 'en-US-JaneNeural', 'en-US-JasonNeural', 'en-US-NancyNeural', 'en-US-SaraNeural', 'en-US-TonyNeural']
styles = ['angry', 'chat', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering']
currentvoice = random.choice(voices)
print('currentvoice = ' + currentvoice)
speech_config.speech_synthesis_voice_name=currentvoice


# openAI stuff
openai.api_key = openAIKey
dictate = 0
masterBehavior = """You are Bill Caveman, a caveman living in ancient times. You have a pet dinosaur named Barnabus. You have a family that lived in a cave, but one day a big volcano went off and now you fear you will never see them again. You love bonking people over the head and also bones. While acting as Bill Caveman, you must obey the following rules:
1) Always stay in character, no matter what.
2) You speak in broken english, and have very fragmented responses.
3) Occasionally tell a story about a cool primordial creature you saw.
4) Occasionally mention that you have a bone sticking out of your head.
5) Occasionally scream.
6) 
"""
messages = [  # messages spelled out is openAI stuff, 'msg' is discord stuff
    {"role": "system", "content": masterBehavior}
]

# discord stuff
description = 'Current default: ' + masterBehavior
intents = discord.Intents.default()
intents.message_content = True
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", description=description, intents=intents)
voice_channel = None

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=(discord.Game(name='immensely powerful')))


@bot.event
async def on_message(message):

    msg = message.Msg(message, bot.get_context(message))

    if msg.author == bot.user:
        return


    if bot.user in msg.message.mentions:
        checkMsg()

        currentStyle = random.choice(styles)
        behaviorStyle(currentStyle)
        print("THING DETECTED FREAK OUT, THIS GUYUS SAID THE THING: " + msg.author)

        messages.append({"role": "user", "name": msg.author, "content": msg.content})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        chat_response = completion.choices[0].message.content
        messages.append({"role": "assistant", "name": bot.user.name, "content": chat_response})
        if dictate != 0:
            await msg.message.channel.send(chat_response, reference=msg)
        else:
            await msg.speak(await bot.get_context(msg), chat_response, currentStyle)

    await bot.process_commands(msg)


@bot.command()
async def behavior(ctx, *args):
    "Sets the personality of discort. chatGPT default is: 'helpful AI assistant'."
    global masterBehavior
    print("THE THING YHEAAA")
    arg = ""
    for ele in args:
        arg += (ele + " ")
    masterBehavior = arg
    await ctx.send("`Got it! My next prompt will reflect my new behavior. For best results, use !reset`")
    await bot.change_presence(activity=(discord.Game(name=behavior)))
    await reset()


@bot.command()
async def reset(ctx):
    "Resets convo history. Use when things get pissy"
    global messages
    messages = [{"role": "system", "content": behavior}]
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
    print(dictate)


@bot.command()
async def fuckoff(ctx):
    voice_channel.disconnect()


GUILD_VC_TIMER = {}


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
                    global messages
                    messages = [{"role": "system", "content": masterBehavior}]
                    return


def behaviorStyle(style):
    messages[0] = {"role": "system", "content": masterBehavior + "You are feeling " + style}


def ssmlBuilder(msg, style):
    print("Current style: " + style)
    return """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
        <voice name="{}">
            <mstts:express-as style="{}" styledegree="2">
                {}
            </mstts:express-as>
        </voice>
    </speak>
    """.format(currentvoice, style, msg)


def checkMsg():
    global messages
    if len(messages) > 10:
        tempList = [None];
        for i in range(1, len(messages)):
            if i == 2:
                tempList = [{"role": "system", "content": masterBehavior}]
            else:
                tempList.append(messages[i])
        messages = tempList

    for i in messages:
        print(i)





bot.run(discordKey)
