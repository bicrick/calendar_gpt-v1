from calendarFunctions import Calendar
from indexFunctions import Index

#This test will create a new event, get the list of events, 
#get the first event, update the event, and then get the event again to check that it was updated.
def test1():
    Calendar.init()

    #Sample event object
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

    #Create new event using sample event object
    Calendar.add_event(sample_event,'token.json')

    #Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    #Get the id and sumary of the first event
    event_id = events[0]['id']
    event_summary = events[0]['summary']
    print("Previous Event ID: " + event_id)
    print("Previous Event Summary: " + event_summary)

    #Get the event object from the calendar using the id
    event = Calendar.get_event_by_id(event_id,'token.json')

    #Change the event object so that the summary is different
    event['summary'] = "Holy Crap is it Working?"

    #Update the event on the calendar
    Calendar.update_event(event,'token.json')

    #Check that the event was updated
    event = Calendar.get_event_by_id(event_id,'token.json')

    #Print the id and summary of the event
    event_id = event['id']
    event_summary = event['summary']
    print("Previous Event ID: " + event_id)
    print("Previous Event Summary: " + event_summary)

    #check that the summary was updated
    if event_summary == "Holy Crap is it Working?":
        print("Event was updated")
    else:
        print("Event was not updated")
    

#Create a test to create an event like the one above and the delete it. Also checking that it was deleted.
def test2():
    Calendar.init()

    #Sample event object
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

    #Create new event using sample event object
    Calendar.add_event(sample_event,'token.json')

    #Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    #Get the id and sumary of the first event
    event_id = events[0]['id']
    event_summary = events[0]['summary']
    print("Previous Event ID: " + event_id)
    print("Previous Event Summary: " + event_summary)

    #Delete the event
    Calendar.delete_event_by_id(event_id,'token.json')

    #Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    #Check that the event was deleted
    if len(events) == 0:
        print("Event was deleted")
    else:
        print("Event was not deleted")

#Create script that will add all of the events from the events.json file to the calendar
def test3():
    Calendar.init()

    #Get the list of events from the events.json file
    events = Calendar.get_events_from_file('events.json')

    #Add each event to the calendar
    for event in events:
        Calendar.add_event(event,'token.json')

#Create script that will delete all of the events from the calendar
def test4():
    Calendar.init()

    #Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    #Delete each event from the calendar
    for event in events:
        Calendar.delete_event_by_id(event['id'],'token.json')

    #Get the list of events from the calendar
    events = Calendar.get_events('token.json')

    #Check that the event was deleted
    if len(events) == 0:
        print("All events were deleted")
    else:
        print("All events were not deleted")

#Initializes the index - scrapes the calendar and creates the index.
def test5():
    #Create the index
    Index.init_index('token.json')

#Creates a query of choice and returns the event id, and then prints the event summary and description. Then it says when the beginning of the event is and where the event is.
def test6():
    #Define the query
    query = "I got ketchtup on my shirt"
    #Query the index
    event_id = Index.query_index(query)
    #Get the event from the calendar
    event = Calendar.get_event_by_id(event_id,'token.json')
    #Print the different facets of the event, given that they are a present in the event object
    print("Event Summary: " + event['summary'])
    if 'description' in event:
        print("Event Description: " + event['description'])
    if 'location' in event:
        print("Event Location: " + event['location'])
    #Remeber for start times, the format is not always dateTime, and it can be other things like date. Check for these alternatives
    if 'dateTime' in event['start']:
        print("Event Start Time: " + event['start']['dateTime'])
    elif 'date' in event['start']:
        print("Event Start Time: " + event['start']['date'])
    else:
        print("Event Start Time: " + event['start'])
    #Check for reccurence and print the schedule
    if 'recurrence' in event:
        print("Event Schedule: " + event['recurrence'][0])
    
#Create a test that adds an arbitrary event to the calendar:
def test7():
    Calendar.init()

    #Sample event object
    sample_event = {
    "summary": "Spa Day at Bliss",
    "location": "Bliss Spa",
    "description": "Pamper yourself with a relaxing Swedish massage",
    "start": {
      "dateTime": "2023-05-12T14:00:00-04:00",
      "timeZone": "America/New_York"
    },
    "end": {
      "dateTime": "2023-05-12T15:30:00-04:00",
      "timeZone": "America/New_York"
    }
  }

    #Create new event using sample event object
    Calendar.add_event(sample_event,'token.json')

test4()