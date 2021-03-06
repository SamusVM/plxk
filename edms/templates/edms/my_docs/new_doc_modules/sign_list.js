'use strict';
import * as React from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faPlus, faTimes} from '@fortawesome/free-solid-svg-icons';
import {uniqueArray} from 'templates/components/my_extras';
import {getEmpSeats} from '../../../../api/get_emp_seats';
import 'static/css/my_styles.css';

class SignList extends React.Component {
  state = {
    sign_list: this.props.signList,
    select_sign_id: 0,
    select_sign: '',
    seat_list: JSON.parse(localStorage.getItem('emp_seat_list')) ? JSON.parse(localStorage.getItem('emp_seat_list')) : []
  };

  onChange = (event) => {
    const selectedIndex = event.target.options.selectedIndex;
    this.setState({
      select_sign_id: event.target.options[selectedIndex].getAttribute('data-key'),
      select_sign: event.target.options[selectedIndex].getAttribute('value')
    });
  };

  // перевіряємо, чи оновився список співробітників з часу останнього візиту
  componentWillMount() {
    const get_emp_seats = getEmpSeats();
    get_emp_seats.then((result) => {
      // Якщо result === 0 - змін у базі не виявлено
      if (result === 0) {
        // Але якщо на сторінці два компоненти запитують про зміни,
        // їх правильно покаже тільки перший, всі наступні будуть показувати result===0,
        // але список не оновлять, тому оновлюємо список самі
        this.state.seat_list.length === 0
          ? this.setState({
              seat_list: JSON.parse(localStorage.getItem('emp_seat_list'))
            })
          : null;
      } else {
        this.setState({
          seat_list: result
        });
      }
    });
  }

  // надсилає новий список у батьківський компонент:
  changeList = (new_list) => {
    const changed_event = {
      target: {
        name: 'sign_list',
        value: new_list
      }
    };
    this.props.onChange(changed_event);
  };

  // додає нову посаду у список
  addNewSign = (e) => {
    e.preventDefault();
    if (this.state.select_sign !== '') {
      let sign_list = [...this.state.sign_list];
      sign_list.push({
        id: this.state.select_sign_id,
        emp_seat: this.state.select_sign
      });
      const unique_seats = uniqueArray(sign_list);
      this.setState({
        sign_list: unique_seats,
        select_sign_id: '',
        select_sign: ''
      });
      // надсилаємо новий список у батьківський компонент
      this.changeList(unique_seats);
    }
  };

  // видає посаду з списку
  delSign = (e, seat_id) => {
    e.preventDefault();
    // надсилаємо новий список у батьківський компонент
    this.changeList(this.state.sign_list.filter((seat) => seat.id !== seat_id));

    this.setState((prevState) => ({
      sign_list: prevState.sign_list.filter((seat) => seat.id !== seat_id)
    }));
  };

  render() {
    const {seat_list, select_sign, sign_list} = this.state;
    const {module_info} = this.props;
    return (
      <Choose>
        <When condition={seat_list.length > 0}>
          <br />
          <div className='w-75 d-flex align-items-start mt-1'>
            <label className='flex-grow-1 text-nowrap mr-1' htmlFor='select_sign'>
              {module_info.field_name}:
            </label>
            <select className='form-control' id='select_sign' name='select_sign' value={select_sign} onChange={this.onChange}>
              <option key={0} data-key={0} value='0'>
                ------------
              </option>
              <For each='seat' index='index' of={seat_list}>
                <option key={index} data-key={seat.id} value={seat.emp + ', ' + seat.seat}>
                  {seat.emp + ', ' + seat.seat}
                </option>
              </For>
            </select>
            <button
              className={
                select_sign ? 'btn btn-sm font-weight-bold ml-1 css_flash_button' : 'btn btn-sm font-weight-bold ml-1 btn-outline-secondary'
              }
              onClick={this.addNewSign}
            >
              <FontAwesomeIcon icon={faPlus} />
            </button>
          </div>
          <small className='text-danger'>{module_info?.additional_info}</small>
          <If condition={sign_list.length > 0}>
            <ul className='mt-1'>
              <For each='seat' index='index' of={sign_list}>
                <div key={index} className='d-flex align-items-start'>
                  <li>{seat.emp_seat}</li>
                  <button
                    className='btn btn-sm btn-outline-secondary font-weight-bold align-self-start ml-1'
                    onClick={(e) => this.delSign(e, seat.id)}
                  >
                    <FontAwesomeIcon icon={faTimes} />
                  </button>
                </div>
              </For>
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
    signList: [],
    module_info: {
      field_name: 'Список отримувачів',
      queue: 0,
      required: false,
      additional_info: null
    }
  };
}

export {SignList as default};
// export default SignList;
