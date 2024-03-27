import json
import math
import random
import requests
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import requests
##################################################################          PART 1:           ####################################################

## get the search input from the user

#event = str(input("what event do you want to buy a ticket for ?"))
#city = str(input("what city do you want the event to be held in ?"))
#ticketPrice = int(input("Enter the maximum amount for the ticket:"))
#from_address = input("Enter your address in the form ( street, city, state. example: 1456 lantern lane, Florence, NY")
#Event_Genre = input("enter the event's genre you prefer:")

event = "concerts"
city = "cincinnati"
resource = ['venues', 'events']

response = requests.get(
    url='https://app.ticketmaster.com/discovery/v2/events',
    params={
        'apikey': 'pKuE2ifGu5wmUqsIAxgzdIDbqiWz26pt',
        'resource': resource,
        'keyword': event,
        'city': city,

    }).json()

###################################################################################

##########################################################
with open('ticketmaster22.json', 'w') as file:

    json.dump(response,file,indent=4)

########################################################################

ticketData = pd.read_json("ticketmaster.json")
event_data = ticketData['_embedded']['events']
# data_3 = data_2['events']
normalized_event_data = pd.json_normalize(event_data)

####################                 Type of Event   ##################################################

events_type = []
event_genre = []
event_subGenre = []

for eventType in normalized_event_data['classifications']:
    # print(" classification ###################")
    print(eventType)
    for dictionary in eventType:
        type = dictionary.get('segment')
        genre = dictionary.get('genre')
        subGenre = dictionary.get('subGenre')
        ##
        events_type.append(type.get('name'))
        event_genre.append(genre.get('name'))
        event_subGenre.append(subGenre.get('name'))

###########   date & time                                                #############################################

print(" dates $$$$$$$$$$$$$$$$$")
event_Date = []

for date in normalized_event_data['dates.start.localDate']:
    print(date)
    event_Date.append(date)

print("********************           time")
event_Time = []
for time in normalized_event_data['dates.start.localTime']:
    print(time)
    event_Time.append(time)

#####################################   Get the ticket price of the event    #############################
price = []

# we're trying to extract the price from the list of dict in the 'priceRanges' column,
# But there are nan values and they're a float objects which means that we can't iterate through them,
# So, we're going to replace them with a string 'price unknown',
# in order for us to iterate through the dict and extract the price

normalized_event_data['priceRanges'].fillna('Price Unknown', inplace=True)

for row in normalized_event_data['priceRanges']:

    if isinstance(row[0], dict):
        price.append(row[0]['max'])

    else:
        price.append(row)

# ******************************************************************************************************************************

########################################################   we want to GET the full address of the event,      ######################################################
########################################################   so we can measure the distance between the user and the event. And also to provide driving directions.

full_address = []
street_address = []
city = []
state = []
for row in normalized_event_data['_embedded.venues']:
    for location in row:

        loc_city = location.get('city')
        loc_state = location.get('state')
        loc_street = location.get('address')
        street_name = 'line1'

        # full address by adding all strings together
        f_address = loc_street['line1'] + ", " + loc_city['name'] + ", " + loc_state['stateCode']
        full_address.append(f_address)


################################################ The new data frame with only the information we need  ######################

all_needed_data = {'Event': normalized_event_data['name'], 'Date': event_Date, 'Time': event_Time,
                   'Event_Type': events_type,
                   'Genre': event_genre, 'Sub_Genre': event_subGenre, 'full_address': full_address,
                   'Price': price}
all_needed_data = pd.DataFrame(all_needed_data)

##  Replace 'Price Unknown' with a random generated price

value = -1
for row in all_needed_data['Price']:
    value = value + 1
    if row == 'Price Unknown':
        all_needed_data['Price'][value] = random.randint(15, 90)



#####           driving distance and direction             #################################3

#########################################################################################################
def get_directions(api_key, from_address, to_address):
    # Encode the addresses
    from_address_encoded = requests.utils.quote(from_address)
    to_address_encoded = requests.utils.quote(to_address)

    # Construct the URL for the Directions API
    url = f"http://www.mapquestapi.com/directions/v2/route?key={api_key}&from={from_address_encoded}&to={to_address_encoded}"

    # Make the GET request
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Check if the route is available
        if 'route' in data and 'legs' in data['route']:
            distance = data['route']['distance']
            legs = data['route']['legs']

            # Extract directions
            directions = []
            for leg in legs:
                for maneuver in leg['maneuvers']:
                    directions.append(maneuver['narrative'])

            return distance, directions
        else:
            return None, "No route found."
    else:
        return None, f"Error: {response.status_code}"



api_key = 'tpDhFVmVmBBpUHshKkMoiiR7gubySisZ'
from_address = '1632 Corinthian drive, Florence, KY'

########################### add the driving distance and the directions to our dataframe

distances = []
directions = []
num_events = 0
for address in all_needed_data['full_address']:
    num_events = num_events + 1
    dis, direction = get_directions(api_key, from_address, address)

    distances.append(dis)
    directions.append(direction)

all_needed_data['driving_distance'] = distances
all_needed_data['directions'] = directions
all_needed_data.to_csv('needed_data.csv')
print(all_needed_data.iloc[2])
##########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################

#*********************************            PART 2:                ************************************
i = 0
#while i < num_events:

#for row in all_needed_data:
 #   print(row)
    #i = i+1
#print(i)

# User Preferences
max_distance = 20
max_price = 30

# Scoring Function
def score_event(row, max_distance, max_price):
    distance_score = max(0, max_distance - row['driving_distance']) / max_distance
    price_score = max(0, max_price - row['Price']) / max_price
    return (distance_score + price_score) / 2

# Apply Scoring Function
all_needed_data['score'] = all_needed_data.apply(score_event, axis=1, max_distance=max_distance, max_price=max_price)

# Sorting by Score
recommended_events = all_needed_data.sort_values(by='score', ascending=False)
recommended_events.to_csv("sorted_data.csv")
