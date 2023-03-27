import openai
import pinecone
import dateutil
import dotenv
import os
import datetime
import json

from calendarFunctions import Calendar

class Index:
    def get_embedding(text,model="text-embedding-ada-002"):
        text = text.replace("\n"," ")
        #add the openai api key from the .env file
        dotenv.load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        return openai.Embedding.create(input=text, model=model)['data'][0]
    
    def parse_event(event):
        event_string = ''

        # Get the summary (name/title) of the event
        summary = event.get('summary', '')
        if summary:
            event_string += f'Summary: {summary} '

        # Get the start and end times of the event
        start_time = ''
        end_time = ''
        start = event.get('start', {})
        end = event.get('end', {})
        if 'dateTime' in start:
            start_time = dateutil.parser.parse(start['dateTime']).strftime('%Y-%m-%d %H:%M:%S')
        elif 'date' in start:
            start_time = dateutil.parser.parse(start['date']).strftime('%Y-%m-%d')
        if 'dateTime' in end:
            end_time = dateutil.parser.parse(end['dateTime']).strftime('%Y-%m-%d %H:%M:%S')
        elif 'date' in end:
            end_time = dateutil.parser.parse(end['date']).strftime('%Y-%m-%d')
        if start_time and end_time:
            event_string += f'Time: {start_time} - {end_time} '

        # Get the duration of the event if it is not specified in the 'end' property
        duration = ''
        if 'dateTime' in start and 'dateTime' in end:
            event_start = dateutil.parser.parse(start['dateTime'])
            event_end = dateutil.parser.parse(end['dateTime'])
            event_duration = event_end - event_start
            if event_duration.days > 0:
                duration = f'{event_duration.days} day(s) '
            duration += f'{event_duration.seconds // 3600} hour(s) {(event_duration.seconds // 60) % 60} minute(s)'
        elif 'date' in start and 'date' in end:
            event_start = dateutil.parser.parse(start['date'])
            event_end = dateutil.parser.parse(end['date']) + datetime.timedelta(days=1)
            event_duration = event_end - event_start
            if event_duration.days > 0:
                duration = f'{event_duration.days} day(s) '
            duration += f'{event_duration.seconds // 3600} hour(s) {(event_duration.seconds // 60) % 60} minute(s)'
        if duration:
            event_string += f'Duration: {duration} '

        # Get the location of the event
        location = event.get('location', '')
        if location:
            event_string += f'Location: {location} '

        # Get the description of the event
        description = event.get('description', '')
        if description:
            event_string += f'Description: {description} '

        # Get the list of attendees for the event
        attendees = event.get('attendees', [])
        if attendees:
            attendee_emails = [attendee.get('email', '') for attendee in attendees]
            event_string += f'Attendees: {", ".join(attendee_emails)} '

        # Get the recurrence information for the event
        recurrence = event.get('recurrence', [])
        if recurrence:
            event_string += f'Recurrence: {", ".join(recurrence)} '

        # Get the reminders for the event
        reminders = event.get('reminders', {}).get('overrides', [])
        if reminders:
            reminder_methods = [reminder.get('method', '') for reminder in reminders]
            event_string += f'Reminders: {", ".join(reminder_methods)} '


        # Return the event string
        return event_string



    def init_index(token_file_path):
        #Get the openai api key from the .env file
        dotenv.load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

        #Get the list of events from the calendar
        events = Calendar.get_events(token_file_path)

        #Using the list of event objects, create a list of event strings containing the event details using the parse_event function
        event_strings = []
        for event in events:
            event_strings.append(Index.parse_event(event))

        #Create embeddings for each event string using ada framework.
        event_embeddings = []
        for event_string in event_strings:
            event_embeddings.append(Index.get_embedding(event_string))

        #supply Pinecone API key
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"),environment="us-central1-gcp")

        #Create a pinecone index or use an existing one if the index already exists
        index_name = "events-index"
        global index
        
        #check if index exists
        if index_name in pinecone.list_indexes():
            index = pinecone.Index(index_name)
        else:
            index = pinecone.create_index(name=index_name, dimension = 1536)
        
        data = []
        for i in range(len(event_embeddings)):
            event_id = events[i]['id']
            event_embedding = event_embeddings[i]
            metadata = {'event_id': event_id}
            values = list(map(float, event_embedding['embedding']))

            data.append({'id': event_id, 'values': values, 'metadata': metadata})

        payload = {'vectors': data}

        vectors = payload["vectors"]

        # upsert the vectors
        index.upsert(vectors=vectors)

        return

    #Returns a list of the ids and their scores mathcing the query. The top 5 results are returned.
    def query_index(query_text, event_ids=None):
        # Get the embedding of the query text using the same model as before
        query_embedding = Index.get_embedding(query_text)
        # Query the index for the closest event to the query text
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"),environment="us-central1-gcp")
        index = pinecone.Index("events-index")
        results = index.query(query_embedding['embedding'], top_k=len(event_ids) if event_ids else 5)
        # Get the event ID and metadata from the query results
        if event_ids:
            id_score_list = [
                (match['id'], match['score'])
                for match in results['matches']
                if match['id'] in event_ids
            ]
        else:
            id_score_list = [(match['id'], match['score']) for match in results['matches']]


        return id_score_list
    
    def delete_all_vectors():
        #load the pinecone api key from the .env file
        dotenv.load_dotenv()
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"),environment="us-central1-gcp")
        index = pinecone.Index("events-index")
        index.delete(deleteAll=True)