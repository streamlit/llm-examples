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

# PaLM 2 Hyperparameters, Google PaLM2 & Maps API Keys
temperature = 0.25
top_k = 10
top_p = 1.0
palm_2_api_key = PALM_2_API_KEY
maps_api_key = MAPS_API_KEY