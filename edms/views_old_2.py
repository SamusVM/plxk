from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, QueryDict
from django.contrib.auth.decorators import login_required
from django.utils.timezone import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
import json
import pytz
import smtplib

from accounts import models as accounts  # import models Department, UserProfile
from .models import Seat, Employee_Seat, Document, File, Document_Path, Document_Type, Document_Type_Permission, Mark
from .models import Carry_Out_Items, Mark_Demand
from .forms import DepartmentForm, SeatForm, UserProfileForm, EmployeeSeatForm, DocumentForm, DocumentPathForm
from .forms import CarryOutItemsForm, MarkDemandForm, ResolutionForm
from .forms import DTPDeactivateForm, DTPAddForm, CloseDocForm
# Модульна система:
from .models import Document_Type_Module, Doc_Name, Doc_Preamble, Doc_Approval, Doc_Article, Doc_Article_Dep
from .models import Doc_Text, Doc_Recipient, Doc_Day, Doc_Gate, Doc_Type_Unique_Number
from .forms import NewArticleForm, NewArticleDepForm, NewApprovalForm, NewNameForm, NewPreambleForm, NewFileForm
from .forms import NewTextForm, NewRecipientForm, NewDayForm, NewGateForm
# Система фаз:
from .models import Doc_Type_Phase, Doc_Type_Phase_Queue


# При True у списках відображаться і ті документи, які знаходяться в режимі тестування.
testing = True


def convert_to_localtime(utctime, frmt):
    if frmt == 'day':
        fmt = '%d.%m.%Y'
    else:
        fmt = '%d.%m.%Y %H:%M'

    utc = utctime.replace(tzinfo=pytz.UTC)
    localtz = utc.astimezone(timezone.get_current_timezone())
    return localtz.strftime(fmt)


# Функція, яка рекурсією шукає всіх підлеглих посади користувача і їх підлеглих
def get_subs_list(seat):
    seats = [{'id': seat.id} for seat in Seat.objects.filter(chief_id=seat)]  # Знаходимо підлеглих посади
    temp_seats = []
    if seats:  # якщо підлеглі є:
        for seat in seats:
            temp_seats.append({'id': seat['id']})  # додамо кожного підлеглого у список
            new_seats = get_subs_list(seat['id'])  # і шукаємо його підлеглих
            if new_seats is not None:  # якщо підлеглі є, додаємо і їх у список
                for new_seat in new_seats:
                    temp_seats.append({'id': new_seat['id']})
        return temp_seats
    else:
        return None


# Функція, яка рекурсією шукає всіх начальників посади користувача і їх начальників
def get_chiefs_list(seat):
    # Знаходимо id посади начальника
    chief_id = (Seat.objects.only('chief_id').filter(id=seat).first()).chief_id
    # Знаходимо людинопосаду начальника
    chief = [{
        'id': empSeat.id,
        'name': empSeat.employee.pip,
        'seat': empSeat.seat.seat if empSeat.is_main is True else empSeat.seat.seat + ' (в.о.)',
    } for empSeat in Employee_Seat.objects.filter(seat_id=chief_id).filter(is_active=True).filter(employee__on_vacation=False)]

    temp_chiefs = []
    if chief_id is not None:  # якщо начальник є:
        temp_chiefs.append(chief[0])
        new_chiefs = get_chiefs_list(chief_id)  # і шукаємо його начальника і так далі
        if new_chiefs is not None:  # якщо начальники є, додаємо і їх у список
            for new_chief in new_chiefs:
                temp_chiefs.append({
                    'id': new_chief['id'],
                    'name': new_chief['name'],
                    'seat': new_chief['seat']
                })
        return temp_chiefs
    else:
        return None


# Функція, яка повертає список всіх актуальних посад юзера
def get_my_seats(emp_id):
    my_seats = [{  # Список посад юзера
        'id': empSeat.id,
        'seat_id': empSeat.seat_id,
        'seat': empSeat.seat.seat if empSeat.is_main else '(в.о.) ' + empSeat.seat.seat,
    } for empSeat in Employee_Seat.objects.filter(employee_id=emp_id).filter(is_active=True)]
    return my_seats


# Функція, яка повертає з бд список відділів
def get_deps():
    deps = [{
        'id': dep.pk,
        'dep': dep.name,
        'text': dep.text,
    } for dep in accounts.Department.objects.filter(is_active=True).order_by('name')]
    return deps


# Функція, яка повертає з бд елементарний список посад
def get_seats():
    seats = [{
        'id': seat.pk,
        'seat': seat.seat,
    } for seat in Seat.objects.filter(is_active=True).order_by('seat')]
    return seats


# Функція, яка повертає список пунктів документу
def get_doc_articles(doc_id):
    articles = [{
        'id': article.id,
        'text': article.text,
        'deadline': None if not article.deadline else datetime.strftime(article.deadline, '%Y-%m-%d'),
        'deps': get_responsible_deps(article.id),  # Знаходимо список відповідальних за пункт окремою функцією
    } for article in Doc_Article.objects.filter(document_id=doc_id).filter(is_active=True)]

    return articles


