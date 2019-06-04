'use strict';
import React from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faPlus, faTimes} from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import {uniqueArray} from '../../_else/my_extras';
import '../../_else/my_styles.css'

class AcquaintList extends React.Component {
  state = {
    acquaint_list: this.props.acquaintList,
    select_acquaint_id: 0,
    select_acquaint: '',
    seat_list: []
  };

  onChange = (event) => {
    const selectedIndex = event.target.options.selectedIndex;
    this.setState({
      select_acquaint_id: event.target.options[selectedIndex].getAttribute('data-key'),
      select_acquaint: event.target.options[selectedIndex].getAttribute('value')
    });
  };

  // отримуємо з бд список користувачів
  componentWillMount() {
    axios({
      method: 'get',
      url: 'get_emp_seats/',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
      .then((response) => {
        this.setState({
          seat_list: response.data
        });
      })
      .catch((error) => {
        console.log('errorpost: ' + error);
      });
  }

  // надсилає новий список у батьківський компонент:
  changeList = (new_list) => {
    const changed_event = {
      target: {
        name: 'acquaint_list',
        value: new_list
      }
    };
    this.props.onChange(changed_event);
  };

  // додає нову посаду у список
  addNewAcquaint = (e) => {
    e.preventDefault();
    if (this.state.select_acquaint !== '') {
      let acquaint_list = [...this.state.acquaint_list];
      acquaint_list.push({
        id: this.state.select_acquaint_id,
        emp_seat: this.state.select_acquaint
      });
      const unique_seats = uniqueArray(acquaint_list);
      this.setState({
        acquaint_list: unique_seats,
        select_acquaint_id: '',
        select_acquaint: ''
      });
      // надсилаємо новий список у батьківський компонент
      this.changeList(unique_seats);
    }
  };

  // видає посаду з списку
  delAcquaint = (e, seat_id) => {
    e.preventDefault();
    // надсилаємо новий список у батьківський компонент
    this.changeList(this.state.acquaint_list.filter((seat) => seat.id !== seat_id));

    this.setState((prevState) => ({
      acquaint_list: prevState.acquaint_list.filter((seat) => seat.id !== seat_id)
    }));
  };

  render() {
    const {seat_list, select_acquaint, acquaint_list} = this.state;
    const {fieldName} = this.props;
    return (
      <Choose>
        <When condition={seat_list.length > 0}>
          <br />
          <div className='d-flex align-items-start mt-1'>
            <label className='flex-grow-1 text-nowrap mr-1' htmlFor='select_acquaint'>
              {fieldName}:
            </label>
            <select
              className='form-control'
              id='select_acquaint'
              name='select_acquaint'
              value={select_acquaint}
              onChange={this.onChange}
            >
              <option key={0} data-key={0} value='0'>
                ------------
              </option>
              {seat_list.map((seat) => {
                return (
                  <option key={seat.id} data-key={seat.id} value={seat.emp + ', ' + seat.seat}>
                    {seat.emp + ', ' + seat.seat}
                  </option>
                );
              })}
            </select>
            <button
              className={
                select_acquaint
                  ? 'btn btn-sm font-weight-bold ml-1 css_flash_button'
                  : 'btn btn-sm font-weight-bold ml-1 btn-outline-secondary'
              }
              onClick={this.addNewAcquaint}
            >
              <FontAwesomeIcon icon={faPlus} />
            </button>
          </div>
          <If condition={acquaint_list.length > 0}>
            <ul className='mt-1'>
              {acquaint_list.map((seat) => {
                return (
                  <div key={seat.emp_seat_id} className='d-flex align-items-start'>
                    <li>{seat.emp_seat}</li>
                    <button
                      className='btn btn-sm btn-outline-secondary font-weight-bold align-self-start ml-1'
                      onClick={(e) => this.delAcquaint(e, seat.id)}
                    >
                      <FontAwesomeIcon icon={faTimes} />
                    </button>
                  </div>
                );
              })}
            </ul>
          </If>
          <br />
        </When>
        <Otherwise>
          <div className='mt-3 loader-small' id='loader-1'>
            {' '}
          </div>
        </Otherwise>
      </Choose>
    );
  }

  static defaultProps = {
    acquaintList: [],
    fieldName: 'Список отримувачів'
  };
}

export {AcquaintList as default};
// export default AcquaintList;