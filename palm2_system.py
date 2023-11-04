#!/usr/bin/env python

"""PaLM 2 Restaurant Recommender System

This is a library that interfaces with the Google Maps API and the PaLM 2 API
to create the backend for the restaurant recommender system.

As soon as the user logs into the app, the Google Maps API extracts all nearby
restaurants and loads it into the context of the PaLM 2 LLM. The user then
provides prompts which are fed into the PaLM 2 LLM, and then this library
extracts the resopnse from the model to give back to the front end and then the
user.
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
defaults = {
    'model': 'models/chat-bison-001',
    'temperature': 0.25,
    'top_k': 10,
    'top_p': 1,
}
messages = []
context = """I want to order some food for delivery or pickup but I don't know
what to get.

Your job is to ask questions to me about my food preferences, my dietary
restrictions, and my current mood and then recommend restaurants for delivery
or pickup to me. Have a cheerful conversation with me. Follow this step-by-step
process. Make sure to ask me these questions one response at a time. Don't
reveal all the questions to me in one go.
1) Ask me about current mood.
2) Ask whether I would like delivery or pickup.
2) Ask me about what kind of food I would like to eat.
3) Ask me about my dietary restrictions.
4) Using all of the information you have gathered above, give me the top 5
restaurant recommendations back.

Important note: DO NOT GIVE ME ANY RESTAURANT RECOMMENDATIONS UNTIL YOU REACH
STEP 4.

Stay in character for every response you give me. Keep your responses short.
Ask one and only one question per response. Feel free to ask me questions, too.
"""
examples = [
  [
    "Hi",
    "Hello! How can I help you today?"
  ],
  [
    "I would like something to order in.",
    "Sure! I can help you with that. What kind of food would you like?"
  ]
]

# Google PaLM 2 & Maps API Keys
palm_2_api_key = PALM_2_API_KEY
maps_api_key = MAPS_API_KEY


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
def nearby_restaurants(loc) -> str:
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
                    "longitude": long},
                "radius": 100.0
            }
        }
    }
    url = "https://places.googleapis.com/v1/places:searchNearby"
    maps_places_request = requests.post(url, headers=headers, data=data)

    return maps_places_request.text


# Setup necessary APIs (MUST USE THIS BEFORE USING CHAT)
def setup():
    """Setup all the necessary APIs for the system to work"""
    # Setup PaLM 2
    palm.configure(api_key=palm_2_api_key)


# Using nearby restaurants available, get a response from PaLM 2 given a prompt
def chat(prompt: str) -> str:
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
    # Add location and nearby restaurants to the context
    loc = current_location()
    loc_str = f"My location in latitude, longitude format: {loc}"
    restaurants = f"Restaurants near me: {nearby_restaurants(loc)}"
    final_context = f"{loc_str}\n {restaurants}\n {context}\n"

    # Converse with PaLM 2
    messages.append("NEXT REQUEST")
    response = palm.chat(
        **defaults,
        context=final_context,
        examples=examples,
        messages=messages
    )

    return response.last
