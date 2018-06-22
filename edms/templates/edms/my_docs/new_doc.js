'use strict';
import React from 'react';
import PropTypes from 'prop-types';
import Form from 'react-validation/build/form';
import Input from 'react-validation/build/input';
import Button from 'react-validation/build/button';
import Textarea from 'react-validation/build/textarea';
import axios from 'axios';
import querystring from 'querystring'; // for axios

import {required} from '../validations.js';
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.headers.put['Content-Type'] = 'application/x-www-form-urlencoded, x-xsrf-token';


class NewDoc extends React.Component {
    constructor(props) {
        super(props);

        this.onChange = this.onChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    state = {
        text: '',
        date: '',
        my_seats: window.my_seats,
    };

    styles = {
        textarea_style : {
            width: 400,
            height: 100
        },
    };

    onChange(event) {
        if (event.target.name === 'my_seat') { // беремо ід посади із <select>
            const selectedIndex = event.target.options.selectedIndex;
            this.state.my_seat_id = event.target.options[selectedIndex].getAttribute('value');
            this.setState({my_seat_id: event.target.options[selectedIndex].getAttribute('value')});
        }
        else {
             this.setState({[event.target.name]:event.target.value});
        }
    }

    // Додає нову звільнюючу перепустку
    handleSubmit(e) {
        e.preventDefault();

        axios({
            method: 'post',
            url: '',
            data: querystring.stringify({
                new_free_time: '',
                document_type: 1,
                free_day: this.state.date,
                text: this.state.text,
                employee_seat: this.props.my_seat_id,
            }),
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            },
        }).then((response) => { // закриваємо і очищаємо модальне вікно, відправляємо дані нового документа в MyDocs
            document.getElementById("modal_freetime_close").click();

            let today = new Date();
            this.setState({
                date:'',
                text:'',
            });

            this.props.addDoc(response.data, 'Звільнююча перепустка', today.getDate() + '-' + today.getMonth() + '-' + today.getFullYear(), this.props.my_seat_id);
        })
          .catch(function (error) {
            console.log('errorpost: ' + error);
        });
    }

    render() {
        return(
            <div>

                <div>Створити новий документ:</div>
                <button type="button" className="btn btn-outline-secondary mb-1 w-100" data-toggle="modal" data-target="#modalNewFreePass" id="button_new_free_pass">Звільнююча перепустка</button>

                {/*форма нової звільнюючої:*/}
                <div className="container">
                  <div className="modal fade" id="modalNewFreePass">
                    <div className="modal-dialog modal-lg modal-dialog-centered">
                      <div className="modal-content">

                        <div className="modal-header">
                          <h4 className="modal-title">Нова звільнююча</h4>
                          <button type="button" className="close" data-dismiss="modal" id="modal_freetime_close">&times;</button>
                        </div>

                        <Form onSubmit={this.handleSubmit}>
                            <div className="modal-body">

                                <label>День дії звільнюючої:
                                    <Input type="date" value={this.state.date} name="date" onChange={this.onChange} validations={[required]}/>
                                </label> <br /> <br />

                                <label>Куди, з якою метою звільнюєтесь:
                                    <Textarea value={this.state.text} name='text' onChange={this.onChange} style={this.styles.textarea_style} maxLength={4000}/>
                                </label> <br /> <br />

                            </div>

                            <div className="modal-footer">
                              <Button className="float-sm-left btn btn-outline-secondary mb-1">Підтвердити</Button>
                            </div>
                        </Form>

                      </div>
                    </div>
                  </div>
                </div>
            </div>
        )
    }
}

NewDoc.propTypes = {
      addDoc: PropTypes.func
    };

export default NewDoc;