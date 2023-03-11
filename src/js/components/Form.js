import React from 'react';
import '../../css/styles.css';

function Form(props) {
  return (
    <form className='col-6 p-3' onSubmit={(e) => props.handleSubmit(e)}>
        <div className='row'>
            <div class="col-5 form-group">
                <label for="startLocation">Origin</label>
                <input type="text" class="form-control" id="startLocationInput" placeholder="From" onChange={ (e) => { props.setStartLocation(e.target.value)} } value={ props.startLocation } />
            </div>
            <div class="col-5 form-group">
                <label for="endLocation">Destination</label>
                <input type="text" class="form-control" id="endLocationInput" placeholder="To" onChange={ (e) => { props.setEndLocation(e.target.value)} } value={ props.endLocation } />
            </div>
            <div class="col-2 form-group">
                <br />
                <button type="submit" className="btn btn-secondary">Submit</button>
            </div>
        </div>
    </form>
  );
  }
  
  export default Form;