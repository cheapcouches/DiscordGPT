from openai import OpenAI
import discord
class openHandler:

    def __init__(self):
        # read from files
        f = open("openAIKey.txt", "r")
        try:
            key = ''.join(f.readline().strip('\n'))
        except:
            print("openAI key not found!")
        f.close()
        try:
            with open("defaultPrompt.txt", "r") as file:
                self.masterBehavior = file.read()
            file.close()
        except:
            raise FileNotFoundError("defaultPrompt.txt does not exist!")

        # initialize variables
        self.client = OpenAI(api_key=key)
        self.messages = [  # messages spelled out is openAI stuff, 'msg' is discord stuff
            {"role": "system", "content": self.masterBehavior}
        ]
        self.styles = ['angry', 'chat', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified',
                       'unfriendly', 'whispering']
        self.style = None


    def genMessage(self, msg):

        # Removes GPT history if there gets to be too many messages
        # Keeps prices down
        # Eventually replace this with actual token analysis
        if len(self.messages) > 10:
            tempList = [None];
            for i in range(1, len(self.messages)):
                if i == 2:
                    tempList = [{"role": "system", "content": self.masterBehavior}]
                else:
                    tempList.append(self.messages[i])
            self.messages = tempList
        for i in self.messages:
            print(i)

        # Generate the message
        self.messages.append({"role": "user", "name": msg.author.name, "content": msg.content})
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        chat_response = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": chat_response})
        print("Generated message")
        return chat_response


    def setStyle(self, style):
        self.messages[0] = {"role": "system", "content": self.masterBehavior + "You are feeling " + style}


    def setBehavior(self, *args):
        print("THE THING YHEAAA")
        arg = ""
        for ele in args:
            arg += (ele + " ")
        self.masterBehavior = arg


    def getBehavior(self):
        return self.masterBehavior

    def resetBehavior(self):
        try:
            with open("defaultPrompt.txt", "r") as file:
                self.masterBehavior = file.read()
            file.close()
        except:
            raise FileNotFoundError("defaultPrompt.txt does not exist!")


    def reset(self):
        self.messages = [{"role": "system", "content": self.masterBehavior}]


    def getHistory(self):
        return self.messages

