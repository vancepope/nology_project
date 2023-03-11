import os
import sys
import json
import pytest
import logging
from pytest import approx 
from flask import Flask, request

from server import NologyNav
from server.NologyNav import create_app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestNavigationManager:
    @pytest.mark.parametrize("input, output",[
        (("Disneyland_to_Seaworld.json"), (49)),
        (("London_to_Paris.json"), (51))
    ])
    def test_count_waypoints(self, input, output):
        logger.info("Loading Test File: " + input)
        with open("./test/routes/" + input) as test_file:
            test_data_contents = test_file.read()
        testData = json.loads(test_data_contents)
        logger.info("calling 'count_waypoints' function with test data to get result")
        result = NologyNav.count_waypoints(testData)   

        assert result == output

    @pytest.mark.parametrize("input, output", [
        (("Disneyland_to_UniversalStudios.json"), ("35.1 mi")),
        (("London_to_Paris.json"), ("295.5 mi"))
    ])
    def test_distance_travelled(self, input, output):
        logger.info("Loading Test File: " + input)
        with open("test/routes/" + input) as test_file:
            test_data_contents = test_file.read()
        testData = json.loads(test_data_contents)

        logger.info("Calling modes_of_transportation function with test data to get result")
        result = NologyNav.distance_travelled(testData)
        assert result == output
        assert type(result) == str
        logger.info(f'Expected output: distance_travelled == {output} | Actual output: distance_travelled == "{result}"')
    
    @pytest.mark.parametrize("input, output", [
        (("Disneyland_to_UniversalStudios.json"), ("49 mins")),
        (("London_to_Paris.json"), ("5 hours 50 mins"))
    ])
    def test_total_time(self, input, output):
        logger.info("Loading Test File: " + input)
        with open("./test/routes/" + input) as test_file:
            test_data_contents = test_file.read()
        testData = json.loads(test_data_contents)

        logger.info("Calling 'total_time' function with test data to get result")
        result = NologyNav.total_time(testData)

        logger.info("Verifying Total Time result matches: " + output)
        assert result == output
        
    @pytest.mark.parametrize("input, output", [
        (("Disneyland_to_UniversalStudios.json"), 
        ({"lat" : 33.8160897, "lng" : -117.9225226}, {"lat" : 34.1358593, "lng" : -118.3511633})),
        (("London_to_Paris.json"), 
        ({"lat" : 51.5072126, "lng" : -0.1275835}, {"lat" : 48.85637149999999, "lng" : 2.3532147})),
    ])
    def test_lat_lng(self, input, output):
        logger.info("Loading Test File: " + input)
        with open("./test/routes/" + input) as test_file:
            test_data_contents = test_file.read()
        testData = json.loads(test_data_contents)

        logger.info("Calling 'lat_lng' function with test data to get result")
        result = NologyNav.lat_lng(testData)

        logger.info(f"this is a tuple: %s" % (output,))
        assert result[0]["lat"] == output[0]["lat"]
        assert result[0]["lng"] == output[0]["lng"]
        assert result[1]["lat"] == output[1]["lat"]
        assert result[1]["lng"] == output[1]["lng"]
    
    @pytest.mark.parametrize("input, output",[
        (("Disneyland_to_Seaworld.json"), (69.0)),
        (("London_to_Paris.json"), (50.9))
    ])
    def test_avg_speed(self, input, output):
        logger.info("Loading Test File: " + input)
        with open("test/routes/" + input) as test_file:
            test_data_contents = test_file.read()
        testData = json.loads(test_data_contents)

        logger.info("Calling 'avg_speed' function with test data to get result")
        result = NologyNav.avg_speed(testData)

        logger.info("Verifying 'avg_speed' result is: " + str(output))
        assert result == output
    
    @pytest.mark.parametrize("input, output", [
        (("Disneyland_to_UniversalStudios.json"), ["driving"]),
        (("London_to_Paris.json"), ["driving", "ferry-train"]),
    ])    
    def test_modes_of_transportation(self, input, output):
        logger.info("Loading Test File: " + input)
        with open("test/routes/" + input) as test_file:
            test_data_contents = test_file.read()
        testData = json.loads(test_data_contents)

        logger.info("Calling modes_of_transportation function with test data to get result")
        result = NologyNav.modes_of_transportation(testData)
        assert result == output
        assert type(result) == list
        logger.info("Expected output: travel modes: " + ' '.join(output) + " | Actual output: travel modes = " + ' '.join(result))
    
    @pytest.mark.parametrize("input, output", [
        ({"waypoints": "32", 
        "distance_travelled": "295.5mi",
        "total_time": "5 hours 50 mins",
        "lat_lng": [{"lat": 51.5072126, "lng": -0.1275835}, {"lat": 48.85637149999999, "lng": 2.3532147}],
        "avg_speed": "50.9",
        "modes_of_transportation": ["driving"]},
        "This journey will take 5 hours 50 mins over 295.5mi, covering 32 waypoints at an average speed of 50.9. It will only require driving, at a starting (Lat/Long) of (51.5072126, -0.1275835), and ending at (48.85637149999999, 2.3532147)"),
        ({"waypoints": "32", 
        "distance_travelled": "295.5mi",
        "total_time": "5 hours 50 mins",
        "lat_lng": [{"lat": 51.5072126, "lng": -0.1275835}, {"lat": 48.85637149999999, "lng": 2.3532147}],
        "avg_speed": "50.9",
        "modes_of_transportation": ["driving", "ferry"]},
        "This journey will take 5 hours 50 mins over 295.5mi, covering 32 waypoints at an average speed of 50.9. In addition to driving, you will also need to use a ferry, at a starting (Lat/Long) of (51.5072126, -0.1275835), and ending at (48.85637149999999, 2.3532147)"),
        ({"waypoints": "32", 
        "distance_travelled": "295.5mi",
        "total_time": "5 hours 50 mins",
        "lat_lng": [{"lat": 51.5072126, "lng": -0.1275835}, {"lat": 48.85637149999999, "lng": 2.3532147}],
        "avg_speed": "50.9",
        "modes_of_transportation": ["driving", "ferry-train"]},
        "This journey will take 5 hours 50 mins over 295.5mi, covering 32 waypoints at an average speed of 50.9. In addition to driving, you will also need to use an auto-train, at a starting (Lat/Long) of (51.5072126, -0.1275835), and ending at (48.85637149999999, 2.3532147)"),
        ({"waypoints": "32", 
        "distance_travelled": "295.5mi",
        "total_time": "5 hours 50 mins",
        "lat_lng": [{"lat": 51.5072126, "lng": -0.1275835}, {"lat": 48.85637149999999, "lng": 2.3532147}],
        "avg_speed": "50.9",
        "modes_of_transportation": ["driving", "ferry-train", "ferry"]},
        "This journey will take 5 hours 50 mins over 295.5mi, covering 32 waypoints at an average speed of 50.9. In addition to driving, you will also need to use an auto-train and a ferry, at a starting (Lat/Long) of (51.5072126, -0.1275835), and ending at (48.85637149999999, 2.3532147)"),
        ({"waypoints": "32", 
        "distance_travelled": "295.5mi",
        "total_time": "5 hours 50 mins",
        "lat_lng": [{"lat": 51.5072126, "lng": -0.1275835}, {"lat": 48.85637149999999, "lng": 2.3532147}],
        "avg_speed": "50.9",
        "modes_of_transportation": ["driving", "ferry", "ferry-train"]},
        "This journey will take 5 hours 50 mins over 295.5mi, covering 32 waypoints at an average speed of 50.9. In addition to driving, you will also need to use a ferry and an auto-train, at a starting (Lat/Long) of (51.5072126, -0.1275835), and ending at (48.85637149999999, 2.3532147)")
    ])  
    def test_summary(self, input, output):
        logger.info("Calling summary function to retrieve result.")
        result = NologyNav.summary(input)
        
        logger.info("Verifying correct output of summary for data - notably checking modes: " + ' '.join(map(str, input["modes_of_transportation"])))
        assert result == output

    @pytest.mark.parametrize("input, output", [
        ({"origin": "Hawaii", "destination": "California"}, {"error": "We are unable to find a driving route between Hawaii and California."}),
        ({"origin": "Example Junk Origin", "destination": "Example Junk Destination"}, {"error": "We are unable to find the origin and destination."}),
        ({"origin": "Example Junk Origin", "destination": "California"}, {"error": "We are unable to find that origin."}),
        ({"origin": "Hawaii", "destination": "Example Junk Destination"}, {"error": "We are unable to find that destination."}),
        ({"origin": "London", "destination": "Paris"}, ("OK"))
    ])  
    def test_retrieve_data_from_google(self, input, output):
        logger.info("Calling retrieve_data_from_google function with test data to get result")
        logger.info("With values - Origin: " + input["origin"] + " / Destination: " + input["destination"])
        result = NologyNav.retrieve_data_from_google(input)
        
        if "error" in output:
            logger.info("Verfing output has expected error: " + output["error"])
            assert result == output
        else:
            logger.info("Verfing output a valid response was received from Google API")
            assert result["geocoded_waypoints"][0]["geocoder_status"] == output
            assert result["geocoded_waypoints"][1]["geocoder_status"] == output
            assert len(result["routes"]) > 0
