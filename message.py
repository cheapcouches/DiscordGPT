import openai
import random
import discord
import asyncio
import azure.cognitiveservices.speech as speechsdk
import os
#from discord.ext import command
from time import sleep

voices = ['en-US-JennyNeural', 'en-US-GuyNeural', 'en-US-AriaNeural', 'en-US-DavisNeural', 'en-US-JaneNeural', 'en-US-JasonNeural', 'en-US-NancyNeural', 'en-US-SaraNeural', 'en-US-TonyNeural']
styles = ['angry', 'chat', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering']

class Msg:
    def __init__(self, message, ctx):
        self.message = message
        self.ctx = ctx
        self.content = message.content
        self.author = message.author.name
        self.voiceName = random.choice(voices)
        self.voiceAttitude = random.choice(styles)


    async def speak(self):
        self.voiceAttitude = random.choice(styles)
        try:
            while self.ctx.voice_client.is_playing():
                print("Waiting for audio to finish...")
                sleep(5)
        except:
            print("Nothing playing!")
        # sleep to avoid race condition
        sleep(1)

        # TTS stuff
        print('tryinta speak!')
        file_name = "audio.wav"
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)
        result = speech_synthesizer.speak_ssml(self.ssmlBuilder(self.message, self.voiceAttitude))
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}], and the audio was saved to [{}]".format(msg, file_name))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

        # discord stuff
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.channel.send("`Author not in voice channel - sending to chat instead`\n")
            await ctx.channel.send(msg)
        channel = None
        if voice_channel != None:
            try:
                global vc
                vc = await voice_channel.connect()
            except:
                print("already connected!")

            source = discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source="audio.wav")
            await ctx.reply(msg)
            vc.play(source)

        else:
            return


    def ssmlBuilder(self, msg, style):
        print("Current style: " + style)
        return """
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{}">
                <mstts:express-as style="{}" styledegree="2">
                    {}
                </mstts:express-as>
            </voice>
        </speak>
        """.format(self.currentAttitude, style, msg)