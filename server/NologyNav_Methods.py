import os
import sys
import json
import requests
from dotenv import load_dotenv

from Google_API_Handler import retrieve_navigation_payload

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

def count_waypoints(navigation_data):
    return len(navigation_data["routes"][0]["legs"][0]["steps"])

def distance_travelled(navigation_data):
    if "km" in (navigation_data["routes"][0]["legs"][0]["distance"]["text"]):
        miles = '{:.1f}'.format((navigation_data["routes"][0]["legs"][0]["distance"]["value"]/1000)/1.609)
        return (f"{miles} mi")
    return (navigation_data["routes"][0]["legs"][0]["distance"]["text"])

def total_time(navigation_data):
    return (navigation_data["routes"][0]["legs"][0]["duration"]["text"])

def lat_lng(navigation_data):
    lat_long_locations = ({"lat": navigation_data["routes"][0]["legs"][0]["start_location"]["lat"], "lng": navigation_data["routes"][0]["legs"][0]["start_location"]["lng"]}, 
                          { "lat": navigation_data["routes"][0]["legs"][0]["end_location"]["lat"], "lng": navigation_data["routes"][0]["legs"][0]["end_location"]["lng"] })
    return lat_long_locations

def avg_speed(navigation_data):
    distanceInMeters = navigation_data["routes"][0]["legs"][0]["distance"]["value"]
    timeInSeconds = navigation_data["routes"][0]["legs"][0]["duration"]["value"]

    distanceInMiles = float('{:.1f}'.format(distanceInMeters * 0.0006213712))
    timeInHours = float('{:.1f}'.format(timeInSeconds/60/60))

    averageMph = float('{:.1f}'.format(distanceInMiles/timeInHours))

    return averageMph

def modes_of_transportation(navigation_data):
    steps = navigation_data["routes"][0]["legs"][0]["steps"]
    travelTypes = []
    for step in steps: 
        if step["travel_mode"].lower() not in travelTypes:
            travelTypes.append(step["travel_mode"].lower())
        if "maneuver" in step and "ferry" in step["maneuver"].lower() and step["maneuver"].lower() not in travelTypes:
            travelTypes.append(step["maneuver"].lower())

    return travelTypes

def summary(navigation_data):
    outputStr = "This journey will take " + str(navigation_data["total_time"]) + " over " + str(navigation_data["distance_travelled"])
    outputStr += ", covering " + str(navigation_data["waypoints"]) + " waypoints at an average speed of " + str(navigation_data["avg_speed"]) + ". "
    
    if (len(navigation_data["modes_of_transportation"]) == 1):
        outputStr += "It will only require " + str(navigation_data["modes_of_transportation"][0])
    elif (len(navigation_data["modes_of_transportation"]) == 2):
        outputStr += "In addition to " + str(navigation_data["modes_of_transportation"][0]) + ", you will also need to use " + str(navigation_data["modes_of_transportation"][1])
    else:
        outputStr += "In addition to " + str(navigation_data["modes_of_transportation"][0]) + ", you will also need to use " + str(navigation_data["modes_of_transportation"][1]) + " and " + str(navigation_data["modes_of_transportation"][2])
    outputStr = outputStr.replace("ferry-train", "an auto-train").replace("ferry", "a ferry")
    outputStr += ", at a starting (Lat/Long) of (" + str(navigation_data["lat_lng"][0]['lat']) + ", " + str(navigation_data["lat_lng"][0]['lng']) +  "), and ending at (" + str(navigation_data["lat_lng"][1]['lat']) + ", " + str(navigation_data["lat_lng"][1]['lng']) + ")"
    return outputStr

def retrieve_data_from_google(locations):
    requestOptions = {
        "origin": locations["origin"],
        "destination": locations["destination"]
    }
    
    result = retrieve_navigation_payload(requestOptions)
    error_dict = {"error": ""}

    if result["geocoded_waypoints"][0]["geocoder_status"] == "OK" and result["geocoded_waypoints"][1]["geocoder_status"] == "OK" and result["status"] == "ZERO_RESULTS":
        error_dict["error"] = f"We are unable to find a driving route between {locations['origin']} and {locations['destination']}."
        
    if result["geocoded_waypoints"][0]["geocoder_status"] == "ZERO_RESULTS" and result["geocoded_waypoints"][1]["geocoder_status"] == "ZERO_RESULTS":
        error_dict["error"] = f"We are unable to find the origin and destination."
    elif result["geocoded_waypoints"][0]["geocoder_status"] == "ZERO_RESULTS":
        error_dict["error"] = "We are unable to find that origin."
    elif result["geocoded_waypoints"][1]["geocoder_status"] == "ZERO_RESULTS":
        error_dict["error"] = "We are unable to find that destination."
    else:
        pass
    
    return result if error_dict["error"] == "" else error_dict   
      