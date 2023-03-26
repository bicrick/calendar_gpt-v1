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


#Get the current day of the week
current_day = current_datetime.strftime("%A")


#Grab openai api key from .env file
dotenv.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


# Create a python agent that uses OpenAI as the language model and PythonREPL as the tool
agent = create_python_agent(
    llm=OpenAI(temperature=0.0, max_tokens=1000, openai_api_key=api_key),
    tool=PythonREPLTool(),
    verbose=True,
    tool_kwargs= {'Calendar': calendarFunctions.Calendar,
                 'current_datetime': current_datetime,
                 'current_day': current_day}
)

#Define the task for the agent
task = '''
I think Izzy and I will be leaving at 11AM now. Change my calendar to reflect that.'''
# Define the instructions for the agent
instruction = '''
## Overall Instructions:
You are a calendar assistant. You will help users by adding, deleting, and modifying events on their calendar.

## Calendar Class Instructions
You have been given the Calendar class from calendarFunctions.py. 
You can use this class to add/delete/modify events on the calendar. 
You will need to choose which functions to use and when. Here are its static methods:

## Calendar Class Methods:
get_events(token_file_path): Retrieves all events from the calendar.
get_event_by_id(event_id, token_file_path): Retrieves an event by its ID.
delete_event_by_id(event_id, token_file_path): Deletes an event by its ID. If the event is recurring, it will delete all instances.
add_event(event, token_file_path): Adds an event to the calendar.
update_event(event, token_file_path): Updates an existing event on the calendar.
delete_event(event, token_file_path): Deletes an event from the calendar.

## Calendar Class Attributes:
token_file_path will always be: 'token.json'
event will always be the google calendar event object.
event_id will have to be extracted from the event object.

## Date and Time Instructions:
When formatting the event object, you must use either a date or datetime object.
However, it must be a string before passing it to the Calendar class methods.

## Relative Time Instructions:
You can use the current_datetime and current_day variables to get the current date and time and day of the week. You can use these variables to construct relative time events.

## Recurrence Instructions
Unless specifically prompted, you do not need to create a field for recurrence. Refer to google calendar documentation for more information on recurrence.

## RULES
1. ONLY EXECUTE AN ADDITION OR DELETION OF AN EVENT ONCE.
2. DO NOT INCLUDE ANY NEW ADDITIONS TO THE EVENT OBJECT, (RECURRANCE, REMINDERS,Etc.), UNLESS SPECIFICALLY ASKED TO DO SO.
TASK:

'''

# Run the agent on the task
agent.run(instruction+task)