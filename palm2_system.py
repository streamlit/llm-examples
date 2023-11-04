#!/usr/bin/env python

"""PaLM 2 Restaurant Recommender System

This is a library that interfaces with the Google Maps API and the PaLM 2 API
to create the backend for the restaurant recommender system.

As soon as the user logs into the app, the Google Maps API extracts all nearby
restaurants and loads it into the context of the PaLM 2 LLM. The user then
provides prompts which are fed into the PaLM 2 LLM, and then this library
extracts the resopnse from the model to give back to the front end and then the
user.

The way to use this API is to do the following:
    1) While setting up the app, run the following command:
            
            response = palm2_system.setup()
       
       This setup command sets up the 'response' object, which will hold all of
       the conversation between the user and PaLM 2

    2) Each time the user gives a prompt, run the following command:
            
            answer = palm2_system.chat(response, [whatever the prompt is])
       
       This command returns the answer from PaLM 2 but at the same time updates
       the 'response' object with the new prompt and answer. To be clear, the
       'answer' variable contains the most recent text response from PaLM 2.
       The string stored in this variable should be the one displayed to the
       user. And this 'response' object is the same response object you defined
       in the setup.
"""

# Insert modules here
import geocoder
import google.generativeai as palm
import requests

__author__ = "Akhil Karra"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Akhil Karra"
__email__ = "akarra@andrew.cmu.edu"
__status__ = "Prototype"

# PaLM 2 Hyperparameters
DEFAULTS = {
    'model': 'models/chat-bison-001',
    'temperature': 0.15,
    'top_k': 5,
    'top_p': 1,
}
MESSAGES = []
CONTEXT = """I want to order some food for delivery or pickup but I don't know
what to get.

Your job is to ask questions to me about my food preferences, my dietary
restrictions, and my current mood and then recommend restaurants for delivery
or pickup to me. Have a cheerful conversation with me. Follow this step-by-step
process. Make sure to ask me these questions one RESPONSE at a time. Don't
reveal all the questions to me in one go.
1) Ask me about current mood.
2) Ask whether I would like delivery or pickup.
2) Ask me about what kind of food I would like to eat.
3) Ask me about my dietary restrictions.
4) Using all of the information you have gathered above, give me the top 5
restaurant recommendations back.

Important note: DO NOT GIVE ME ANY RESTAURANT RECOMMENDATIONS UNTIL YOU REACH
STEP 4.

Stay in character for every RESPONSE you give me. Keep your RESPONSEs short.
Ask one and only one question per RESPONSE. Feel free to ask me questions, too.
"""
EXAMPLES = [
  [
    "Hi",
    "Hello! How can I help you today?"
  ],
  [
    "I would like something to order in.",
    "Sure! I can help you with that. What kind of food would you like?"
  ]
]


# Get current location of the user
@staticmethod
def current_location() -> tuple[float, float]:
    """Using the Geocode Python library, get the current location of the user.

    Returns
    -------
    :returns: A (latitude, longitude) tuple with the user's current location
    """
    geoloc = geocoder.ip("me")
    return geoloc.latlng


# Get nearby restaurants using Google Maps Places API
@staticmethod
def nearby_restaurants(loc: tuple[float, float]) -> str:
    """Given the location of the user, provide the nearby restaurants in a JSON
    format.
    """
    # Get current locaiton from user
    lat, long = loc

    # Send a POST Request to the Google Maps Places API
    headers = {
        "Content-Type": "application/json",
        "X-Goog-API-Key": MAPS_API_KEY,
        "X-Goog-FieldMask": "places.displayName"
    }
    data = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": long
                },
                "radius": 100.0
            }
        }
    }
    url = "https://places.googleapis.com/v1/places:searchNearby"

    maps_places_request = requests.post(
        url, headers=headers, data=data, timeout=50
    )

    return maps_places_request.text


# Setup necessary APIs
def setup():
    """Setup all the necessary APIs for the system to work"""
    # Setup PaLM 2
    palm.configure(api_key=PALM_2_API_KEY)

    # Add location and nearby restaurants to the CONTEXT
    loc = current_location()
    loc_str = f"My location in latitude, longitude format: {loc}"
    restaurants = f"Restaurants near me: {nearby_restaurants(loc)}"
    final_context = f"{loc_str}\n {restaurants}\n {CONTEXT}\n"

    MESSAGES.append("NEXT REQUEST")

    response = palm.chat(
        **DEFAULTS,
        context=final_context,
        examples=EXAMPLES,
        messages=MESSAGES
    )

    return response


# Using nearby restaurants available, get a response from PaLM 2 given a prompt
def chat(response: list[str, str], prompt: str) -> str:
    """Given a prompt from the user, send the prompt to PaLM 2 given nearby
    restaurants (information from Google Maps APIs) and receive an output
    from PaLM 2

    Arguments
    ---------
    :param prompt [str]: The prompt provided by the user

    Returns
    -------
    :returns: The response from PaLM 2

    """
    # Converse with PaLM 2
    response = response.reply(prompt)
    return response.last
