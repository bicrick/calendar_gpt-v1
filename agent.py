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


# Create a python agent that uses OpenAI as the language model and PythonREPL as the tool
agent = create_python_agent(
    llm=OpenAI(temperature=0.0, max_tokens=1000, openai_api_key=api_key),
    tool=PythonREPLTool(),
    verbose=True,
    tool_kwargs= {'Calendar': calendarFunctions.Calendar,}
)

#Define the task for the agent
task = '''
On tuesday I am going to give Izzy a big kiss and take her out to dinner. She is the best girlfriend. I am thinking around 9PM.
'''

#Define a string that outlines the current day of the week, date, time, and timezone
realtimedate = "Today is " + current_day + " " + current_datetime.strftime("%B") + " " + current_datetime.strftime("%d") + " " + current_datetime.strftime("%Y") + " " + current_datetime.strftime("%H") + ":" + current_datetime.strftime("%M") + " " + current_datetime.strftime("%Z")

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

## Additonal Methods:
query_calendar_events(token_file_path,search_term,start_date,end_date,max_results=None): Queries the calendar for events that match the search term.

search_term is a required parameter that will always be a string that is queries the summary, description, and attendees of the events on the calendar.
start_date is a datetime.datetime object that is not required.
end_date is a datetime.datetime object that is not required.
max_results is an integer that limits the number of results returned and is not required.

## Update Instructions
In order to update an event, you must first retrieve the event by its ID. 
You do this by querying the calendar using the query_calendar_events method for the event and extracting the event ID from the event object.
Then, you can update the event object and pass it to the update_event method.

## Delete Instructions
In order to delete an event, you must first retrieve the event by its ID.
You do this by querying the calendar for the event and extracting the event ID from the event object.
Then, you can pass the event ID to the delete_event_by_id method.

## Date and Time Instructions:
When formatting the event object, you must use either a date or datetime object.
However, it must be a string before passing it to the Calendar class methods.

## RULES
1. ONLY EXECUTE AN ADDITION OR DELETION OF AN EVENT ONCE.
2. DO NOT INCLUDE ANY NEW ADDITIONS TO THE EVENT OBJECT, (RECURRANCE, REMINDERS,Etc.), UNLESS SPECIFICALLY ASKED TO DO SO.
3. ASK FOR HELP IF YOU GET STUCK or NEED MORE INFORMATION

'''

filler = '''
------------------------------------------------------------------------------------------------------------------------
'''

# Run the agent on the task
agent.run(instruction+filler+realtimedate+filler+task)