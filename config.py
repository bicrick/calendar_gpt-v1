from calendarFunctions import Calendar
from indexFunctions import Index

# Test creating, updating, and verifying an event update
def test_create_update_event():
    Calendar.init()

    # Sample event object
    sample_event = {
                'summary': 'Test1',
                'location': 'Texas',
                'description': 'This is a test event.',
                'start': {
                    'dateTime': '2023-03-23T14:00:00-05:00',
                    'timeZone': 'America/Chicago',
                },
                'end': {
                    'dateTime': '2023-03-23T14:00:00-08:00',
                    'timeZone': 'America/Chicago',
                },
            }

    # Create new event using sample event object
    Calendar.add_event(sample_event,'token.json')

    # Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    # Get the id and summary of the first event
    event_id = events[0]['id']
    event_summary = events[0]['summary']
    print("Previous Event ID: " + event_id)
    print("Previous Event Summary: " + event_summary)

    # Get the event object from the calendar using the id
    event = Calendar.get_event_by_id(event_id,'token.json')

    # Change the event object so that the summary is different
    event['summary'] = "Holy Crap is it Working?"

    # Update the event on the calendar
    Calendar.update_event(event,'token.json')

    # Check that the event was updated
    event = Calendar.get_event_by_id(event_id,'token.json')

    # Print the id and summary of the event
    event_id = event['id']
    event_summary = event['summary']
    print("Previous Event ID: " + event_id)
    print("Previous Event Summary: " + event_summary)

    # Check that the summary was updated
    if event_summary == "Holy Crap is it Working?":
        print("Event was updated")
    else:
        print("Event was not updated")
    
# Test creating, deleting, and verifying an event deletion
def test_create_delete_event():
    Calendar.init()

    # Sample event object
    sample_event = {
                'summary': 'Test2',
                'location': 'My House',
                'description': 'This is a test event.',
                'start': {
                    'dateTime': '2023-03-23T14:00:00-05:00',
                    'timeZone': 'America/Chicago',
                },
                'end': {
                    'dateTime': '2023-03-23T14:00:00-08:00',
                    'timeZone': 'America/Chicago',
                },
            }

    # Create new event using sample event object
    Calendar.add_event(sample_event,'token.json')

    # Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    # Get the id and summary of the first event
    event_id = events[0]['id']
    event_summary = events[0]['summary']
    print("Previous Event ID: " + event_id)
    print("Previous Event Summary: " + event_summary)

    # Delete the event
    Calendar.delete_event_by_id(event_id,'token.json')

    # Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    # Check that the event was deleted
    if len(events) == 0:
        print("Event was deleted")
    else:
        print("Event was not deleted")

# Test adding all events from a JSON file to the calendar
def test_add_events_from_file():
    Calendar.init()

    # Get the list of events from the events.json file
    events = Calendar.get_events_from_file('events.json')

    # Add each event to the calendar
    for event in events:
        Calendar.add_event(event,'token.json')

# Test deleting all events from the calendar and verifying their deletion
def test_delete_all_events():
    Calendar.init()

    # Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    # Delete each event from the calendar
    for event in events:
        Calendar.delete_event_by_id(event['id'],'token.json')

    # Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    # Check that the event was deleted
    if len(events) == 0:
        print("All events were deleted")
    else:
        print("All events were not deleted")

# Test initializing the index by scraping the calendar and creating the index
def test_init_index():
    # Create the index
    Index.init_index('token.json')

# Test querying the index and returning event details
def test_query_index():
    # Define the query
    query = "I got ketchup on my shirt"
    # Query the index
    id_score_list = Index.query_index(query)
    # Get the event from the calendar
    event = Calendar.get_event_by_id(id_score_list[0][0],'token.json')
    # Print the different facets of the event, given that they are present in the event object
    print("Event Summary: " + event['summary'])
    if 'description' in event:
        print("Event Description: " + event['description'])
    if 'location' in event:
        print("Event Location: " + event['location'])
    # Remember for start times, the format is not always dateTime, and it can be other things like date. Check for these alternatives
    if 'dateTime' in event['start']:
        print("Event Start Time: " + event['start']['dateTime'])
    elif 'date' in event['start']:
        print("Event Start Time: " + event['start']['date'])
    else:
        print("Event Start Time: " + event['start'])
    # Check for recurrence and print the schedule
    if 'recurrence' in event:
        print("Event Schedule: " + event['recurrence'][0])

# Test querying calendar events using query_calendar_events function
def test_query_calendar_events():
    # Define the query
    query = "Dry cleaning"
    # Query the calendar
    events = Calendar.query_calendar_events('token.json',query)
    # Print the events
    for event in events:
        print(event['summary'])

# Test deleting all vectors from the index
def test_delete_all_vectors():
    Index.delete_all_vectors()

test_init_index()