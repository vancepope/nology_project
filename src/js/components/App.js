import React, { useEffect, useState } from 'react';
import '../../css/styles.css';
import Form from '../components/Form';
import Card from './Card';

function App() {
  const [navigationResponse, setNavigationResponse] = useState([]);
  const [startLocation, setStartLocation] = useState("");
  const [endLocation, setEndLocation] = useState("");
  const [error, setError] = useState("");
  const [warning, setWarning] = useState(false);

  function handleSubmit(e) {
    e.preventDefault()
    if (startLocation == "" || endLocation == "") {
      setWarning(true);
    } else {
      setWarning(false);
    }

    let locations = {
      "origin": startLocation,
      "destination": endLocation
    };

    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locations)
    };
    fetch('/get_summary', requestOptions)
      .then(response => response.json())
      .then(data => {
        if (data["error"]) {
          setError(data["error"]);
          setStartLocation("");
          setEndLocation("");
          return;
        }
        setNavigationResponse([data].concat(navigationResponse));
        setWarning(false);
        setError("");
        setStartLocation("");
        setEndLocation("");
      });
  }
  return (
    <div className="p-3 m-2">
        <main className='row justify-content-md-center'>
        {
          error != "" && (
            <div class="alert alert-danger m-3" role="alert"><strong>Error:</strong> { error } We definitely don't recommend riding a Unicycle.</div>
          )
        }
        {
          warning && (
            <div class="alert alert-warning m-3" role="alert"><strong>Warning:</strong> Please make sure to enter your origin and destination. We definitely don't recommend riding a Unicycle.</div>
          )
        }
        <Form handleSubmit={ handleSubmit } 
              setStartLocation={ setStartLocation }
              setEndLocation={ setEndLocation }
              startLocation= { startLocation }
              endLocation= { endLocation }
        />
        {
          navigationResponse.length > 0 && navigationResponse.map((item, i) => {
            return (
                <Card key={ i } 
                      origin={ item["origin"] }
                      destination={ item["destination"] }
                      wayPoints={ item["waypoints"] } 
                      distanceTravelled={ item["distance_travelled"] }
                      totalTime={ item["total_time"] }
                      avgSpeed={ item["avg_speed"] }
                      modes={ item["modes_of_transportation"] }
                      summary={ item["summary"] }
                />

            )
          })
        }
        </main>
    </div>
  );
  }
  
  export default App;