# Функція, яка повертає з бд список відділів, відповідальних за виконання пункту документу
def get_responsible_deps(article_id):
    deps = [{
        'id': dep.department.id,
        'dep': dep.department.name,
    } for dep in Doc_Article_Dep.objects.filter(article_id=article_id).filter(is_active=True)]

    return deps


# Фунція, яка "видаляє" документ/чернетку
def close_doc(request, doc_id):
    try:
        doc = get_object_or_404(Document, pk=doc_id)
        doc_request = request.POST.copy()
        doc_request.update({'closed': True})
        close_doc_form = CloseDocForm(doc_request, instance=doc)
        if close_doc_form.is_valid():
            close_doc_form.save()
        else:
            raise ValidationError('edms/view func close_doc: close_doc_form invalid')
    except ValidationError as err:
        raise err
    except Exception as err:
        raise err


def send_email(email_type, recipients):
    for recipient in recipients:
        recipient_mail = Employee_Seat.objects.values('employee__user__email').filter(id=recipient['id'])
        mail = recipient_mail[0]['employee__user__email']

        if mail:
            HOST = "imap.polyprom.com"

            SUBJECT = "Новий електронний документ" \
                if email_type == 'new_doc' \
                else "Нова реакція на Ваш електронний документ"

            TO = 'sauron4er@gmail.com' if testing else mail

            FROM = "it@lxk.com.ua"

            text = "Вашої реакції очікує новий документ. " \
                   "Щоб переглянути, перейдіть за посиланням: http://plhk.com.ua/edms/my_docs/" \
                if email_type == 'new_doc' \
                else "У Вашого електронного документу з’явилася нова позначка. " \
                     "Щоб переглянути, перейдіть за посиланням: http://plhk.com.ua/edms/my_docs/"

            BODY = u"\r\n".join((
                "From: " + FROM,
                "To: " + TO,
                "Subject: " + SUBJECT,
                "",
                text
            )).encode('utf-8').strip()

            server = smtplib.SMTP(HOST)
            server.login('lxk_it', 'J2NYEHb50nymRF1L')
            server.sendmail(FROM, [TO], BODY)
            server.quit()


# ---------------------------------------------------------------------------------------------------------------------
# функції модульних документів

# Функція, яка додає у бд новий документ та повертає його id
def post_document(request):
    try:
        doc_request = request.POST.copy()
        doc_request.update({'employee': request.user.userprofile.id})
        doc_request.update({'text': request.POST.get('text', None)})  # Якщо поля text немає, у форму надсилається null

        doc_form = DocumentForm(doc_request)
        if doc_form.is_valid():
            new_doc = doc_form.save()
            return new_doc
        else:
            raise ValidationError('edms/views: function post_document: document_form invalid')
    except Exception as err:
        raise err


# Функція, яка перебирає список модулів і викликає необхідні функції для їх публікації
# Повертає список отримувачів документа (якщо використовується модуль recipient_chief)
def post_modules(doc_request, doc_modules, doc_files, new_path):
    recipients = []
    # Додаємо назву документа
    if 'name' in doc_modules:
        post_name(doc_request, doc_modules['name'])

    # Додаємо текст документа
    if 'text' in doc_modules:
        post_text(doc_request, doc_modules['text'])

    # Додаємо отримувача-шефа
    # Отримувач-шеф отримує mark-demand з вимогою поставити "Погоджую"
    # Звичайний отримувач - якусь іншу позначку.
    if 'recipient_chief' in doc_modules:
        recipient_id = post_recipient_chief(doc_request, doc_modules['recipient_chief'], new_path.pk)
        recipients = [{'id': recipient_id}]

    # Додаємо преамбулу документа
    if 'preamble' in doc_modules:
        post_preamble(doc_request, doc_modules['preamble'])

    # Додаємо погоджуючих
    if 'approval_seats' in doc_modules:
        post_approval_seats(doc_request, doc_modules['approval_seats'])

    # Додаємо пункти
    if 'articles' in doc_modules:
        post_articles(doc_request, doc_modules['articles'])

    # Додаємо дату
    if 'day' in doc_modules:
        post_day(doc_request, doc_modules['day'])

    # Додаємо прохідну
    if 'gate' in doc_modules:
        post_gate(doc_request, doc_modules['gate'])

    # Додаємо список матеріальних цінностей
    if 'carry_out_items' in doc_modules:
        post_carry_out_items(doc_request, doc_modules['carry_out_items'])

    # Додаємо файли
    if doc_files:
        # Поки що файли додаються тільки якщо документ публікується не як чернетка
        # Для публікації файла необідно мати перший path_id документа, якго нема в чернетці
        if new_path is not None:
            handle_files(doc_files, doc_request, new_path.pk)

    return recipients


# Функція, яка додає у бд нові пункти документу
def post_articles(doc_request, articles):
    try:
        for article in articles:
            doc_request.update({
                'text': article['text'],
                'deadline': article['deadline'],
            })
            article_form = NewArticleForm(doc_request)
            if article_form.is_valid():
                new_article_id = article_form.save().pk
                for dep in article['deps']:
                    doc_request.update({'article': new_article_id})
                    doc_request.update({'department': dep['id']})
                    article_dep_form = NewArticleDepForm(doc_request)
                    if article_dep_form.is_valid():
                        article_dep_form.save()
                    else:
                        raise ValidationError('edms/view func post_articles: article_dep_form invalid')
            else:
                raise ValidationError('edms/view func post_articles: article_form invalid')
    except ValueError as err:
        raise err


