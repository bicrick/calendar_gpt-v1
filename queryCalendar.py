import openai
import pinecone
import dotenv
from datetime import datetime, time
from dateutil import tz, parser
import dateparser

import os
import re

from indexFunctions import Index
from calendarFunctions import Calendar

def process_time(query_text):
    #Create an openai object

    #Get the current date and time relative to the timezone
    timezone = tz.tzlocal()
    current_datetime = datetime.now(timezone)
    print(current_datetime)

    #Get the current day of the week
    current_day = current_datetime.strftime("%A")
    realtimedate = "Today is " + current_day + " " + current_datetime.strftime("%B") + " " + current_datetime.strftime("%d") + " " + current_datetime.strftime("%Y") + " in the timezone of " + current_datetime.strftime("%Z")

    # Initialize the start and end times as None
    start_time = None
    end_time = None

    # Use regular expressions to extract date-related words from the query text
    pattern = r"(\d+:\d+|\d+ [ap]m|tomorrow|today|yesterday|(this|next|last) (\d+ )?\w+|\d+ days? ago|\d+ days? later|\d+ weeks? ago|\d+ weeks? later|\d+ months? ago|\d+ months? later|\d+ years? ago|\d+ years? later)"
    matches = re.findall(pattern, query_text)
    print(matches)

    # Parse the date-related words into datetime objects and find the overall time range for the query
    if matches:
        for match in matches:
            parsed_time = dateparser.parse(match[0], settings={'RELATIVE_BASE': current_datetime})
            parsed_time = parsed_time.astimezone(current_datetime.tzinfo)

            print("Found: %s, Parsed: %s" % (match[0], parsed_time))
            #If a parse date is found and it is after the current date, set it as the end time and the start time as the current date
            if parsed_time is not None and parsed_time > current_datetime:
                end_time = parsed_time
                start_time = current_datetime
            #If a parse date is found and it is before the current date, set it as the start time and the end time as None
            elif parsed_time is not None and parsed_time < current_datetime:
                start_time = parsed_time
                end_time = None


        # Set the end time to the end of the day if it is found in the query
        if end_time is not None:
            end_time = datetime.combine(end_time.date(), time(hour=23, minute=59, second=59, microsecond=999999))

    # Convert the start and end times to the UTC timezone and ISO format if they are not None
     # Convert the start and end times to the UTC timezone and ISO format if they are not None
    if start_time is not None and end_time is not None:
        start_time = start_time.astimezone(tz.UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        end_time = end_time.astimezone(tz.UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        print("Start time in UTC timezone:", start_time)
        print("End time in UTC timezone:", end_time)
    elif start_time is not None:
        
        end_time = None
        print("Start time in UTC timezone:", start_time)
        print("No end time found in the query.")
    else:
        print("No time-related words found in the query.")


    return start_time, end_time


def process_semantic_search(query_text):
    #Process the query text for a semantic search. Returns a list of strings that will be used to query the vector store
    openai_response_for_vector_query = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": '''
        You will be given a query. 
        What you return will be used to query a vector store containing google calendar event documents. 
        The documents will be retrieved and used to generate a natural language response. 

        I need you to use the user query to generate a list of strings that will be used to query the vector store.
        The strings should be related to the user's query.

        IE:
        User: My teeth hurt. I think I have a cavity.
        You: teeth cavity

        IE:
        User: I am low on cash. Am I going the the bank anytime soon?
        You: cash bank

        '''},
        {"role": "user", "content": query_text}
        ]
    )

    #Get the text from the response
    print("Gathering from vector store: " + openai_response_for_vector_query['choices'][0]['message']['content'])
    response_for_vector_query = openai_response_for_vector_query['choices'][0]['message']['content']

    #Query the vectorstore using the query text and functions from the Index class
    # Query the Pinecone base using the filtered event ids
    id_score_list = Index.query_index(response_for_vector_query)
    ids = [t[0] for t in id_score_list]

    #Get the event details from the calendar using the ids from the query results
    token_file_path = 'token.json'
    #Using the get event by id function from the calendar class, get the event details from the calendar for each id
    events = []
    for id in ids:
        events.append(Calendar.get_event_by_id(id, token_file_path))
    #Turn events into a long string
    events_string = " ".join([Index.parse_event(event) for event in events])
    return events_string

def generate_response(query_text, events_string):
    #Get the local time information:
    timezone = tz.tzlocal()
    current_datetime = datetime.now(timezone)
    current_day = current_datetime.strftime("%A")
    realtimedate = "Today is " + current_day + " " + current_datetime.strftime("%B") + " " + current_datetime.strftime("%d") + " " + current_datetime.strftime("%Y") + " in the timezone of " + current_datetime.strftime("%Z")
    
    #Create another openai object to respond to the user
    openai_response_for_event_details = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": '''
        You will be given a list of a user's google calendar event objects taking place in the future. 
        You will need to take the user query given below and respond with something relating to their events
        Remind users of the dates/times/locations of the relevant events to their query.
        '''},
        {"role": "user", "content": realtimedate},
        {"role": "user", "content": events_string},
        {"role": "user", "content": query_text},
        ]
    )
    return (openai_response_for_event_details['choices'][0]['message']['content'])

def process_query(query_text):
    #Process Time:
    start_time, end_time = process_time(query_text)
    #Process Semantic Search
    if(start_time==None and end_time==None):
        events_string = process_semantic_search(query_text)
    else:
        events = Calendar.get_events_in_date_range('token.json', start_time, end_time)
        events_string = " ".join([Index.parse_event(event) for event in events])
    #Respond to the User
    response = generate_response(query_text, events_string)
    #Return the response:
    return response

def main():
    #Initilaize the index - this will add all the events on your calendar to the vector store.
    Index.init_index('token.json')

    # Create an OpenAI object using your API key and parameters, and specify the gpt-3.5-turbo model as the engine
    #Get the openai api key from .env file
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    while True:
        # Get the user input
        query_text = input("Enter a query (type 'exit' to quit): ")

        if query_text.lower() == 'exit':
            break

        if query_text.lower() == 'refresh':
            Index.init_index('token.json')
            continue

        response = process_query(query_text)

        # Print the response
        print(response)
    

if __name__ == "__main__":
    main()