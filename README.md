This is a discord bot that will respond with a chatGPT-generated response when you ping it. If you are in a voice call, it will also speak to you with TTS. Currently a WIP as a personal side project.

This currently is only built for small-scale private use (as in, one discord server at a time). One day I might scale it up to larger portions, but I want to make sure I'm happy with this first.

### To Use

This application requires the following packages:

`discord.py`
`azure.cognitiveservices.speech`
`openai`

When you install the package, modify the `samplekeys.txt` file to include your API keys and rename the file to `keys.txt`.


### TO-DO

Add queue for multiple requests (voice mode only)

Add command to leave the call

Add command to change TTS voice/attitude
