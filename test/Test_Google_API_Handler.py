import os
import sys
import json
import time
import pytest
import logging
from pytest import approx

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

from server import Google_API_Handler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestGoogleApiHandler:
    @pytest.mark.parametrize("input, output", [
        ({"origin": "San Diego", 
        "destination": "Los Angeles"},
        "https://maps.googleapis.com/maps/api/directions/json?origin=San Diego&destination=Los Angeles&key="+API_KEY),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "mode": "walking"},
        "https://maps.googleapis.com/maps/api/directions/json?origin=San Diego&destination=Los Angeles&mode=walking&key="+API_KEY),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "avoid": ("ferry", "tolls")},
        "https://maps.googleapis.com/maps/api/directions/json?origin=San Diego&destination=Los Angeles&avoid=ferry|tolls&key="+API_KEY)
        ])  
    def test_url_builder(self, input, output):
        logger.info("Sending input options to URL builder")
        urlResult = Google_API_Handler.url_builder(input)

        logger.info("Verifying resulting URL matches expected output")
        assert urlResult == output

    @pytest.mark.parametrize("input, output", [
        ({"origin": "Junipero Serra Park and Ride, San Juan Capistrano, CA 92675", 
        "destination": "Emoji Rock, Laguna Beach, CA 92651",
        "avoid": ("tolls")},
        {"expected": False, "text": "Toll road"}),
        ({"origin": "Junipero Serra Park and Ride, San Juan Capistrano, CA 92675", 
        "destination": "Emoji Rock, Laguna Beach, CA 92651",
        "avoid": ("ferries")},
        {"expected": True, "text": "Toll road"})
        ])  
    def test_avoid_tolls(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        wasFound = False

        logger.info("Iterating over steps to verify that '" + output["text"] + "' is " + ("found" if output["expected"] else "not found"))
        steps = Google_API_Handler.get_steps(result, 0)
        for step in steps:
            if output["text"] in step["html_instructions"]:
                wasFound = True

        assert wasFound == output["expected"]

    @pytest.mark.parametrize("input, output", [
        ({"origin": "San Diego International Airport", 
        "destination": "Torrey Pines Golf Course, 11480 N Torrey Pines Rd, La Jolla, CA 92037",
        "avoid": ("highways")},
        {"expected": False, "text": "I-5 N"}),
        ({"origin": "San Diego International Airport", 
        "destination": "Torrey Pines Golf Course, 11480 N Torrey Pines Rd, La Jolla, CA 92037",
        "avoid": ("ferries")},
        {"expected": True, "text": "I-5 N"})
        ])  
    def test_avoid_highways(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        wasFound = False

        logger.info("Iterating over steps to verify that '" + output["text"] + "' is " + ("found" if output["expected"] else "not found"))
        steps = Google_API_Handler.get_steps(result, 0)
        for step in steps:
            if output["text"] in step["html_instructions"]:
                wasFound = True

        assert wasFound == output["expected"]

    @pytest.mark.parametrize("input, output", [
        ({"origin": "Seattle, Washington", 
        "destination": "Bainbridge Island, Washington",
        "avoid": ("ferries")},
        {"expected": False}),
        ({"origin": "Seattle, Washington", 
        "destination": "Bainbridge Island, Washington"},
        {"expected": True})
        ])  
    def test_avoid_ferries(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        wasFound = False

        logger.info("Iterating over steps to verify that Ferry maneuver is " + ("found" if output["expected"] else "not found"))
        steps = Google_API_Handler.get_steps(result, 0)
        for step in steps:
            if "maneuver" in step and "ferry" in step["maneuver"]:
                wasFound = True

        assert wasFound == output["expected"]

    #note: ferries and tolls often intermixed, so sometimes blocking one will/won't block the other.
    @pytest.mark.parametrize("input, output", [
        ({"origin": "Seattle, Washington", 
        "destination": "Bainbridge Island, Washington"},
        {"ferries": True, "highways": False, "tolls": True, "highwayText": "I-5"}),
        ({"origin": "Seattle, Washington", 
        "destination": "Bainbridge Island, Washington",
        "avoid": ("ferries", "tolls")},
        {"ferries": False, "highways": True, "tolls": False, "highwayText": "I-5"}),
        ({"origin": "Seattle, Washington", 
        "destination": "Bainbridge Island, Washington",
        "avoid": ("tolls", "highways")},
        {"ferries": True, "highways": False, "tolls": True, "highwayText": "I-5"}),
        ({"origin": "Main Street Dog Park, 2990 Main St, Alameda, CA 94501", 
        "destination": "Oracle Park",
        "avoid": ("ferries", "highways")},
        {"ferries": False, "highways": False, "tolls": True, "highwayText": "880"}),
        ({"origin": "Seattle, Washington", 
        "destination": "Bainbridge Island, Washington",
        "avoid": ("ferries", "highways", "tolls")},
        {"ferries": False, "highways": False, "tolls": False, "highwayText": "I-5"})
        ])  
    def test_avoid_multiple(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        ferryFound = False
        highwaysFound = False
        tollsFound = False

        logger.info("Iterating over steps to verify that:")
        logger.info(" - Ferry maneuver is " + ("found" if output["ferries"] else "not found"))
        logger.info(" - Highways are " + ("found" if output["highways"] else "not found"))
        logger.info(" - Tolls are " + ("found" if output["tolls"] else "not found"))
        steps = Google_API_Handler.get_steps(result, 0)
        for step in steps:
            if not output["ferries"] and "maneuver" in step:
                print(step["maneuver"])
            if "maneuver" in step and "ferry" in step["maneuver"]:
                ferryFound = True
            if output["highwayText"] in step["html_instructions"]:
                highwaysFound = True
            if "Toll road" in step["html_instructions"]:
                tollsFound = True

        assert ferryFound == output["ferries"]
        assert highwaysFound == output["highways"]
        assert tollsFound == output["tolls"]

    oneDayInSeconds = 24 * 60 * 60 #hh ** mm ** ss

    #Per API docs, arrival_time is only available for transit mode (not driving, walking, biking, etc), hence the inclusion of mode and transit_mode options
    #arrival_time must be an integer
    @pytest.mark.parametrize("input, output", [
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "mode": "transit",
        "transit_mode": "bus"},
        {"expected": False}),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "mode": "transit",
        "transit_mode": "bus",
        "arrival_time": str(int(time.time() + oneDayInSeconds))},
        {"expected": True}),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "mode": "transit",
        "transit_mode": "bus",
        "arrival_time": str(int(time.time() - oneDayInSeconds))},
        {"error": True})
        ])  
    def test_arrival_time(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        if "error" in output:
            logger.info("Verifying no route was found due to arrival time being in the past.")
            assert output["error"] == Google_API_Handler.verify_route_found(result)
        else:
            logger.info("Verifying that arrival_time exists as expected based on calculated variance")
            arrival_time = Google_API_Handler.get_arrival_time(result, 0)

            #30000 seconds ends up being around 8 hours, as bus schedules vary quite alot. This is still less than one day, which is the difference between the 
            if output["expected"] == False:
                calculatedArrivalTime = int(time.time()) + Google_API_Handler.get_duration_value(result, 0)
                assert arrival_time["value"] == approx(calculatedArrivalTime, abs=30000)
            else:
                print(type(arrival_time["value"]))
                assert arrival_time["value"] == approx(int(input["arrival_time"]), abs=30000)


    @pytest.mark.parametrize("input, output", [
        ({"origin": "San Diego", 
        "destination": "Los Angeles"},
        {"expected": False}),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "departure_time": str(int(time.time() + oneDayInSeconds/4))},
        {"expected": True}),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "departure_time": str(int(time.time() - oneDayInSeconds/4))},
        {"error": "departure_time is in the past. Traffic information is only available for future and current times."})
        ])  
    def test_departure_time(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        if "error" in output:
            logger.info("Verifying no route was found due to departure time being in the past.")
            assert output["error"] == result["error_message"]
        else:
            logger.info("Verifying that departure_time exists as expected based on calculated variance")
            duration_time_traffic_value = Google_API_Handler.get_duration_in_traffic_value(result, 0)
            duration_time = Google_API_Handler.get_duration_value(result, 0)

            if output["expected"] == False:
                assert duration_time_traffic_value == output["expected"]
            else:
                assert duration_time == approx(int(duration_time_traffic_value), int(duration_time_traffic_value)/2)

    @pytest.mark.parametrize("input, output", [
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "mode": "transit",
        "transit_mode": "bus",
        "arrival_time": str(int(time.time() + oneDayInSeconds))},
        {"expected": True}),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "mode": "transit",
        "transit_mode": "bus",
        "departure_time": str(int(time.time() + oneDayInSeconds/4)),
        "arrival_time": str(int(time.time() + oneDayInSeconds))},
        {"expected": True}),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "mode": "transit",
        "transit_mode": "bus",
        "departure_time": str(int(time.time() + oneDayInSeconds/4))},
        {"expected": True})
        ])  
    def test_arrival_and_departure_time(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        if "arrival_time" in input:
            logger.info("Verifying Arrival Time matches, as it takes priority over Departure")
            arrival_time = Google_API_Handler.get_arrival_time(result, 0)
            assert arrival_time["value"] == approx(int(input["arrival_time"]), abs=50000)
        else:
            logger.info("Verifying Departure Time matches, as Arrival Time was not specified")
            departure_time = Google_API_Handler.get_departure_time(result, 0)
            assert departure_time["value"] == approx(int(input["departure_time"]), abs=50000)

    @pytest.mark.parametrize("input, output", [
    ({"origin": "San Diego, California",
    "destination": "Los Angeles, California",
    "units": "metric"},
    {"expected": "km"}),
    ({"origin": "San Diego, California",
    "destination": "Los Angeles, California",
    "units": "imperial"},
    {"expected": "mi"})
    ])    
    def test_units_displayed(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        unit = Google_API_Handler.getUnit(result)
        logger.info("checking unit measurements for assertion")
        
        assert unit[-2:] == output["expected"]

    @pytest.mark.parametrize("input, output", [
    ({"origin": "San Diego", "destination": "Los Angeles", "mode": "driving", "waypoints": "[{\"location\":\"Long Beach,CA\", \"stopover\": True}]"}, {"waypoint_num": 3}),
    ({"origin": "San Diego", "destination": "Los Angeles", "mode": "driving", "waypoints": '[{"location": {"lat": "33.7701° N", "lng": "118.1937° W"}, "stopover": True}]'}, {"waypoint_num": 3}),
    ({"origin": "San Diego", "destination": "Los Angeles", "mode": "driving", "waypoints": "place_id:ChIJWdeZQOjKwoARqo8qxPo6AKE"}, {"waypoint_num": 3}),
    ({"origin": "San Diego Convention Center", "destination": "Little Italy San Diego", "mode": "walking", "waypoints": "[{\"location\":\"Kettner Exchange\", \"stopover\": True}]"}, {"waypoint_num": 3}),
    ({"origin": "San Diego Convention Center", "destination": "Little Italy San Diego", "mode": "walking", "waypoints": '[{"location": {"lat": "32.7254° N", "lng": "117.1698° W"}, "stopover": True}]'}, {"waypoint_num": 3}),
    ({"origin": "San Diego Convention Center", "destination": "Little Italy San Diego", "mode": "walking", "waypoints": "place_id:ChIJs7N7gbRU2YARkSPbQpAGTUM"}, {"waypoint_num": 3}),
    ({"origin": "South Mission Beach", "destination": "La Jolla", "mode": "bicycling", "waypoints": "[{\"location\":\"Mavericks Pacific Beach\", \"stopover\": True}]"}, {"waypoint_num": 3}),
    ({"origin": "South Mission Beach", "destination": "La Jolla", "mode": "bicycling", "waypoints": '[{"location": {"lat": "32.7970° N", "lng": "117.2546° W"}, "stopover": True}]'}, {"waypoint_num": 3}),
    ({"origin": "South Mission Beach", "destination": "La Jolla", "mode": "bicycling", "waypoints": "place_id:ChIJZ8ozSu0B3IARVsg9xEXxzOU"}, {"waypoint_num": 3}),
    ({"origin": "San Diego", "destination": "Los Angeles", "mode": "transit", "waypoints": "place_id:ChIJWdeZQOjKwoARqo8qxPo6AKE"}, {"error": "Transit may not be used as a mode when adding waypoints in between an origin and destination."}),
    ({"origin": "San Diego Convention Center", "destination": "Little Italy San Diego", "mode": "transit", "waypoints": "place_id:ChIJs7N7gbRU2YARkSPbQpAGTUM"}, {"error": "Transit may not be used as a mode when adding waypoints in between an origin and destination."}),
    ({"origin": "South Mission Beach", "destination": "La Jolla", "mode": "transit", "waypoints": "place_id:ChIJZ8ozSu0B3IARVsg9xEXxzOU"}, {"error": "Transit may not be used as a mode when adding waypoints in between an origin and destination."}),
    ])  
    def test_waypoints(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)
        waypoints = Google_API_Handler.get_waypoints(result)
        logger.info("Checking number of waypoints for assertion")
        
        if "error_message" in result:
            assert waypoints["error"] == output["error"]
        else:    
            assert waypoints == output["waypoint_num"]
    
    @pytest.mark.parametrize("input, output", [
        ({"origin": "Tokyo, Japan",
        "destination": "Yokohama, Japan",
        "language": "ja"},
        {"expected": "日本、東京都"}),
        ({"origin": "Tokyo, Japan",
        "destination": "Yokohama, Japan",
        "language": "en"},
        {"expected": "Tokyo, Japan"}),
        ({"origin": "San Diego, California",
        "destination": "Los Angeles, California",
        "language": "en"},
        {"expected": "San Diego, CA, USA"}),
        ({"origin": "San Diego, California",
        "destination": "Los Angeles, California",
        "language": "aopsdkopasdk"},
        {"expected": "San Diego, CA, USA"}),
    ])
    def test_language(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        logger.info("Retrieving start address to test set language")
        language = Google_API_Handler.get_start_address(result)
        
        assert language == output["expected"]

    @pytest.mark.parametrize("input, output", [
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "alternatives": "false"},
        {"expected": 1}),
        ({"origin": "San Diego", 
        "destination": "Los Angeles",
        "alternatives": "true"},
        {"expected": 2}),
        ({"origin": "San Diego International Airport", 
        "destination": "San Diego Zoo, 2920 Zoo Dr, San Diego, CA 92101",
        "alternatives": "false"},
        {"expected": 1}),
        ({"origin": "San Diego International Airport", 
        "destination": "San Diego Zoo, 2920 Zoo Dr, San Diego, CA 92101",
        "alternatives": "true"},
        {"expected": 2})
        ])  
    def test_alternatives(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)

        logger.info("Verifying Number of routes = " + str(output["expected"]))
        numberOfRoutes = Google_API_Handler.get_num_routes(result)

        if output["expected"] == 1:
            assert numberOfRoutes == output["expected"]
        else:
            assert numberOfRoutes >= output["expected"]

    @pytest.mark.parametrize("input, output", [
        ({"origin": "San Diego, CA, USA", 
        "destination": "Los Angeles, CA, USA",
        "mode": "transit", "transit_mode": "bus"},
        {"expected": "Bus"}),
        ({"origin": "Brooklyn, NY, USA", 
        "destination": "Manhattan, New York, NY, USA",
        "mode": "transit", "transit_mode": "subway"},
        {"expected": "Subway"}),
        ({"origin": "Seattle, WA, USA", 
        "destination": "Los Angeles, CA, USA",
        "mode": "transit", "transit_mode": "train"},
        {"expected": "Train"}),
        ({"origin": "San Diego, CA, USA", 
        "destination": "Los Angeles, CA, USA",
        "mode": "transit", "transit_mode": "tram"},
        {"expected": "Light rail"}),
        ({"origin": "San Diego, CA, USA", 
        "destination": "Los Angeles, CA, USA",
        "mode": "transit", "transit_mode": "rail"},
        {"expected": "Train"})
        ])  
    def test_transit_mode(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)
        
        logger.info("Finding specific transit mode")
        travel_mode = Google_API_Handler.get_transit_mode(result)

        assert travel_mode == output["expected"]

    def test_traffic_model(self):
        options = {
            "origin": "San Diego", 
            "destination": "Los Angeles",
            "departure_time": str(int(time.time()))
        }

        logger.info("Retrieving API Payload with defaults")
        resultDefaults = Google_API_Handler.retrieve_navigation_payload(options)

        logger.info("Retrieving API Payload with Best Guess")
        options["traffic_model"] = "best_guess"
        resultBestGuess = Google_API_Handler.retrieve_navigation_payload(options)

        logger.info("Retrieving API Payload with Pessimistic")
        options["traffic_model"] = "pessimistic"
        resultPessimistic = Google_API_Handler.retrieve_navigation_payload(options)

        logger.info("Retrieving API Payload with Optimistic")
        options["traffic_model"] = "optimistic"
        resultOptimistic = Google_API_Handler.retrieve_navigation_payload(options)

        logger.info("Verifying Default Options match Best Guess traffic model")
        assert Google_API_Handler.get_duration_in_traffic_value(resultDefaults) == Google_API_Handler.get_duration_in_traffic_value(resultBestGuess)
        logger.info("Verifying Optimistic/Default Traffic is faster than Pessimistic Model")
        assert Google_API_Handler.get_duration_in_traffic_value(resultDefaults) < Google_API_Handler.get_duration_in_traffic_value(resultPessimistic)
        logger.info("Verifying Optimistic/Default Traffic is slower than Optimistic Model")
        assert Google_API_Handler.get_duration_in_traffic_value(resultDefaults) > Google_API_Handler.get_duration_in_traffic_value(resultOptimistic)
        
    @pytest.mark.parametrize("input, output", [
        ({"origin": "Encanto,San Diego,Ca", "destination": "La Jolla", "mode": "driving"}, {"travel_mode": "DRIVING", "duration": 9183}),
        ({"origin": "Encanto,San Diego,Ca", "destination": "La Jolla", "mode": "walking"}, {"travel_mode": "WALKING", "duration": 21985}),
        ({"origin": "Encanto,San Diego,Ca", "destination": "La Jolla", "mode": "bicycling"}, {"travel_mode": "BICYCLING", "duration": 6998}),
        ({"origin": "Encanto,San Diego,Ca", "destination": "La Jolla", "mode": "transit"}, {"travel_mode": "TRANSIT", "duration": 5549}),
        ({"origin": "Encanto,San Diego,Ca", "destination": "La Jolla", "mode": "transit", "transit_mode": "bus", "transit_routing_preference": "fewer_transfers"}, {"travel_mode": "TRANSIT", "duration": 10533}),
        ({"origin": "Encanto,San Diego,Ca", "destination": "La Jolla", "mode": "transit", "transit_mode": "bus", "transit_routing_preference": "less_walking"}, {"travel_mode": "TRANSIT", "duration": 6867}),
    ])  
    def test_travel_modes(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        result = Google_API_Handler.retrieve_navigation_payload(input)
        data = Google_API_Handler.get_travel_mode(result)
        logger.info("Checking travel modes for assertion")
        
        assert data["travel_mode"] == output["travel_mode"]
        assert data["duration"] == approx(output["duration"], output["duration"]/10)

    @pytest.mark.parametrize("input, output", [
        ({"origin": "Brooklyn", "destination": "Manhattan", "mode": "transit", "transit_mode": "bus"}, {"walking_duration": 2070, "transit_duration": 2130}),
        ({"origin": "Brooklyn", "destination": "Manhattan", "mode": "transit", "transit_mode": "subway"}, {"walking_duration": 627, "transit_duration": 2250}),
        ({"origin": "Brooklyn", "destination": "Manhattan", "mode": "transit", "transit_mode": "tram"}, {"walking_duration": 2070, "transit_duration": 2130}),
        ({"origin": "Brooklyn", "destination": "Manhattan", "mode": "transit", "transit_mode": "train"}, {"walking_duration": 690, "transit_duration": 2460}),
        ({"origin": "Brooklyn", "destination": "Manhattan", "mode": "transit", "transit_mode": "rail"}, {"walking_duration": 627, "transit_duration": 2250})
    ])
    def test_route_preferences(self, input, output):
        logger.info("Retrieving configured Google Directions API Payload")
        
        input["transit_routing_preference"] = "fewer_transfers"
        fewer_transfers_data = Google_API_Handler.retrieve_navigation_payload(input)
        
        input["transit_routing_preference"] = "less_walking"
        less_walking_data = Google_API_Handler.retrieve_navigation_payload(input)
        
        fewer_transfers_result = Google_API_Handler.get_transit_route_preferences(fewer_transfers_data)
        less_walking_result = Google_API_Handler.get_transit_route_preferences(less_walking_data)

        
        logger.info("Checking route preferences for assertion")
        assert less_walking_result["walking_duration"] <= output["walking_duration"]
        assert fewer_transfers_result["transit_duration"] != output["transit_duration"]