# Функція, яка додає у бд список погоджуючих
def post_approval_seats(doc_request, approval_seats):
    for item in approval_seats:
        doc_request.update({'seat': item})
        approval_form = NewApprovalForm(doc_request)
        if approval_form.is_valid():
            approval_form.save()
        else:
            raise ValidationError('edms/views post_approval_seats approval_form invalid')


# Функція, яка додає у бд назву документу
def post_name(doc_request, name):
    doc_request.update({'name': name})
    name_form = NewNameForm(doc_request)
    if name_form.is_valid():
        name_form.save()
    else:
        raise ValidationError('edms/views post_name name_form invalid')


# Функція, яка додає у бд текст документу
def post_text(doc_request, text):
    doc_request.update({'text': text})
    text_form = NewTextForm(doc_request)
    if text_form.is_valid():
        text_form.save()
    else:
        raise ValidationError('edms/views post_text text_form invalid')


# Функція, яка додає у бд отримувача
def post_recipient_chief(doc_request, recipient_chief, path_id):
    doc_request.update({'mark': 2})
    doc_request.update({'recipient': recipient_chief['id']})
    doc_request.update({'document_path': path_id})

    recipient_form = NewRecipientForm(doc_request)
    if recipient_form.is_valid():
        recipient_form.save()
    else:
        raise ValidationError('edms/views post_recipient_chief recipient_form invalid')

    # Заносимо документ у mark_demand
    chief_mark_demand_form = MarkDemandForm(doc_request)
    if chief_mark_demand_form.is_valid:
        chief_id = chief_mark_demand_form.save()
        return chief_id.recipient_id
    else:
        raise ValidationError('edms/views post_recipient_chief chief_mark_demand_form invalid')


# Функція, яка додає у бд преамбулу документу
def post_preamble(doc_request, preamble):
    doc_request.update({'preamble': preamble})
    preamble_form = NewPreambleForm(doc_request)
    if preamble_form.is_valid():
        preamble_form.save()
    else:
        raise ValidationError('edms/views post_preamble preamble_form invalid')


# Функція, яка додає у бд дату документу
def post_day(doc_request, day):
    doc_request.update({'day': day})
    day_form = NewDayForm(doc_request)
    if day_form.is_valid():
        day_form.save()
    else:
        raise ValidationError('edms/views post_day day_form invalid')


# Функція, яка додає у бд прохідну
def post_gate(doc_request, gate):
    doc_request.update({'gate': gate})
    gate_form = NewGateForm(doc_request)
    if gate_form.is_valid():
        gate_form.save()
    else:
        raise ValidationError('edms/views post_day day_form invalid')


# Функція, яка додає у бд дату документу
def post_carry_out_items(doc_request, carry_out_items):
    for item in carry_out_items:
        doc_request.update({'item_name': item['item_name']})
        doc_request.update({'quantity': item['quantity']})
        doc_request.update({'measurement': item['measurement']})
        carry_out_item_form = CarryOutItemsForm(doc_request)
        if carry_out_item_form.is_valid():
            carry_out_item_form.save()
        else:
            raise ValidationError('edms/views post_carry_out_item carry_out_item_form invalid')


# Функція, яка постить файли
def handle_files(doc_files, doc_request, path_id):
    if len(doc_files) > 0:
        # TODO додати обробку помилок при збереженні файлів
        doc_request.update({'document_path': path_id})
        doc_request.update({'name': 'file'})

        file_form = NewFileForm(doc_request, doc_files)
        if file_form.is_valid():
            document_path = file_form.cleaned_data['document_path']
            for f in doc_files.getlist('file'):
                File.objects.create(
                    document_path=document_path,
                    file=f,
                    name=f.name
                )
        else:
            raise ValidationError('edms/views: function handle_files: file_form invalid')
# ---------------------------------------------------------------------------------------------------------------------


@login_required(login_url='login')
def edms_main(request):
    if request.method == 'GET':
        return render(request, 'edms/main.html')
    return HttpResponse(status=405)


