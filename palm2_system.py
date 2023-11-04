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

__author__ = "Akhil Karra"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Akhil Karra"
__email__ = "akarra@andrew.cmu.edu"
__status__ = "Prototype"

# PaLM 2 Hyperparameters, 
temperature = 0.25
top_k = 10
top_p = 1.0
context = """I am currently in Pittsburgh, Pennsylvania. I don't know what to order.

Your job is to ask questions to me about my food preferences, my dietary restrictions, and my current mood and then recommend restaurants for delivery or pickup to me. Have a cheerful conversation with me. Follow this step-by-step process. Make sure to ask me these questions one response at a time. Don't reveal all the questions to me in one go.
1) Ask me about current mood.
2) Ask whether I would like delivery or pickup.
2) Ask me about what kind of food I would like to eat. 
3) Ask me about my dietary restrictions. 
4) Using all of the information you have gathered above, give me the top 5 restaurant recommendations back.

Important note: DO NOT GIVE ME ANY RESTAURANT RECOMMENDATIONS UNTIL YOU REACH STEP 4.

Stay in character for every response you give me. Keep your responses short. Ask one and only one question per response. Feel free to ask me questions, too. 
"""

# Google PaLM 2 & Maps API Keys
palm_2_api_key = PALM_2_API_KEY
maps_api_key = MAPS_API_KEY


# Get current location of the user
@staticmethod
def current_location():
    """Using the appropriate Google Maps API, get the current location of the
    user.
    """
    return


# Get nearby restaurants using Google Maps
@staticmethod
def nearby_restaurants(location) -> str:
    """Given the location of the user, provide the nearby restaurants in a JSON
    format.
    """
    return ""


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
    return ""
