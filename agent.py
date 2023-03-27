# Import the langchain library and other modules
from langchain.agents.agent_toolkits import create_python_agent
from langchain.tools.python.tool import PythonREPLTool
from langchain.python import PythonREPL
from langchain.llms.openai import OpenAI
import dotenv
import os
import datetime
import pytz

#Import the calendar functions so the agent can use them
import calendarFunctions

#Get the current date and time relative to the timezone
tz = pytz.timezone('America/Chicago')
current_datetime = datetime.datetime.now(tz)
print(current_datetime)

#Get the current day of the week
current_day = current_datetime.strftime("%A")
print(current_day)


#Grab openai api key from .env file
dotenv.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

#Define an instance of the calendar class
cal = calendarFunctions.Calendar()


# Create a python agent that uses OpenAI as the language model and PythonREPL as the tool
agent = create_python_agent(
    llm=OpenAI(temperature=0.0, max_tokens=1000, openai_api_key=api_key),
    tool=PythonREPLTool(),
    verbose=True,
    tool_kwargs= {'cal': cal,}
)

#Define the task for the agent
task = '''
Add an event on 3/29/2023 at 10AM that I will be going to the Doctors office for a colon treatment.
'''

#Define a string that outlines the current day of the week, date, time, and timezone
realtimedate = "Today is " + current_day + " " + current_datetime.strftime("%B") + " " + current_datetime.strftime("%d") + " " + current_datetime.strftime("%Y") + " " + current_datetime.strftime("%H") + ":" + current_datetime.strftime("%M") + " " + current_datetime.strftime("%Z")

# Define the instructions for the agent
instruction = '''
You are a google calendar assistant. You have been provided an authentication token at the root folder with name 'token.json'. 
Use this to make additions/deletions/modificaitons to the calendar.

You will need to use your knowledge to complete the task queries below:
'''

filler = '''
------------------------------------------------------------------------------------------------------------------------
'''

# Run the agent on the task
output = agent.run(instruction+filler+realtimedate+filler+task)
print(output)