@login_required(login_url='login')
def edms_hr(request):
    if request.method == 'GET':

        deps = get_deps()

        seats = [{       # Список посад для форм на сторінці відділу кадрів
            'id': seat.pk,
            'seat': seat.seat,
            'dep': 'Не внесено' if seat.department is None else seat.department.name,
            'dep_id': 0 if seat.department is None else seat.department.id,
            'is_dep_chief': 'true' if seat.is_dep_chief else 'false',
            'chief': 'Не внесено' if seat.chief is None else seat.chief.seat,
            'chief_id': 0 if seat.chief is None else seat.chief.id,
        } for seat in Seat.objects.all().filter(is_active=True).order_by('seat')]

        # Додаємо поле "вакансія" у список посад (посада, де вакансія = True, буде виділятися червоним)
        for seat in seats:
            occupied_by = Employee_Seat.objects.filter(seat_id=seat['id']).filter(is_active=True).first()
            seat['is_vacant'] = 'true' if occupied_by is None else 'false'

        emps = [{       # Список працівників для форм на сторінці відділу кадрів
            'id': emp.pk,
            'emp': emp.pip,
            'on_vacation': 'true' if emp.on_vacation else 'false',
            'acting': 0 if emp.acting is None else emp.acting.pip,
            'acting_id': 0 if emp.acting is None else emp.acting.id,
        } for emp in accounts.UserProfile.objects.only(
            'id', 'pip', 'on_vacation', 'acting').filter(is_active=True).order_by('pip')]

        return render(request, 'edms/hr/hr.html', {
            'deps': deps,
            'seats': seats,
            'emps': emps,
        })

    elif request.method == 'POST':

        if 'new_dep' in request.POST:
            form = DepartmentForm(request.POST)
            if form.is_valid():
                new_dep = form.save()
                return HttpResponse(new_dep.pk)

        if 'new_seat' in request.POST:
            form = SeatForm(request.POST)
            if form.is_valid():
                new_seat = form.save()
                return HttpResponse(new_seat.pk)

        if 'new_emp_seat' in request.POST:
            form_employee_seat = EmployeeSeatForm(request.POST)
            if form_employee_seat.is_valid():
                new_emp_seat = form_employee_seat.save()
                return HttpResponse(new_emp_seat.pk)

    return HttpResponse(status=405)


@login_required(login_url='login')
def edms_administration(request):
    if request.method == 'GET':
        my_seats = get_my_seats(request.user.userprofile.id)
        seats = [{  # Список посад для форм на сторінці відділу кадрів
            'id': seat.pk,
            'seat': seat.seat,
        } for seat in Seat.objects.filter(is_active=True).order_by('seat')]
        marks = [{
            'id': mark.pk,
            'mark': mark.mark,
        } for mark in Mark.objects.filter(is_active=True)]
        return render(request, 'edms/administration/administration.html', {
            'my_seats': my_seats,
            'seats': seats,
            'marks': marks,
        })

    if request.method == 'POST':
        form = DTPAddForm(request.POST)
        if form.is_valid():
            new_dtp = form.save()
            return HttpResponse(new_dtp.pk)

    return HttpResponse(status=405)


@login_required(login_url='login')
def edms_deactivate_permission(request, pk):
    permission = get_object_or_404(Document_Type_Permission, pk=pk)
    if request.method == 'POST':
        form = DTPDeactivateForm(request.POST, instance=permission)
        if form.is_valid():
            form.save()
            return redirect('administration.html')


@login_required(login_url='login')
def edms_get_types(request, pk):
    # Отримуємо ід посади з ід людинопосади
    seat_id = Employee_Seat.objects.filter(id=pk).values_list('seat_id')[0][0]

    if request.method == 'GET':
        if request.user.userprofile.is_it_admin:
            doc_types_query = Document_Type.objects.all()

            # Якщо параметр testing = False - програма показує лише ті типи документів, які не тестуються.
            if not testing:
                doc_types_query = doc_types_query.filter(testing=False)

            doc_types = [{
                'id': doc_type.id,
                'description': doc_type.description,
                'creator': '' if doc_type.creator_id is None else doc_type.creator.employee.pip,
            } for doc_type in doc_types_query]

            return HttpResponse(json.dumps(doc_types))
        else:
            doc_types = [{
                'id': doc_type.id,
                'description': doc_type.description,
                'creator': '' if doc_type.creator_id is None else doc_type.creator.employee.pip,
            } for doc_type in Document_Type.objects.filter(creator_id=seat_id)]

            # Відділ кадрів може змінювати свої документи та загальні (не створені іншими користувачами)
            if request.user.userprofile.is_hr:
                hr_doc_types = [{
                    'id': doc_type.id,
                    'description': doc_type.description,
                    'creator': '',
                } for doc_type in Document_Type.objects.filter(creator_id=None).filter(testing=False)]
                doc_types = doc_types + hr_doc_types

            return HttpResponse(json.dumps(doc_types))


@login_required(login_url='login')
def edms_get_type_info(request, pk):
    # Отримуємо ід типу документу
    doc_type_id = Document_Type.objects.filter(id=pk).values_list('id')[0][0]

    if request.method == 'GET':
        permissions = [{  # Список дозволів для посад для цього документу
            'id': permission.id,
            'seat_id': permission.seat.id,
            'seat': permission.seat.seat,
            'mark_id': permission.mark.id,
            'mark': permission.mark.mark,
        } for permission in Document_Type_Permission.objects
            .filter(document_type_id=doc_type_id)
            .filter(is_active=True)]

        return HttpResponse(json.dumps(permissions))


@login_required(login_url='login')
def edms_hr_emp(request, pk):       # changes in employee row
    post = get_object_or_404(accounts.UserProfile, pk=pk)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('hr.html')
    elif request.method == 'GET':
        emp_seats = [{  # список зв’язків посада-співробітник
            'id': empSeat.pk,
            'seat': empSeat.seat.seat,
        } for empSeat in Employee_Seat.objects.only('id', 'seat').filter(employee_id=pk).filter(is_active=True).order_by('seat')]
        return HttpResponse(emp_seats)


