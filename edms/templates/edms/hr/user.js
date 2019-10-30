'use strict';
import React, {Fragment} from 'react';
import Modal from 'react-responsive-modal';
import Form from 'react-validation/build/form';
import Input from 'react-validation/build/input';
import Button from 'react-validation/build/button';
import Select from 'react-validation/build/select';
import axios from 'axios';
import querystring from 'querystring'; // for axios
import UserVacation from './user_vacation';
import {getIndex} from '../_else/my_extras.js';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.min.css';

axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.headers.put['Content-Type'] = 'application/x-www-form-urlencoded, x-xsrf-token';

class User extends React.Component {
  state = {
    on_vacation: this.props.user.on_vacation, // статус відпустки
    acting: this.props.user.acting, // ід співробітника, що заміняє даного на час відпустки
    acting_id: this.props.user.acting_id, // id в.о посади

    seat: '', // назва посади для форми
    seat_id: '', // id посади
    emp_seat: '', // обрана посада співробітника
    emp_seat_id: '', // ід запису посади співробітника
    emp_seats_list: this.props.user.emp_seats_list, // список посад співробітника

    vacation_checked: this.props.user.vacation_checked, // чи позначений чекбокс "у відпустці" (для відображення списку людей для в.о.)

    today:
      new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-' + new Date().getDate(), // сьогоднішня дата

    new_emp_seat_button_label: 'Прийняти на посаду',
    del_emp_seat_button_label: 'Звільнити з посади',

    new_emp: '', // нова людина на посаду замість звільненої
    new_emp_id: '',
    new_emp_is_acting: false, // чи нова людина оформляється як в.о.
    new_emp_form: <div> </div>,
    new_emp_is_acting_checked: false
  };

  onChange = (event) => {
    if (event.target.name === 'acting') {
      // беремо ід в.о. із <select>
      const selectedIndex = event.target.options.selectedIndex;
      this.setState({
        acting_id: event.target.options[selectedIndex].getAttribute('data-key'),
        acting: event.target.options[selectedIndex].getAttribute('value')
      });
    } else if (event.target.name === 'seat') {
      // беремо ід посади із <select>
      const selectedIndex = event.target.options.selectedIndex;
      this.setState({
        seat_id: event.target.options[selectedIndex].getAttribute('data-key'),
        seat: event.target.options[selectedIndex].getAttribute('value')
      });
    } else if (event.target.name === 'emp_seat') {
      // беремо ід посади із <select>
      const selectedIndex = event.target.options.selectedIndex;
      this.setState({
        emp_seat_id: event.target.options[selectedIndex].getAttribute('value'),
        emp_seat: event.target.options[selectedIndex].getAttribute('data-key')
      });
    } else if (event.target.name === 'new_emp') {
      const selectedIndex = event.target.options.selectedIndex;
      this.state.new_emp_id = event.target.options[selectedIndex].getAttribute('data-key');
      this.state.new_emp = event.target.options[selectedIndex].getAttribute('value');
    } else if (event.target.name === 'on_vacation') {
      this.setState({
        on_vacation: event.target.checked,
        vacation_checked: !this.state.vacation_checked
      });
      // якщо знімаємо галочку - видалити в.о.
      if (!event.target.checked) {
        this.state.acting_id = 0;
      }
    } else if (event.target.name === 'new_emp_is_acting') {
      this.setState({
        new_emp_is_acting: event.target.checked,
        new_emp_is_acting_checked: !this.state.new_emp_is_acting_checked
      });
      // якщо знімаємо галочку - видалити в.о.
      if (!event.target.checked) {
        this.state.new_emp_seat_id = 0;
      }
    } else {
      this.setState({
        [event.target.name]: event.target.value
      });
    }
  };

