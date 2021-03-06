'use strict';
import * as React from 'react';
import {view, store} from '@risingstack/react-easy-state';
import ordersStore from 'docs/templates/docs/orders/orders_store';
import Order from './order';
import OrdersTable from 'docs/templates/docs/orders/orders_table';
import OrdersCalendar from 'docs/templates/docs/orders/calendar/orders_calendar';
import ordersCalendarStore from 'docs/templates/docs/orders/calendar/orders_calendar_store';
import OverdueReport from 'docs/templates/docs/orders/calendar/overdue_report';

class Orders extends React.Component {
  componentDidMount() {
    ordersStore.employees = window.employees;
    ordersStore.emp_seats = window.emp_seats;
    ordersStore.types = window.types;
    ordersStore.is_orders_admin = window.is_orders_admin;
    // ordersStore.orders = window.orders;

    // Визначаємо, чи відкриваємо просто список документів, чи це посилання на конкретний документ:
    const arr = window.location.href.split('/');
    const last_href_piece = parseInt(arr[arr.length - 1]);
    const is_link = !isNaN(last_href_piece);

    if (is_link) {
      ordersStore.order.id = last_href_piece;
      ordersStore.view = 'order';
    }
  }

  changeView = (name) => {
    ordersStore.view = name;
  };

  getButtonStyle = (name) => {
    if (name === ordersStore.view) return 'btn btn-sm btn-secondary mr-1 active';
    else if (name === 'my_calendar') return 'btn btn-sm btn-primary mr-1 active';
    return 'btn btn-sm btn-secondary mr-1';
  };

  render() {
    const {view} = ordersStore;
    return (
      <>
        <div className='btn-group mb-2' role='group' aria-label='orders_index'>
          <button type='button' className={this.getButtonStyle('table')} onClick={() => this.changeView('table')}>
            Загальний список
          </button>
          <button type='button' className={this.getButtonStyle('my_calendar')} onClick={() => this.changeView('my_calendar')}>
            Мій календар
          </button>
          <button type='button' className={this.getButtonStyle('constant_calendar')} onClick={() => this.changeView('constant_calendar')}>
            Мої постійні накази
          </button>
          <If condition={window.is_orders_admin || my_department_id === 45}>
            <button type='button' className={this.getButtonStyle('calendar')} onClick={() => this.changeView('calendar')}>
              Загальний календар
            </button>
          </If>
        </div>

        <Choose>
          <When condition={view === 'table'}>
            <OrdersTable />
          </When>
          <When condition={view === 'order'}>
            <Order />
          </When>
          <When condition={view === 'my_calendar' || view === 'calendar' || view === 'constant_calendar'}>
            <OrdersCalendar type={view} />
          </When>
        </Choose>
      </>
    );
  }
}

export default view(Orders);
