'use strict';
import {view, store} from '@risingstack/react-easy-state';
import newDocStore from './new_doc_store';
import * as React from 'react';
import {getIndexByProperty} from 'templates/components/my_extras';

class CustomSelect extends React.Component {
  getSelectOptions = (module) => {
    switch (module) {
      case 'accounting':
        return ['Бухгалтерський облік', 'Управлінський облік', 'Податковий облік', 'Загальний'];
      case 'type':
        return ['Операційна підтримка', 'Стратегічна підтримка', 'Управління доступами'];
      case 'importancy':
        return ['Дуже терміново', 'Терміново', 'Не терміново', 'На потім'];
      default:
        return [];
    }
  };
  
  onChange = (event) => {
    let text_box_id = event.target.id.substring(7); // видаляємо 'select-' з ід інпуту
    const queue = getIndexByProperty(newDocStore.new_document.text, 'queue', parseInt(text_box_id));
    if (queue === -1) {
      newDocStore.new_document.text.push({
        queue: parseInt(text_box_id),
        text: event.target.value
      });
    } else {
      newDocStore.new_document.text[queue].text = event.target.value;
    }
  };
  
  getSelectText = (queue) => {
    let text = '';
    const select_queue = getIndexByProperty(
      newDocStore.new_document.text,
      'queue',
      parseInt(queue)
    );
    if (select_queue !== -1) text = newDocStore.new_document.text[select_queue].text;
    return text;
  };

  render() {
    const {module_info} = this.props;
  
    return (
      <>
        <div className='row align-items-center mr-lg-1'>
          <label className='col-lg-5' htmlFor={'select-' + module_info.queue}>
            <If condition={module_info.required}>{'* '}</If>{module_info.field_name}:
          </label>
          <select className='col-lg-7 form-control mx-3 mx-lg-0' id={'select-' + module_info.queue} name='select' value={this.getSelectText(module_info.queue)} onChange={this.onChange}>
            <option key={0} data-key={0} value='0'>
              ------------
            </option>
            <For each='option' index='index' of={this.getSelectOptions(module_info.field)}>
              <option key={index} data-key={index} value={option}>
                {option}
              </option>
            </For>
          </select>
        </div>
        <small className='text-danger'>{module_info?.additional_info}</small>
      </>
    );
  }

  static defaultProps = {
    options: [],
    module_info: {
      field_name: '---',
      queue: 0,
      required: false,
      additional_info: null
    },
    text: '',
    onChange: () => {}
  };
}

export default view(CustomSelect);
