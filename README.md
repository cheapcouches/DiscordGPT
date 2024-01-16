This is a discord bot that will respond with a chatGPT-generated response when you ping it. If you are in a voice call, it will also speak to you with TTS. Currently a WIP as a personal side project.

This currently is only built for small-scale private use (as in, one discord server at a time). One day I might scale it up to larger portions, but I want to make sure I'm happy with this first.

### To Use

This application requires the following packages:

`discord.py`
`azure.cognitiveservices.speech`
`openai`

After installing packages, create three txt files named "azureKey.txt", "discordKey.txt", and "openAIKey.txt".

Copy + paste your respective API keys into each TXT file.

### TO-DO

Add command to change TTS voice/attitude

Midi generation
