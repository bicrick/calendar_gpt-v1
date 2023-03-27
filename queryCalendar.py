import openai
import pinecone
import dotenv

import os

from indexFunctions import Index
from calendarFunctions import Calendar


def main():
    #Initilaize the index - this will add all the events on your calendar to the vector store.
    Index.init_index('token.json')

    # Create an OpenAI object using your API key and parameters, and specify the gpt-3.5-turbo model as the engine
    #Get the openai api key from .env file
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


    #Get the user input
    query_text = input("Enter a query: ")

    #Create an openai object
    openai_response_for_vector_query = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": '''
        You will be given a query. 
        What you return will be used to query a vector store containing google calendar event documents. 
        The documents will be retrieved and used to generate a natural language response. 

        I need you to use the user query to generate a list of strings that will be used to query the vector store.

        IE:
        User: My teeth hurt. I think I have a cavity.
        You: teeth cavity
        '''},
        {"role": "user", "content": query_text},
        ]
    )

    #Get the text from the response
    print("Gathering from vector store: " + openai_response_for_vector_query['choices'][0]['message']['content'])
    response_for_vector_query = openai_response_for_vector_query['choices'][0]['message']['content']

    #Query the vectorstore using the query text and functions from the Index class
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
    #print the response
    print(openai_response_for_event_details['choices'][0]['message']['content'])
    

if __name__ == "__main__":
    main()