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
    @pytest.fixture()
    def app(self):
        app = create_app()

        yield app

    @pytest.fixture()
    def client(self, app):
        return app.test_client()

    @pytest.mark.parametrize("input, output", [
        ({"origin": "London", "destination": "Paris"}, 
        {"response_code": 200, "json": "London_to_Paris_Output.json"}),
        ({"origin": "San Diego, California", "destination": "Phoenix, Arizona"}, 
        {"response_code": 200, "json": "SD_to_PH_Output.json"}),
        ({"origin": "Dublin, Ireland", "destination": "Paris, France"}, 
        {"response_code": 200, "json": "Dublin_to_Paris_Output.json"}),
        ({"origin": "Tokyo, Japan", "destination": "Nagoya, Japan"}, 
        {"response_code": 200, "json": "Tokyo_to_Nagoya_Output.json"}),
        ({"origin": "Times Square, New York", "destination": "42 Wallaby Way, Sydney"}, 
        {"response_code": 406, "json": "TimesSquareNewYork_to_42WallabyWaySydney.json"}),
        ({"origin": "London", "destination": "Very Bad Location Data"}, 
        {"response_code": 406, "json": "London_to_Bad_Location_Output.json"}),
        ({"origin": "Victoria, Canada", "destination": "Seattle, Washington"}, 
        {"response_code": 200, "json": "Victoria_to_Seattle_Output.json"}),
        ({"origin": "17082 Thornmint Ct, San Diego, CA 92127", "destination": "12350 Carmel Mountain Rd, San Diego, CA 92128"}, 
        {"response_code": 200, "json": "ASML_to_Costco_Output.json"})
    ])
    def test_get_summary(self, client, input, output):
        logger.info("Calling Flask Client Route: /get_summary with: - Origin: " + input["origin"] + " / Destination: " + input["destination"])
        response = client.post('/get_summary', json = input)

        logger.info("Verifying expected response code: " + str(output["response_code"]))
        assert response.status_code == output["response_code"]

        logger.info("Converting Response Data into Json")
        responseData = json.loads(response.data.decode("UTF-8"))

        logger.info("Retreiving expected output file: " + output["json"])
        with open("test/route_responses/" + output["json"]) as test_file:
            test_data_contents = test_file.read()
        testData = json.loads(test_data_contents)

        logger.info("Verifying Route Data Matches")
        if "error" in testData:
            assert responseData == testData
        else:
            responseDataDTConverted = float(responseData["distance_travelled"].replace("mi", ""))
            testDataDTConverted = float(testData["distance_travelled"].replace("mi", ""))
            responseDataTTConvertedList = responseData["total_time"].split(" ")
            testDataTTConvertedList = testData["total_time"].split(" ")
            if responseDataTTConvertedList[1] == "mins":
                logger.info("Verifying expected units for total time")
                responseDataTTConvertedMins = float(responseDataTTConvertedList[0])
                testDataTTConvertedMins = float(testDataTTConvertedList[0])
                assert responseDataTTConvertedMins == approx(testDataTTConvertedMins, testDataTTConvertedMins/10)
            else:
                logger.info("Converting hours to minutes for total time verification")
                responseDataTTConvertedHours = float(responseDataTTConvertedList[0])*60
                responseDataTTTotalMins = float(responseDataTTConvertedList[2])+responseDataTTConvertedHours
                testDataTTConvertedHours = float(testDataTTConvertedList[0])*60
                testDataTTTotalMins = float(testDataTTConvertedList[2])+testDataTTConvertedHours
                assert responseDataTTTotalMins == approx(testDataTTTotalMins, testDataTTTotalMins/10)

            assert responseData["waypoints"] == approx(testData["waypoints"], testData["waypoints"]/10)
            assert responseDataDTConverted == approx(testDataDTConverted, testDataDTConverted/10)
            assert responseData["lat_lng"] == testData["lat_lng"]
            assert responseData["avg_speed"] == approx(testData["avg_speed"], testData["avg_speed"]/10)
            assert responseData["modes_of_transportation"] == testData["modes_of_transportation"]
            assert responseData["summary"][0:23] == testData["summary"][0:23]
