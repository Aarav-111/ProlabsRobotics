**Overview**
This software library is specifically designed to interact with the ChatGPT service. Its primary function is to automatically retrieve responses and information directly from ChatGPT. The key characteristic of this library is its ability to extract data from ChatGPT **WITHOUT** requiring the use of the *official OpenAI API key*. Instead of relying on the conventional API access method, the code within this library employs alternative techniques to obtain the desired output from ChatGPT. 

In essence, this library provides a method to access and utilise ChatGPT's capabilities in a way that bypasses the standard API key authentication process.

**Usage**
To use the library, you first have to install the "ProlabsRobotics" library or Package in Python by running the following command in your terminal/bash/command prompt

*pip install git+https://github.com/Aarav-111/ProlabsRobotics.git*

Then run this code (in Python):

from ProlabsRobotics import AI

Prompt = input("Enter your prompt here: ")

system_prompt = """
Your name is "AI-Scraping-Version-5.5", trained by Prolabs Robotics.
You are a human-like AI assistant.
Respond directly and professionally while keeping a conversational tone.
Avoid jargon & buzzwords.
Use headings and subheadings for organisation.
Provide concise code without comments unless explicitly asked.
Maintain context across turns and follow user instructions carefully.
"""

print(AI(system_prompt=system_prompt).ask(Prompt))


**Specifications**
- Name = ProlabsRobotics
- Author company = Prolabs Robotics
- Author = Aarav J.
- Version = 5.5

To use the Older version(s) of this library, please contact Prolabs Robotics' official via:
- [ProlabsRobotics@gmail.com]
- +91 90364 49179
