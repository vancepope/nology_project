import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

def retrieve_navigation_payload(options):
    url = url_builder(options)

    response = requests.post(url)
    result = response.json()

    return result

def url_builder(options):
    urlOptions = ""
    urlPrefix = "https://maps.googleapis.com/maps/api/directions/json"

    for optionName in options: 
        charToAdd = "?" if len(urlOptions) == 0 else "&"
        if(type(options[optionName]) != tuple):
            urlOptions += charToAdd + optionName + "=" + options[optionName]
        else:
            optionList = ""
            for optionSubsection in options[optionName]: 
                optionList += optionSubsection + "|"
            optionList = optionList[:-1]
            urlOptions += charToAdd + optionName + "=" + optionList

    urlOptions += "&key=" + API_KEY

    return urlPrefix + urlOptions

def getNumberOfRoutes(route_data):
    return len(route_data["routes"])

def get_steps(route_data, legNumber):
    return route_data["routes"][0]["legs"][legNumber]["steps"]

def get_arrival_time(route_data, legNumber):
    if "arrival_time" in route_data["routes"][0]["legs"][legNumber]:
        return route_data["routes"][0]["legs"][legNumber]["arrival_time"]
    else:
        return False

def get_departure_time(route_data, legNumber):
    if "departure_time" in route_data["routes"][0]["legs"][legNumber]:
        return route_data["routes"][0]["legs"][legNumber]["departure_time"]
    else:
        return False

def verify_route_found(route_data):
    if get_num_routes(route_data) > 0:
        return True
    else:
        return False

def get_num_routes(route_data):
    return len(route_data["routes"])

def get_duration_value(route_data, legNumber=0):
    return route_data["routes"][0]["legs"][legNumber]["duration"]["value"]

def get_duration_in_traffic_value(route_data, legNumber=0):
    if "duration_in_traffic" in route_data["routes"][0]["legs"][legNumber]:
        return route_data["routes"][0]["legs"][legNumber]["duration_in_traffic"]["value"]
    else:
        return False

def getUnit(route_data):
    return route_data["routes"][0]["legs"][0]["distance"]["text"]

def get_waypoints(route_data):
    if "error_message" in route_data:
        return {"error": "Transit may not be used as a mode when adding waypoints in between an origin and destination."}
    else:
        return len(route_data["geocoded_waypoints"])

def get_start_address(route_data):
    return route_data["routes"][0]["legs"][0]["start_address"]

def get_transit_mode(route_data):
    steps = get_steps(route_data,0)
    
    for step in steps:
        if "transit_details" in step:
            if "line" in step["transit_details"]:
                print("******************************")
                print(step["transit_details"]["line"]["vehicle"]["name"])
                return  step["transit_details"]["line"]["vehicle"]["name"]
    return route_data["routes"][0]["legs"][0]["steps"][0]["transit_details"]["line"]["vehicle"]["name"]

def get_travel_mode(route_data):
    if "fare" in route_data["routes"][0]:
        return {"travel_mode": "TRANSIT", "duration": route_data["routes"][0]["legs"][0]["duration"]["value"]}
    else:
        return {"travel_mode": route_data["routes"][0]["legs"][0]["steps"][0]["travel_mode"], "duration": route_data["routes"][0]["legs"][0]["duration"]["value"]}
    
def get_transit_route_preferences(route_data):
    steps = get_steps(route_data,0)
    walking_duration = 0
    transit_duration = 0

    for index in range(len(steps)):
        if "steps" in steps[index]:
            walking_duration += steps[index]["duration"]["value"]
        if "transit_details" in steps[index]:
            transit_duration += steps[index]["duration"]["value"]
        
    return {"duration": route_data["routes"][0]["legs"][0]["duration"]["value"], "walking_duration": walking_duration, "transit_duration": transit_duration}