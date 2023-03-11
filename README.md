# NologyNav Project

## Description

This project uses the Google navigation API to take in a origin and destination from the user to return a summarized statement including these attributes (waypoints, distance_travelled, total_time, lat_lng (origin & endpoint), avg_speed, modes_of_transportation, and a summary). At the end of the program, it will be able to return the data in a JSON human readable form.

Testing of this program was done in pytest to test full code coverage. CI/CD was also used via Jenkins for live updates/logs of testing.

## Table of Contents 

- [Test Plan & Trello Board](#test-plan-and-trello-board)
- [Installation](#installation)
- [Usage](#usage)
- [Tests](#tests)
- [Team Members](#team-members)

## Test Plan and Trello Board
### Test Plan
The [Test Plan Document](https://docs.google.com/document/d/1NMgcpJF1CMMRhIfXu82r77QWRdTP-W7_9hfGgHUh4n0/edit?usp=sharing) was written in IEEE829-format in order to have the team complete this project using Test Driven Development. The plan was used to identify features that needed to be tested, the approach and tools that would be used in the testing, and the definition of Done for when the test would be passing.

![Test Plan](https://i.imgur.com/4fUJLCw.png)

### Trello Board
The [Trello Board](https://trello.com/b/AGDDXgy3/nology-bot-t1) was used in order to have the team assign tasks in a defined order and keep track of what tasks needed to be done(seperated by testing, development, and documentation).

![Trello Board](https://i.imgur.com/c5NvfpC.png)

## Installation

- Must install [Postman](https://www.postman.com/downloads/), [Node](https://nodejs.org/en/download/), and have local IDE to run code.
- Clone repository onto your device and then run `npm install` on your terminal commandline
- Then `npm run start` on your terminal commandline

## Usage

In the example below, we are setting our origin as London and our destination as Paris. Our program then runs the data through our endpoint and gives us a summary of all the data we requested in a simple statement for the User. An example of the output using sample data (origin: London, destination: Paris) below:

    "summary": "This journey will take 5 hours 50 mins over 295.5 mi, covering 50 waypoints at an average speed of 50.9. In
    addition to driving, you will also need to use an auto-train, at a starting (Lat/Long) of (51.5072126, -0.1275835), and
    ending at (48.85637149999999, 2.3532147)"

Postman Example:
![Postman](https://user-images.githubusercontent.com/25696415/216680860-eeab0310-b5b0-4c07-a571-a73619c0ed48.png)

GUI Example:
![GUI](https://i.imgur.com/kIZ83Pu.png)

---


## Tests

The program was created with Test Driven Development in mind. Since the final output of the program was a to be a compilation of data, each data-point was spun off into its own function which could then be tested on a unit/component level, and then tested together at the system level. The unit level tests were written with white-box testing principles to hit 100% Decision Coverage, verified with `pytest --coverage`.

Final system tests of the whole program are then done, using live data from Google's API. Due to this being live data, values such as distance and time in the API are sometimes different due to route updates, road closures/openings/traffic. This difficulty was overcome by using the `Approx(value, tolerance)` feature of pytest, so that these values that sometimes change can be estimated in the live data to be close to expected, since an exact match is not always possible, especially on a long test route such as Dublin, Ireland to Paris, France.

Pictured below is sample ouput from the generated testing report. Showing details on what actions are being performed on each test:
![EXAMPLE TESTS](https://i.imgur.com/lnFnMAY.png)

All tests passed:
![PASSED TESTS](https://i.imgur.com/fhykzbD.png)

## Code Coverage

After having all our tests pass, we must use `pytest test/Test_NologyNav.py -v --html=report.html --cov=src/ --cov-report=html --cov-branch` in order to get our report below. This report displays a visual of our tests fully running through our program and covering all functions.

Full Test Coverage:
![TEST COVERAGE](https://i.imgur.com/uSbiWZR.png)

## Jenkins

Jenkins was used for CI/CD to run a build and then perform all tests every time a code change was made.

Example output from Jenkins passing all tests:
![LIVE LOG CALL](https://i.imgur.com/GrKMJz5.png)

## Team Members

- [Nik Mikin](https://github.com/NIKMIKIN)
- [Alan Greaney](https://github.com/AlanGreaney)
- [Vance Pope](https://github.com/vancepope)
