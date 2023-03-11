import React from 'react';
import '../../css/styles.css';

function Card(props) {
  return (
    <div className='container col-6 m-2'>
        <div class="card p-2">
            <div class="card-header border border-white rounded bg-dark-subtle">
                <div className='row justify-content-between'>
                    <div className="col-6 justify-content-between">
                        <div className="row justify-content-between">
                            <span className="col-6 text-start"><strong>Origin:</strong></span>
                            <span className="col-6 text-end">{ props.origin }</span>
                        </div>
                    </div>
                    <div className="col-6 justify-content-between">
                        <div className="row justify-content-between">
                            <span className="col-6 text-start"><strong>Destination:</strong></span>
                            <span className="col-6 text-end">{ props.destination }</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div className="row">
                    <div className="row justify-content-between">
                        <span className="col-4 text-start"><strong>Total Distance:</strong></span>
                        <span className="col-4 text-end">{ props.distanceTravelled }</span>
                    </div>
                </div>
                <br />
                <div className="row">
                    <div className="row justify-content-between">
                        <span className="col-4 text-start"><strong>Waypoints:</strong></span>
                        <span className="col-4 text-end">{ props.wayPoints }</span>
                    </div>
                    <div className="row justify-content-between">
                        <span className="col-4 text-start"><strong>Average Speed:</strong></span>
                        <span className="col-4 text-end">{ props.avgSpeed } mph</span>
                    </div>
                    <div className="row justify-content-between">
                        <span className="col-4 text-start"><strong>Total Time:</strong></span>
                        <span className="col-4 text-end">{ props.totalTime }</span>
                    </div>
                </div>
                <div className="row justify-content-center">
                    <span className="col-6 text-center"><strong>Summary</strong></span>
                </div>
                <div className="row">
                    <p className="card-text">{ props.summary }</p>
                </div>
                <br />
                <div className="row justify-content-center">
                    <span className="col-6 text-center"><strong>Final Recommendation</strong></span>
                </div>
                <div className="row">
                    <div className="border border-white rounded bg-dark-subtle">
                        <span className="row">Based on this information, we would not recommend a Unicycle for this journey, and instead suggest you use the following -</span>
                        <div className="row">
                            <span className="col-6 text-start"><strong>Alternate modes:</strong></span>
                            <ul className="col-6 text-end">
                                {
                                    props.modes.map((item, i) => {
                                        return (
                                            <li key={ i }>{ item.replace("driving", "Car").replace("ferry-train", "Auto Train").replace("ferry", "Ferry") }</li>
                                        )
                                    })
                                }
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
  }
  
  export default Card;