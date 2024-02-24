import azure.cognitiveservices.speech as speechsdk
import random


class voiceHandler:

    # constructor
    def __init__(self):
        f = open("azureKey.txt", "r")
        try:
            key = ''.join(f.readline().strip('\n'))
        except:
            raise FileNotFoundError("azureKey.txt not found")
        f.close()

        print(key)
        self.speech_config = speechsdk.SpeechConfig(subscription=key, region='eastus')
        self.file_name = "audio.wav"
        self.file_config = speechsdk.audio.AudioOutputConfig(filename=self.file_name)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.file_config)
        self.voices = ['Jenny', 'Guy', 'Aria', 'Davis', 'Jane', 'Jason', 'Nancy', 'Sara', 'Tony']
        self.styles = ['angry', 'chat', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified',
                  'unfriendly', 'whispering']
        self.currentVoice = "en-US-" + random.choice(self.voices) + "Neural"
        print('currentVoice = ' + self.currentVoice)
        self.speech_config.speech_synthesis_voice_name = self.currentVoice
        self.currentStyle = None

    # Generates an audio file and saves it to the directory
    # Returns nothing
    def generateVoice(self, text):

        print('tryinta speak!')
        file_name = "audio.wav"
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=file_config)
        result = speech_synthesizer.speak_ssml(self.ssmlBuilder(text))
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}], and the audio was saved to [{}]".format(text, file_name))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

    # Builds the message in ssml
    # allows for voice styles to work
    def ssmlBuilder(self, msg):
        print("Current style: " + self.currentStyle)
        return """
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{}">
                <mstts:express-as style="{}" styledegree="2">
                    {}
                </mstts:express-as>
            </voice>
        </speak>
        """.format(self.currentVoice, self.currentStyle, msg)

    def setStyle(self, style):
        self.currentStyle = style

    def setVoice(self, voice):
        if voice in self.voices:
            self.currentVoice = "en-US-" + voice + "Neural"
            return self.currentVoice
        else:
            raise NameError("Voice does not exist. Available voices are: `" + "` `".join(self.voices) + "`. You can preview voices here: https://speech.microsoft.com/portal/voicegallery")