@login_required(login_url='login')
def edms_hr_dep(request, pk):       # changes in department row
    post = get_object_or_404(accounts.Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('hr.html')


@login_required(login_url='login')
def edms_hr_seat(request, pk):       # changes in seat row
    post = get_object_or_404(Seat, pk=pk)
    if request.method == 'POST':
        form = SeatForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('hr.html')


@login_required(login_url='login')
def edms_hr_emp_seat(request, pk):       # changes in emp_seat row
    post = get_object_or_404(Employee_Seat, pk=pk)
    if request.method == 'POST':
        form_request = request.POST.copy()
        form = EmployeeSeatForm(form_request, instance=post)

        # Обробка звільнення з посади:
        if form.data['is_active'] == 'false':
            active_docs = Mark_Demand.objects.filter(recipient_id=pk).filter(is_active=True).first()
            # Якщо у mark_demand є хоча б один документ і не визначено "спадкоємця", повертаємо помилку
            if active_docs is not None and form.data['successor_id'] == '':
                return HttpResponseForbidden('active flow')
            # В іншому разі зберігаємо форму і додаємо "спадкоємцю" (якщо такий є) посаду:
            else:
                if form.data['successor_id'] != '':
                    successor_temp = {
                        'employee': form.data['successor_id'],
                        'seat': form.data['seat'],
                        'is_active': True,
                        'is_main': form.data['new_is_main']
                    }
                    successor = QueryDict('').copy()
                    successor.update(successor_temp)
                    successor_form = EmployeeSeatForm(successor)
                    if successor_form.is_valid():
                        new_successor = successor_form.save()
                        form.data['successor'] = new_successor.pk
                        if form.is_valid():
                            form.save()
                            return HttpResponse('')
                else:
                    if form.is_valid():
                        form.save()
                        return HttpResponse('')


@login_required(login_url='login')
def edms_get_emp_seats(request, pk):
    emp = get_object_or_404(accounts.UserProfile, pk=pk)
    if request.method == 'GET':
        emp_seats = [{
            'id': empSeat.pk,
            'emp_seat': empSeat.seat.seat if empSeat.is_main is True else empSeat.seat.seat + ' (в.о.)',
            'seat_id': empSeat.seat.pk,
            'emp_id': empSeat.employee.pk,
        } for empSeat in
            Employee_Seat.objects.only('id', 'seat', 'employee').filter(employee_id=emp).filter(is_active=True)]

        return HttpResponse(json.dumps(emp_seats))


@login_required(login_url='login')
def edms_get_chiefs(request, pk):
    emp_seat = get_object_or_404(Employee_Seat, pk=pk)
    seat_id = (Employee_Seat.objects.only('seat_id').filter(id=emp_seat.pk).first()).seat_id
    if request.method == 'GET':
        chiefs_list = get_chiefs_list(seat_id)
        # Перевертаємо список шефів (якщо він є), щоб директор був перший у списку (для автоматичного вибору у select)
        if chiefs_list:
            chiefs_list.reverse()
        return HttpResponse(json.dumps(chiefs_list))


@login_required(login_url='login')
def edms_get_direct_subs(request, pk):
    if request.method == 'GET':
        emp_seat = get_object_or_404(Employee_Seat, pk=pk)
        seat_id = (Employee_Seat.objects.only('seat_id').filter(id=emp_seat.pk).first()).seat_id
        direct_subs = [{
            'id': empSeat.id,
            'name': empSeat.employee.pip,
            'seat': empSeat.seat.seat,
            'is_active': True,
        } for empSeat in Employee_Seat.objects.filter(seat__chief_id=seat_id).filter(is_active=True)]  # Знаходимо підлеглих посади
        return HttpResponse(json.dumps(direct_subs))


@login_required(login_url='login')
def edms_get_doc(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'GET':
        # Всю інформацію про документ записуємо сюди
        doc_info = {}

        # Шукаємо path i flow документа, якщо це не чернетка:
        if not doc.is_draft:
            path = [{
                'id': path.id,
                'time': convert_to_localtime(path.timestamp, 'time'),
                'mark_id': path.mark_id,
                'mark': path.mark.mark,
                'emp_seat_id': path.employee_seat_id,
                'emp': path.employee_seat.employee.pip,
                'seat': path.employee_seat.seat.seat if path.employee_seat.is_main else '(в.о.) ' + path.employee_seat.seat.seat,
                'comment': path.comment,
            } for path in Document_Path.objects.filter(document_id=doc.pk).order_by('-timestamp')]

            # Перебираємо шлях документа в пошуках резолюцій і додаємо їх до відповідного запису в path
            for step in path:
                if step['mark_id'] == 10:
                    resolutions = [{
                        'id': res.id,
                        'emp_seat_id': res.recipient.id,
                        'emp': res.recipient.employee.pip,
                        'seat': res.recipient.seat.seat,
                        'comment': res.comment,
                    } for res in Mark_Demand.objects.filter(document_path_id=step['id'])]
                    step['resolutions'] = resolutions

            # Перебираємо шлях документа в пошуках файлів і додаємо їх до відповідного запису в path
            for step in path:
                files = [{
                    'id': file.id,
                    'file': file.file.name,
                    'name': file.name,
                    'path_id': file.document_path.id,
                    'mark_id': file.document_path.mark.id,
                } for file in File.objects.filter(document_path_id=step['id'])]
                step['files'] = files

            # В кого на черзі документ
            flow = [{
                'id': demand.id,
                'emp_seat_id': demand.recipient.id,
                'emp': demand.recipient.employee.pip,
                'seat': demand.recipient.seat.seat if demand.recipient.is_main else '(в.о.) ' + demand.recipient.seat.seat,
                'expected_mark': demand.mark_id,
            } for demand in Mark_Demand.objects.filter(document_id=doc.pk).filter(is_active=True)]

            doc_info = {
                'path': path,
                'flow': flow
            }

        # отримуємо з бд список модулів, які використовує цей тип документа:
        type_modules = [{
            'module': type_module.module.module,
            'field_name': None if type_module.field_name is None else type_module.field_name,
        } for type_module in Document_Type_Module.objects
            .filter(document_type_id=doc.document_type_id)
            .filter(is_active=True)
            .order_by('queue')]
        doc_info.update({
            'type_modules': type_modules,
        })

        # збираємо з використовуваних модулів інфу про документ
        for module in type_modules:
            if module['module'] == 'name':
                name = [{
                    'name': item.name,
                } for item in Doc_Name.objects.filter(document_id=doc.id).filter(is_active=True)]

                doc_info.update({
                    'name': name[0]['name'],
                })
            elif module['module'] == 'preamble':
                test = 'test'
            elif module['module'] == 'text':
                text = [{
                    'text': item.text,
                } for item in Doc_Text.objects.filter(document_id=doc.id).filter(is_active=True)]

                doc_info.update({
                    'text': text[0]['text'],
                })
            elif module['module'] == 'articles':
                test = 'test'
            elif module['module'] == 'recipient' or module['module'] == 'recipient_chief':
                recipient = [{
                    'id': item.recipient.id,
                    'name': item.recipient.employee.pip,
                    'seat': item.recipient.seat.seat
                    if item.recipient.is_main
                    else '(в.о.) ' + item.recipient.seat.seat,
                } for item in Doc_Recipient.objects.filter(document_id=doc.id).filter(is_active=True)]

                doc_info.update({
                    'recipient': {
                        'id': recipient[0]['id'],
                        'name': recipient[0]['name'],
                        'seat': recipient[0]['seat'],
                    }
                })
            elif module['module'] == 'approvals':
                test = 'test'
            elif module['module'] == 'files':
                test = 'test'
            elif module['module'] == 'day':
                day = [{
                    'day': datetime.strftime(item.day, '%Y-%m-%d'),
                } for item in Doc_Day.objects.filter(document_id=doc.id).filter(is_active=True)]

                doc_info.update({
                    'day': day[0]['day'],
                })
            elif module['module'] == 'gate':
                gate = [{
                    'gate': item.gate,
                } for item in Doc_Gate.objects.filter(document_id=doc.id).filter(is_active=True)]

                doc_info.update({
                    'gate': gate[0]['gate'],
                })
            elif module['module'] == 'carry_out_items':
                    items = [{
                        'id': item.id,
                        'item_name': item.item_name,
                        'quantity': item.quantity,
                        'measurement': item.measurement,
                    } for item in Carry_Out_Items.objects.filter(document_id=doc.id)]

                    # Індексуємо список товарів, щоб id товарів не бралися з таблиці а створювалися з 1
                    items_indexed = [{
                        'id': items.index(item) + 1,
                        'item_name': item['item_name'],
                        'quantity': item['quantity'],
                        'measurement': item['measurement'],
                    } for item in items]

                    doc_info.update({'carry_out_items': items_indexed})

        return HttpResponse(json.dumps(doc_info))


@transaction.atomic
@login_required(login_url='login')
def edms_my_docs(request):
    try:
        if request.method == 'GET':
            my_seats = get_my_seats(request.user.userprofile.id)

            new_docs_query = Document_Type.objects.all()
            my_docs_query = Document_Path.objects.filter(mark=1) \
                .filter(employee_seat__employee_id=request.user.userprofile.id) \
                .filter(document__is_draft=False) \
                .filter(document__is_active=True) \
                .filter(document__closed=False)  # Створено користувачем, не чернетка і не деактивовано
            work_docs_query = Mark_Demand.objects \
                .filter(recipient_id__employee_id=request.user.userprofile.id) \
                .filter(is_active=True).order_by('document_id')

            # Якщо параметр testing = False - програма показує лише ті типи документів, які не тестуються.
            if not testing:
                new_docs_query = new_docs_query.filter(testing=False)
                my_docs_query = my_docs_query.filter(document__document_type__testing=False)
                work_docs_query = work_docs_query.filter(document__document_type__testing=False)

            new_docs = [{  # Список документів, які може створити юзер
                'id': doc_type.id,
                'description': doc_type.description,
            } for doc_type in new_docs_query]  # В режимі тестування показуються типи документів, що тестуються

            my_docs = [{  # Список документів, створених даним юзером
                'id': path.document.id,
                'type': path.document.document_type.description,
                'type_id': path.document.document_type.id,
                'date': convert_to_localtime(path.timestamp, 'day'),
                'emp_seat_id': path.employee_seat.id,
                'author': request.user.userprofile.pip,
                'author_seat_id': path.employee_seat.id,
            } for path in my_docs_query]

            work_docs = [{  # Список документів, що очікують на реакцію користувача
                'id': demand.document.id,
                'type': demand.document.document_type.description,
                'type_id': demand.document.document_type_id,
                'flow_id': demand.id,
                'date': convert_to_localtime(demand.document.date, 'day'),
                'emp_seat_id': demand.recipient.id,
                'expected_mark': demand.mark.id,
                'author': demand.document.employee_seat.employee.pip,
                'author_seat_id': demand.document.employee_seat_id,
            } for demand in work_docs_query]

            return render(request, 'edms/my_docs/my_docs.html', {
                'new_docs': new_docs, 'my_docs': my_docs, 'my_seats': my_seats, 'work_docs': work_docs
            })

        elif request.method == 'POST':
            doc_request = request.POST.copy()
            doc_files = request.FILES.copy()

            # Записуємо документ і отримуємо його ід
            new_doc = post_document(request)
            doc_request.update({'document': new_doc.pk})

            # id першого запису в document_path: переробиться на створення запису прямо з django
            new_path = Document_Path.objects.filter(document_id=new_doc.pk).filter(mark_id=1).first()

            # Модульна система:
            # В деяких модулях прямо може бути вказано отримувача,
            # тому post_modules повертає список отримувачів, який може бути і пустий
            doc_modules = json.loads(request.POST['doc_modules'])
            recipients = post_modules(doc_request, doc_modules, doc_files, new_path)

            # Система стадій документа (phases)
            type_phases = [{
                'phase': type_phase.mark_id,
            } for type_phase in Doc_Type_Phase.objects
                .filter(document_type_id=new_doc.document_type_id)
                .filter(is_active=True)
                .order_by('queue')]

            # Деактивуємо стару чернетку
            if doc_request['old_draft_id'] != '0':
                close_doc(request, int(doc_request['old_draft_id']))

            # Відправляємо листа отримувачу:
            if new_path is not None:
                if not recipients:
                    test = 'test'
                    # recipients = Mark_Demand.objects.values('recipient_id').filter(document_path_id=new_path.pk)
                else:
                    send_email('new_doc', recipients)

            return HttpResponse(new_doc_id)
    except ValidationError as err:
        raise err
        # return HttpResponse(status=405, content=err)
    except Exception as err:
        raise err
        # return HttpResponse(status=405, content=err)


@login_required(login_url='login')
def edms_get_doc_type_modules(request, pk):
    if request.method == 'GET':
        doc_type = get_object_or_404(Document_Type, pk=pk)
        doc_type_modules = [{
            'module': type_module.module.module,
            'field_name': None if type_module.field_name is None else type_module.field_name,
            # 'queue': type_module.queue,
            'required': type_module.required,
        } for type_module in Document_Type_Module.objects
            .filter(document_type_id=doc_type)
            .filter(is_active=True)
            .order_by('queue')]
        return HttpResponse(json.dumps(doc_type_modules))


@login_required(login_url='login')
def edms_get_drafts(request):
    try:
        if request.method == 'GET':
            my_drafts_query = Document.objects\
                .filter(employee_seat__employee_id=request.user.userprofile.id)\
                .filter(is_draft=True)\
                .filter(closed=False)

            # Якщо параметр testing = False - програма показує лише ті типи документів, які не тестуються.
            if not testing:
                my_drafts_query = my_drafts_query.filter(document_type__testing=False)

            my_drafts = [{  # Список документів, створених даним юзером
                'id': draft.id,
                'type': draft.document_type.description,
                'type_id': draft.document_type.id,
                'date': convert_to_localtime(draft.date, 'day'),
            } for draft in my_drafts_query]

            response = my_drafts if len(my_drafts) > 0 else []

            return HttpResponse(json.dumps(response))
    except Exception as err:
        return HttpResponse(status=405, content=err)


@login_required(login_url='login')
def edms_del_draft(request, pk):
    try:
        if request.method == 'POST':
            close_doc(request, pk)
            return HttpResponse(pk)
    except Exception as err:
        return HttpResponse(status=405, content=err)


@login_required(login_url='login')
def edms_archive(request):
    if request.method == 'GET':
        my_seats = get_my_seats(request.user.userprofile.id)

        my_archive_query = Document_Path.objects.filter(mark=1) \
            .filter(mark=1).filter(employee_seat__employee_id=request.user.userprofile.id) \
            .filter(document__is_active=False) \
            .filter(document__closed=False)

        work_archive_query = Document_Path.objects.distinct() \
            .filter(employee_seat_id__employee_id=request.user.userprofile.id) \
            .filter(document__closed=False) \
            .exclude(document__employee_seat__employee=request.user.userprofile.id)  # Автор не користувач

        # Якщо параметр testing = False - програма показує лише ті типи документів, які не тестуються.
        if not testing:
            my_archive_query = my_archive_query.filter(document__document_type__testing=False)
            work_archive_query = work_archive_query.filter(document__document_type__testing=False)

        my_archive = [{  # Список документів, створених даним юзером
            'id': path.document.id,
            'type': path.document.document_type.description,
            'type_id': path.document.document_type.id,
            'date': convert_to_localtime(path.timestamp, 'day'),
            'emp_seat_id': path.employee_seat.id,
            'author_seat_id': path.employee_seat.id,
        } for path in my_archive_query]

        work_archive_with_duplicates = [{  # Список документів, які були у роботі користувача
            'id': path.document_id,
            'type': path.document.document_type.description,
            'type_id': path.document.document_type_id,
            'date': convert_to_localtime(path.document.date, 'day'),
            'emp_seat_id': path.employee_seat_id,
            'author': path.document.employee_seat.employee.pip,
            'author_seat_id': path.document.employee_seat_id,
        } for path in work_archive_query]

        # Позбавляємось дублікатів:
        work_archive = list({item["id"]: item for item in work_archive_with_duplicates}.values())

        return render(request, 'edms/archive/archive.html', {
            'my_seats': my_seats, 'my_archive': my_archive, 'work_archive': work_archive,
        })
    return HttpResponse(status=405)


@login_required(login_url='login')
def edms_sub_docs(request):
    if request.method == 'GET':
        my_seats = get_my_seats(request.user.userprofile.id)

        return render(request, 'edms/sub_docs/sub_docs.html', {
            'my_seats': my_seats,
        })
    return HttpResponse(status=405)


@login_required(login_url='login')
def edms_get_sub_docs(request, pk):
    if request.method == 'GET':
        # Отримуємо ід посади з ід людинопосади
        seat_id = Employee_Seat.objects.filter(id=pk).values_list('seat_id')[0][0]

        # Список всіх підлеглих користувача:
        subs_list = get_subs_list(int(seat_id))

        # Шукаємо документи кожного підлеглого
        sub_docs = []
        if subs_list:
            for sub in subs_list:

                docs_query = Document_Path.objects \
                    .filter(mark_id=1) \
                    .filter(employee_seat__seat_id=sub['id']) \
                    .filter(document__closed=False) \

                # Якщо параметр testing = False - програма показує лише ті типи документів, які не тестуються.
                if not testing:
                    docs_query = docs_query.filter(document__document_type__testing=False)

                docs = [{  # Список документів у роботі, створених підлеглими юзера
                    'id': path.document_id,
                    'type': path.document.document_type.description,
                    'type_id': path.document.document_type_id,
                    'date': datetime.strftime(path.timestamp, '%d.%m.%Y'),
                    'author_seat_id': path.employee_seat_id,
                    'author': path.employee_seat.employee.pip,
                    'dep': path.employee_seat.seat.department.name,
                    'emp_seat_id': int(pk),
                    'is_active': path.document.is_active,
                } for path in docs_query]

                if docs:
                    for doc in docs:
                        sub_docs.append(doc)
        return HttpResponse(json.dumps(sub_docs))

    return HttpResponse(status=405)


@transaction.atomic
@login_required(login_url='login')
def edms_mark(request):
    try:
        if request.method == 'POST':
            # Якщо документ намагаються видалити, шукаємо, чи хтось не відреагував на нього
            # Якщо позначки від інших користувачів є - відмовляємо у видаленні
            if request.POST['mark'] == '13':
                deletable = Document_Path.objects\
                    .filter(document_id=request.POST['document'])\
                    .exclude(employee_seat_id=request.POST['employee_seat'])

                if len(deletable) > 0:
                    return HttpResponse('not deletable')

            path_form = DocumentPathForm(request.POST)
            if path_form.is_valid():
                new_path = path_form.save()
            else:
                raise ValidationError('view edms_mark: path_form invalid')

            # Додаємо файли, якщо такі є:
            doc_request = request.POST.copy()
            handle_files(request.FILES, doc_request, new_path.pk)

            return HttpResponse(new_path.pk)
    except ValidationError as err:
        raise err
    except Exception as err:
        raise err


@login_required(login_url='login')
def edms_resolution(request):
    if request.method == 'POST':

        # отримуємо список резолюцій з request і публікуємо їх усі у базу
        resolutions = json.loads(request.POST['resolutions'])
        res_request = request.POST.copy()
        for res in resolutions:
            res_request.update({'recipient': res['recipient_id']})
            res_request.update({'comment': res['comment']})
            resolution_form = ResolutionForm(res_request)
            if resolution_form.is_valid():
                new_res = resolution_form.save()
            else:
                return HttpResponse(status=405)
        return HttpResponse('')


@login_required(login_url='login')
def edms_get_deps(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps(get_deps()))
    return HttpResponse(status=405)


@login_required(login_url='login')
def edms_get_seats(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps(get_seats()))
    return HttpResponse(status=405)