'use strict';
import React, {Fragment} from 'react';
import Modal from 'react-responsive-modal';
import Form from 'react-validation/build/form';
import Input from 'react-validation/build/input';
import Button from 'react-validation/build/button';
import Select from 'react-validation/build/select';
import 'static/css/my_styles.css';
import DxTable from 'templates/components/tables/dx_table';
import {required} from '../_else/validations.js';
import {getIndex} from 'templates/components/my_extras.js';
import axios from 'axios';
import querystring from 'querystring'; // for axios
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.headers.put['Content-Type'] = 'application/x-www-form-urlencoded, x-xsrf-token';

class Seats extends React.Component {
  state = {
    open: false,
    new_open: false,
    id: '', // id посади для форми
    seat: '', // назва посади для форми
    dep: '', // назва відділу для форми
    dep_id: '', // id відділу
    is_dep_chief: false, // чи є посада керівною у відділі
    chief: '', // керівник посади для форми
    chief_id: '', // id керівника посади
    is_vacant: true // чи є посада вакантною
  };

  onChange = (event) => {
    if (event.target.name === 'chief') {
      // беремо ід керівника із <select>
      const selectedIndex = event.target.options.selectedIndex;
      this.state.chief_id = event.target.options[selectedIndex].getAttribute('data-key');
      this.state.chief = event.target.options[selectedIndex].getAttribute('value');
    } else if (event.target.name === 'dep') {
      // беремо ід відділу із <select>
      const selectedIndex = event.target.options.selectedIndex;
      this.setState({
        dep_id: event.target.options[selectedIndex].getAttribute('data-key'),
        dep: event.target.options[selectedIndex].getAttribute('value')
      });
    } else if (event.target.name === 'is_dep_chief') {
      this.setState({
        is_dep_chief: event.target.checked
      });
    } else {
      this.setState({[event.target.name]: event.target.value});
    }
  };

