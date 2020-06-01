'use strict';
import React from 'react';
import {view, store} from '@risingstack/react-easy-state';
import corrStore from '../store';

class Client extends React.Component {
  onChange = (event) => {
    const selectedIndex = event.target.options.selectedIndex;
    corrStore.request.client_id = event.target.options[selectedIndex].getAttribute('data-key');
    corrStore.request.client_name = event.target.options[selectedIndex].getAttribute('value');
  };

  render() {

    return (
      <div className='row align-items-center mt-1 mr-lg-1'>
        <label className='col-lg-1' htmlFor='client'>
          Клієнт:
        </label>
        <select
          className='col-lg-11 form-control mx-3 mx-lg-0'
          id='client'
          name='client'
          value={corrStore.request.client_name}
          onChange={this.onChange}
        >
          <option key={0} data-key={0} value='0'>
            ------------
          </option>
          {corrStore.clients.map((emp) => {
            return (
              <option key={emp.id} data-key={emp.id} value={emp.name}>
                {emp.name}
              </option>
            );
          })}
        </select>
      </div>
    );
  }
}

export default view(Client);