  newUserSeat = (e) => {
    // Оновлює запис у списку відділів
    e.preventDefault();

    axios({
      method: 'post',
      url: '',
      data: querystring.stringify({
        new_emp_seat: '',
        employee: this.props.user.id,
        seat: this.state.seat_id,
        end_date: null,
        is_active: true,
        is_main: true
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
      .then((response) => {
        const new_emp_seat = {
          id: response.data,
          emp_id: this.state.id,
          seat_id: this.state.seat_id,
          emp_seat: this.state.seat
        };
        this.setState((prevState) => ({
          emp_seats_list: [...prevState.emp_seats_list, new_emp_seat]
        }));
        this.setState({
          seat: 0,
          new_emp_seat_button_label: 'Посаду додано...'
        });
        setTimeout(
          function() {
            // повертаємо початковий напис на кнопці через 3 сек.
            this.setState({new_emp_seat_button_label: 'Прийняти на посаду'});
          }.bind(this),
          3000
        );
      })
      .catch((error) => {
        console.log('errorpost: ' + error);
      });
  };

  delEmpSeat = (e) => {
    e.preventDefault();
    console.log('!');
    axios({
      method: 'post',
      url: 'emp_seat/' + this.state.emp_seat_id + '/',
      data: querystring.stringify({
        employee: this.props.user.id,
        seat: this.state.emp_seat,
        end_date: this.state.today,
        successor_id: this.state.new_emp_id,
        is_active: false,
        is_main: true,
        new_is_main: !this.state.new_emp_is_acting
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
      .then((response) => {
        this.setState((prevState) => ({
          emp_seats_list: prevState.emp_seats_list.filter(
            (emp_seat) => emp_seat.id != this.state.emp_seat_id
          )
        }));
        this.setState({
          emp_seat_id: 0,
          del_emp_seat_button_label: 'З посади звільнено...',
          new_emp_form: <div> </div>,
          new_emp: 0
        });
        setTimeout(
          function() {
            // повертаємо початковий напис на кнопці через 3 сек.
            this.setState({del_emp_seat_button_label: 'Звільнити з посади'});
          }.bind(this),
          3000
        );
      })
      .catch((error) => {
        if (error.response.data === 'active flow') {
          this.notify('У даного співробітника є документи у роботі. Призначте, будь ласка, на посаду в.о. або нового працівника');
          this.setState({
            new_emp_form: (
              <div>
                <div>Прийняти на посаду іншу людину:</div>
                <div className='d-flex justify-content-between'>
                  <Select
                    id='emp-select'
                    name='new_emp'
                    value={this.state.new_emp}
                    onChange={this.onChange}
                  >
                    <option data-key={0} value='Не внесено'>
                      ------------
                    </option>
                    {this.props.emps.map((emp) => {
                      return (
                        <option key={emp.id} data-key={emp.id} value={emp.emp}>
                          {emp.emp}
                        </option>
                      );
                    })}
                  </Select>

                  <Input
                    className='mx-1'
                    name='new_emp_is_acting'
                    onChange={this.onChange}
                    type='checkbox'
                    checked={this.state.new_emp_is_acting}
                    id='vacation'
                  />
                  <label htmlFor='vacation'> в.о.</label>
                </div>
              </div>
            )
          });
        }
      });
  };

  handleSubmit = (e) => {
    // Оновлює запис у списку відділів
    e.preventDefault();
    // TODO реалізувати можливість прийняти людину відразу в статусі в.о., тепер вона заступає на посаду як основну

    // переводимо в null не обрані поля
    let acting_id = this.state.acting_id == 0 ? null : this.state.acting_id;

    let new_emps = this.props.emps; // клонуємо масив для внесення змін
    const index = getIndex(this.props.user.id, this.props.emps); // шукаємо індекс запису, в якому треба внести зміни

    // якщо хоча б одна зміна відбулася:

    if (
      new_emps[index].on_vacation !== this.state.on_vacation ||
      new_emps[index].acting_id !== this.state.acting_id
    ) {
      new_emps[index].on_vacation = this.state.on_vacation ? 'true' : 'false';
      new_emps[index].acting_id = parseInt(this.state.acting_id);
      new_emps[index].acting = this.state.acting;

      axios({
        method: 'post',
        url: 'emp/' + this.state.id + '/',
        data: querystring.stringify({
          pip: this.state.emp,
          on_vacation: this.state.on_vacation,
          acting: acting_id,
          is_active: true
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
        .then((response) => {
          // this.props.changeLists('emps', new_emps);
          window.location.reload();
        })
        .catch((error) => {
          console.log('errorpost: ' + error);
        });
    }
    this.setState({open: false}); // закриває модальне вікно
  };

  handleDelete = (e) => {
    // робить співробітника неактивним
    e.preventDefault();

    const {id} = this.state;
    if (this.state.emp_seats_list.length > 0) {
      this.notify('Спочатку звільніть співробітника з усіх посад.');
    } else {
      // переводимо в null не обрані поля
      let acting_id = this.state.acting == 0 ? null : this.state.acting_id;

      axios({
        method: 'post',
        url: 'emp/' + id + '/',
        data: querystring.stringify({
          pip: this.state.emp,
          user: id,
          on_vacation: this.state.on_vacation,
          acting: acting_id,
          is_active: false
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
        .then((response) => {
          // this.props.changeLists('emps', this.props.emps.filter((emp) => emp.id !== id));
          window.location.reload();
        })
        .catch((error) => {
          console.log('errorpost: ' + error);
        });
      // this.setState({open: false}); // закриває модальне вікно
    }
  };

  onClose = () => {
    this.props.onClose();
  };
  
  notify = (message) =>
    toast.error(message, {
      position: 'bottom-right',
      autoClose: 5000,
      hideProgressBar: true,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true
    });

  render() {
    const {acting, seat, emp_seat_id, new_emp_form} = this.state;

    const acting_select = this.state.vacation_checked ? ( // відображення селекту для в.о.
      <div className='d-flex'>
        <label htmlFor='acting-select'> В.о.:</label>
        <Select
          className='form-control'
          id='acting-select'
          name='acting'
          value={acting}
          onChange={this.onChange}
        >
          <option data-key={0} value=''>
            ------------
          </option>
          {this.props.emps.map((emp) => {
            return (
              <option key={emp.id} data-key={emp.id} value={emp.emp}>
                {emp.emp}
              </option>
            );
          })}
        </Select>
        <br />
        <br />
      </div>
    ) : (
      <div>
        <br /> <br />
      </div>
    );

    return (
      <Modal open={true} onClose={this.onClose} center>
        <p> </p>
        <Form onSubmit={this.handleSubmit}>
          <div>
            <div className='font-weight-bold'>
              {this.props.user.emp} <small>({this.props.user.tab_number})</small>
            </div>
          </div>
          <UserVacation emps={this.props.emps} />
          <div className='d-flex'>
            <Input
              name='on_vacation'
              onChange={this.onChange}
              type='checkbox'
              checked={this.state.on_vacation}
              id='vacation'
            />
            <label htmlFor='vacation'>у відпустці</label>
          </div>

          {acting_select}

          <div>
            <label>
              Нова посада:
              <Select
                className='form-control'
                id='seat-select'
                name='seat'
                value={seat}
                onChange={this.onChange}
              >
                <option data-key={0} value='Не внесено'>
                  ------------
                </option>
                {this.props.seats.map((seat) => {
                  return (
                    <option key={seat.id} data-key={seat.id} value={seat.seat}>
                      {seat.seat}
                    </option>
                  );
                })}
              </Select>
              <Button
                className='btn btn-outline-secondary mt-1'
                onClick={this.newUserSeat}
              >
                {this.state.new_emp_seat_button_label}
              </Button>
            </label>
          </div>
          <br />

          <div>
            <label>
              Посади користувача:
              <Select
                className='form-control'
                id='emp-seat-select'
                name='emp_seat'
                value={emp_seat_id}
                onChange={this.onChange}
              >
                <option data-key={0} value=''>
                  ------------
                </option>
                {this.state.emp_seats_list.map((empSeat) => {
                  return (
                    <option key={empSeat.id} data-key={empSeat.seat_id} value={empSeat.id}>
                      {empSeat.emp_seat}
                    </option>
                  );
                })}
              </Select>
              {new_emp_form}
              <Button
                className='btn btn-outline-secondary mt-1'
                onClick={this.delEmpSeat}
              >
                {this.state.del_emp_seat_button_label}
              </Button>
            </label>
          </div>
          <br />

          <Button className='float-sm-left btn btn-outline-success mb-1'>Підтвердити</Button>
          <Button
            className='float-sm-right btn btn-outline-secondary mb-1'
            onClick={this.handleDelete}
          >
            Звільнити співробітника
          </Button>
        </Form>
        
        {/*Вспливаюче повідомлення*/}
        <ToastContainer />
      </Modal>
    );
  }

  static defaultProps = {
    emps: [],
    seats: [],
    user: {}
  };
}

export default User;