  handleSubmit = (e) => {
    // Оновлює запис у списку відділів
    e.preventDefault();
    let new_seats = this.props.seats; // Створюємо змінений масив seats, який призначимо this.seats у разі успіху post
    const index = getIndex(this.state.id, this.props.seats); // шукаємо індекс запису, в якому треба внести зміни

    // якщо хоча б одна зміна відбулася:
    if (
      new_seats[index].seat !== this.state.seat ||
      new_seats[index].dep_id !== this.state.dep_id ||
      new_seats[index].is_dep_chief !== this.state.is_dep_chief ||
      new_seats[index].chief_id !== this.state.chief_id
    ) {
      new_seats[index].id = this.state.id;
      new_seats[index].seat = this.state.seat;
      new_seats[index].dep = this.state.dep;
      new_seats[index].dep_id = this.state.dep_id;
      new_seats[index].is_dep_chief = this.state.is_dep_chief;
      new_seats[index].chief = this.state.chief;
      new_seats[index].chief_id = this.state.chief_id;

      // переводимо в null не обрані поля
      let chief_id = this.state.chief_id == 0 ? null : this.state.chief_id;
      let dep_id = this.state.dep_id == 0 ? null : this.state.dep_id;

      axios({
        method: 'post',
        url: 'seat/' + this.state.id + '/',
        data: querystring.stringify({
          id: this.state.id,
          seat: this.state.seat,
          department: dep_id,
          is_dep_chief: this.state.is_dep_chief,
          chief: chief_id,
          is_active: true
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
        .then((response) => {
          this.props.changeLists('seats', new_seats);
          // console.log('responsepost: ' + response);
        })
        .catch((error) => {
          console.log('errorpost: ' + error);
        });
    }
    this.setState({
      seat: '',
      dep: '',
      dep_id: 0,
      is_dep_chief: false,
      chief: '',
      chief_id: 0,
      open: false
    });
  };

  handleDelete = (e) => {
    // робить відділ неактивним
    e.preventDefault();

    // переводимо в null не обрані поля
    let chief_id = this.state.chief_id == 0 ? null : this.state.chief_id;
    let dep_id = this.state.dep_id == 0 ? null : this.state.dep_id;

    axios({
      method: 'post',
      url: 'seat/' + this.state.id + '/',
      data: querystring.stringify({
        id: this.state.id,
        seat: this.state.seat,
        department: dep_id,
        chief: chief_id,
        is_active: false
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
      .then((response) => {
        this.props.changeLists(
          'seats',
          this.props.seats.filter((seat) => seat.id !== this.state.id)
        );
        // console.log('responsepost: ' + response);
      })
      .catch((error) => {
        console.log('errorpost: ' + error);
      });
    this.setState({
      seat: '',
      dep: '',
      dep_id: 0,
      chief: '',
      chief_id: 0,
      open: false
    });
  };

  handleNew = (e) => {
    // Оновлює запис у списку відділів
    e.preventDefault();

    // let new_seats = this.props.seats;

    // переводимо в null не обрані поля
    let chief_id = this.state.chief_id == 0 ? null : this.state.chief_id;
    let dep_id = this.state.dep_id == 0 ? null : this.state.dep_id;

    axios({
      method: 'post',
      url: '',
      data: querystring.stringify({
        new_seat: '',
        seat: this.state.seat,
        department: dep_id,
        is_dep_chief: this.state.is_dep_chief,
        chief: chief_id,
        is_active: true
      })
    })
      .then((response) => {
        // new_seats.push({
        //     id: response.data,
        //     seat: this.state.seat,
        //     dep_id: parseInt(this.state.dep_id),
        //     dep: this.state.dep,
        //     chief_id: parseInt(this.state.chief_id),
        //     chief: this.state.chief,
        //     is_vacant: true,
        // });
        // this.props.changeLists('seats', new_seats);
        //
        // this.setState({
        //     seat: '',
        //     dep: '',
        //     dep_id: 0,
        //     chief: '',
        //     chief_id: 0,
        //     new_open: false,
        // });
        window.location.reload();
        // console.log('responsepost: ' + response);
      })
      .catch((error) => {
        console.log('errorpost: ' + error);
      });
  };

  onRowClick = (row) => {
    this.setState({
      // інформація про натиснутий рядок
      id: row.id,
      seat: row.seat,
      dep: row.dep,
      dep_id: row.dep_id,
      is_dep_chief: row.is_dep_chief === 'true',
      chief: row.chief,
      chief_id: row.chief_id,
      is_vacant: row.is_vacant === 'true'
    });
    this.onOpenModal();
  };

  onOpenModal = () => {
    this.setState({open: true});
  };

  onCloseModal = () => {
    this.setState({
      open: false,
      seat: '',
      dep: '',
      chief: ''
    });
  };

  onOpenModalNew = () => {
    this.setState({new_open: true});
  };

  onCloseModalNew = () => {
    this.setState({new_open: false});
  };

  render() {
    const {open, new_open, chief, dep} = this.state;

    const seats_columns = [{name: 'seat', title: 'Посада'}, {name: 'dep', title: 'Відділ'}];

    return (
      <Fragment>
        <button
          type='button'
          className='btn btn-sm btn-outline-secondary mb-1 float-right'
          onClick={this.onOpenModalNew}
        >
          Додати посаду
        </button>
        <div className='float-left'>
          <DxTable
            rows={this.props.seats}
            columns={seats_columns}
            defaultSorting={[{columnName: 'seat', direction: 'asc'}]}
            onRowClick={this.onRowClick}
            // redRow="is_vacant"
            height={this.props.height}
            filter
          />
        </div>

        {/*Модальне вікно редагування посади*/}
        <Modal open={open} onClose={this.onCloseModal} center>
          <br />
          <p className='font-weight-bold'>Внесіть зміни при необхідності:</p>

          <Form onSubmit={this.handleSubmit}>
            <label className='full_width' htmlFor='seat'>
              Назва посади:
            </label>
            <Input
              className='form-control full_width'
              id='seat'
              type='text'
              value={this.state.seat}
              name='seat'
              onChange={this.onChange}
              maxLength={100}
              size='51'
              validations={[required]}
            />
            <br />
            <br />

            <label className='full_width' htmlFor='dep-select'>
              Відділ:
            </label>
            <Select
              className='form-control full_width'
              id='dep-select'
              name='dep'
              value={dep}
              onChange={this.onChange}
            >
              <option data-key={0} value='Не внесено'>
                ------------
              </option>
              {this.props.deps.map((dep) => {
                return (
                  <option key={dep.id} data-key={dep.id} value={dep.dep}>
                    {dep.dep}
                  </option>
                );
              })}
            </Select>

            <div className='d-flex'>
              <Input
                name='is_dep_chief'
                onChange={this.onChange}
                type='checkbox'
                checked={this.state.is_dep_chief}
                id='dep_chief'
              />
              <label htmlFor='dep_chief'>керівник відділу</label>
            </div>
            <br />
            <br />

            <label className='full_width'>
              Керівник:
              <Select
                className='form-control full_width'
                id='chief-select'
                name='chief'
                value={chief}
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
            </label>
            <br />
            <br />

            <Button className='float-sm-left btn btn-outline-info mb-1'>Підтвердити</Button>
            <Button
              className='float-sm-right btn btn-outline-secondary mb-1'
              onClick={this.handleDelete}
            >
              Видалити посаду
            </Button>
          </Form>
        </Modal>

        {/*Модальне вікно додання посади*/}
        <Modal open={new_open} onClose={this.onCloseModalNew} center>
          <br />
          <p className='font-weight-bold'>Нова посада</p>
          <Form onSubmit={this.handleNew}>
            <label className='full_width'>
              Назва посади:
              <Input
                className='form-control full_width'
                type='text'
                value={this.state.seat}
                name='seat'
                onChange={this.onChange}
                maxLength={100}
                size='51'
                validations={[required]}
              />
            </label>
            <br />
            <br />

            <label className='full_width'>
              Відділ:
              <Select
                className='form-control full_width'
                id='dep-select'
                name='dep'
                value={dep}
                onChange={this.onChange}
              >
                <option data-key={0} value='Не внесено'>
                  ------------
                </option>
                {this.props.deps.map((dep) => {
                  return (
                    <option key={dep.id} data-key={dep.id} value={dep.dep}>
                      {dep.dep}
                    </option>
                  );
                })}
              </Select>
            </label>
            <br />
            <br />

            <label className='full_width'>
              Керівник:
              <Select
                className='form-control full_width'
                id='chief-select'
                name='chief'
                value={chief}
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
            </label>
            <br />
            <br />

            <Button className='btn btn-outline-info float-sm-left'>Підтвердити</Button>
          </Form>
        </Modal>
      </Fragment>
    );
  }
}

export default Seats;
