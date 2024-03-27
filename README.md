Recommendation System Report

Introduction

We got the data from the Ticketmaster website, using Ticketmaster API, we used the request library. I implemented the user input in term of a profile:
User 1 
Keyword (event type)  = ‘Music Concerts’
City = ‘Cincinnati’
Max_price = $30
Max_distance = 20 (miles)

Only the event type and the city it’s held in will be sent along side with the API key we got from Ticketmaster Developers as parameters, and it will return a Json file as a response. We will use the Max_price and Max_distance to create a scoring function to score each event.
The Json file will have enormous information about the events (of the type that’s requested by the user), the following are the attributes for every event:


 Name,      type,      id,        test,       url,       locale,        images,        classifications,
promoters,        info,       pleaseNote,     priceRanges,      sales.public.startDateTime,
sales.public.startTBD,            sales.public.startTBA,             sales.public.endDateTime,
sales.presales,         dates.start.localDate,         dates.start.localTime,         dates.start.dateTime,
dates.start.dateTBD,          dates.start.dateTBA,            dates.start.timeTBA,
dates.start.noSpecificTime,               dates.timezone,           dates.status.code,
dates.spanMultipleDays,           promoter.id,          promoter.name,             promoter.description,
seatmap.staticUrl,            accessibility.ticketLimit,            ageRestrictions.legalAgeEnforced,
ageRestrictions.ageRuleDescription,                 doorsTimes.localDate,
doorsTimes.localTime,               doorsTimes.dateTime,                ticketing.safeTix.enabled,
ticketing.allInclusivePricing.enabled,                 _links.self.href,                        _links.attractions,
_links.venues,                     _embedded.venues,                 _embedded.attractions,products,
ticketLimit.info,                     outlets,                accessibility.info,    
dates.initialStartDate.localDate,                dates.initialStartDate.localTime, 
dates.initialStartDate.dateTime


Extracting the data we need to build the recommendation

Most of the data in the JSON file is in the form of a dictionary inside of a dictionary, for example:
[{'primary': True, 'segment': {'id': 'KZFzniwnSyZfZ7v7na', 'name': 'Arts & Theatre'}, 'genre': {'id': 'KnvZfZ7v7na', 'name': "Children's Theatre"}}]
The type of event is a dictionary with the key ‘segment’, but it’s also inside of a dictionary.
Most of the data in the JSON file is not going to be useful for building the recommendation system, I went over the whole data multiple times to see which part of the data we’re going to need, and it turned out to be:

-	Name of the event
-	Date
-	Time
-	Type
-	Genre
-	Sub-Genre
-	Street address
-	City
-	State
-	Driving distance: I used street-address, city and state to get it with mapquest API.
-	Driving direction: I used street-address, city and state to get it with mapquest API.
-	Price  

80% of the data of Price is Nan, so because the price is so important for our recommendation system I generated a random price whenever the price was Nan.   


Building the recommendation system

For preferences, I used the following to build the logic of the recommendation system:
-	Price
-	Driving distance

This is the scoring function I used to score every event and then sort them based on that score:

def score_event(row,  max_distance,  max_price):
    distance_score = max(0, max_distance - row['driving_distance']) / max_distance
    price_score = max(0, max_price - row['Price']) / max_price
    return (distance_score + price_score) / 2

Results

Our system recommended the following events in order:
(note: I didn’t include here some of the event’s data such as the name and full address, because of space, also I only included the first 3 events)

         ID	         GENRE	         PRICE	       DISTANCE
         3	Classical	        $15	        15 miles
         7	Metal	        $22	        26 miles
         1	Classical	        $30	        17 miles

We can see that our system will prioritize the price over the distance.
