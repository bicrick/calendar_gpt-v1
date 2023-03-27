import openai
import pinecone
import dotenv
import datetime
import pytz
import dateparser
from dateparser.search import search_dates

import os
import re

from indexFunctions import Index
from calendarFunctions import Calendar

def process_query(query_text):
    #Create an openai object

    #Get the current date and time relative to the timezone
    tz = pytz.timezone('America/Chicago')
    current_datetime = datetime.datetime.now(tz)
    print(current_datetime)

    #Get the current day of the week
    current_day = current_datetime.strftime("%A")
    realtimedate = "Today is " + current_day + " " + current_datetime.strftime("%B") + " " + current_datetime.strftime("%d") + " " + current_datetime.strftime("%Y") + " in the timezone of " + current_datetime.strftime("%Z")

    #Get the start and end times for the query
    start_time=""
    end_time=""

    # Get the start and end times using the LLM
    # openai_response_for_time = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": '''
    #         You will be given a query from a user. You do not need to follow up with questions.
    #         Extract the words that have to do with time. Use them to generate a start and end time.
    #         Your response will be used to query the calendar for events within the time range.
    #         You will be given the current date and time in the following format:
    #         Today is {day of the week} {month} {day of the month} {year} in the timezone of {timezone}

    #         You will need to return a two strings following format: 
    #         YYYY-MM-DDTHH:MM:SSZ, YYYY-MM-DDTHH:MM:SSZ

    #         Please only return the start and end time in the format above. Don't ask subsequent questions.
    #         You will be given the current date and time in the following format:
    #         Today is {day of the week} {month} {day of the month} {year} in the timezone of {timezone}
    #         '''},
    #         {"role": "system", "content": realtimedate},
    #         {"role": "user", "content": query_text}
    #     ],
    #     max_tokens=100
    # )
    # time_response = openai_response_for_time['choices'][0]['message']['content']
    # print(time_response)
    # start_time, end_time = extract_dates_from_llm_response(time_response)
    
    # Gather the events from the calendar within the time range using Calendar.get_events_in_date_range()
    # Get the events from the calendar
    # Gather the events from the calendar within the time range using Calendar.get_events_in_date_range()
    # Get the events from the calendar
    if start_time and end_time:
        events = Calendar.get_events_in_date_range('token.json', start_time, end_time)
    else:
        events = []

    #Get the event ids from the events
    event_ids = []
    for event in events:
        event_ids.append(event['id'])
    
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
    id_score_list = Index.query_index(response_for_vector_query, event_ids=None)
    ids = [t[0] for t in id_score_list]

    #Get the event details from the calendar using the ids from the query results
    token_file_path = 'token.json'
    #Using the get event by id function from the calendar class, get the event details from the calendar for each id
    events = []
    for id in ids:
        events.append(Calendar.get_event_by_id(id, token_file_path))
    #Turn events into a long string
    events_string = " ".join([Index.parse_event(event) for event in events])

    #Create another openai object to respond to the user
    openai_response_for_event_details = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": '''
        You will be given a list of a user's google calendar event objects taking place in the future. 
        You will need to take the user query given below and respond with something relating to their events
        Remind users of the dates/times/locations of the relevant events to their query.
        '''},
        {"role": "user", "content": events_string},
        {"role": "user", "content": query_text},
        ]
    )
    return (openai_response_for_event_details['choices'][0]['message']['content'])

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

        response = process_query(query_text)

        # Print the response
        print(response)
    

if __name__ == "__main__":
    main()