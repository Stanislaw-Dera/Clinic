import json
from datetime import date, datetime, time

from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest, PermissionDenied
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from appointments.models import Appointment, Category
from appointments.utils import get_app_hours
from users.models import WorkDay, Doctor, User, Patient

from clinic import settings

date_options = ['desc', 'asc']
status_options = ['all', 'upcoming', 'cancelled', 'finished']

# Create your views here.
@login_required(redirect_field_name=None)
def patient_history(request):
    if request.user.role != 'p':
        raise PermissionDenied('Only Patients can access this page.')

    doctors: set[User] = {a.doctor for a in Appointment.objects.filter(patient=request.user)}

    doctor_options = [[doc.id, doc.get_full_name()] for doc in doctors]

    return render(request, 'appointments/patient_history.html', {
        'date_options': date_options,
        'status_options': status_options,
        'doctor_options': doctor_options
    })

@login_required(redirect_field_name=None)
def patient_history_api(request):
    if request.user.role != 'p':
        raise PermissionDenied('Only Patients can access this page. ')

    appointments = Appointment.objects.filter(patient=request.user)

    if appointments is None:
        return JsonResponse({'message': "You haven't scheduled nor completed any appointments yet. "}, status=200)

    date_filter = request.GET.get('date')
    status_filter = request.GET.get('status')
    doc_filter = request.GET.get('doc-id')

    print(date_filter, '|', status_filter, '|', doc_filter)

    if not status_filter or status_filter == 'all':
        # appointments = appointments.all()
        pass
    elif status_filter in ['upcoming', 'cancelled', 'finished']:
        appointments = appointments.filter(status=status_filter.capitalize())
    else:
        raise BadRequest('Invalid status filter. Available options are: upcoming, cancelled, finished, all')

    if not date_filter:
        date_filter = 'desc'
    elif date_filter in ['asc', 'desc']:
        pass
    else:
        raise BadRequest('Invalid date filter. Available options are: asc, desc.')

    if not doc_filter or doc_filter == 'all':
        pass
    else:
        try:
            appointments = appointments.filter(doctor=User.objects.get(id=doc_filter))
        except User.DoesNotExist:
            raise BadRequest('Invalid doctor filter.')

    appointments = appointments.order_by('-date_time' if date_filter == "desc" else 'date_time')

    page = request.GET.get('page')
    print(page)

    try:
        paginator = Paginator(appointments, 5)
    except EmptyPage:
        raise BadRequest('No more pages to load. ')

    appointments = paginator.page(page)

    print(appointments)
    return JsonResponse([appointment.serialize() for appointment in appointments], safe=False)

def patient_history_doc(request, patient_id):
    if request.user.role != 'd':
        raise BadRequest('Only Doctors can access this page. ')

    patient = User.objects.get(id=patient_id)

    appointments = Appointment.objects.filter(patient=patient, doctor=request.user)

    if not appointments.exists():
        return JsonResponse({'message': 'Patient visits you for the first time.'}, status=200)

    return JsonResponse([appointment.serialize() for appointment in appointments], safe=False)
# implement pagination, 5app/page

# doc history for one day

def get_doc_booking_data(request, doc_id):
    day = request.GET.get('day')
    month = request.GET.get('month')
    year = request.GET.get('year')

    dt = date(int(year), int(month), int(day))
    if dt < date.today():
        raise BadRequest("You can't book visits for past days.")
    elif dt == date.today():
        dt = datetime.now()
    else:
        dt = datetime.combine(dt, time(6, 0))

    closure = dt.replace(hour=settings.CLINIC_CLOSURE.hour, minute=settings.CLINIC_CLOSURE.minute)

    doc = User.objects.get(id=doc_id)
    blocks = WorkDay.filters.filter_by_doc_and_date(doc=doc, date=dt.date()).workblocks.filter(
        start__range=(dt.time(), closure.time())).order_by('start')

    appointments = Appointment.objects.filter(doctor=doc, date_time=dt)

    app_hours = get_app_hours(appointments)

    available_hours = [block.start.strftime('%H:%M') for block in blocks if block.start not in app_hours]

    categories = []
    if request.user.role == 'p':
        categories = Category.objects.for_patient()

    elif request.user.role == 'd':
        categories = Category.objects.for_doctor()

    return JsonResponse(
        {'bookingHours': available_hours, 'categories': [c.name for c in categories], 'date': dt.date()}, safe=False,
        status=200)


def manage_appointment(request, user_id):
    pass
    # POST, PUT, DELETE appointments
    # one at the time at one doctor.

    if request.method == 'POST':
        dt = request.POST.get('datetime')
        category = request.POST.get('category')
        print(dt)
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M')

        if request.user.role == 'p':
            doc = User.objects.get(pk=user_id)

            if not Doctor.objects.get(user=doc).exists():
                return JsonResponse({'message': 'Doctor does not exist'}, status=400)

            patient = request.user
        elif request.user.role == 'd':
            doc = request.user
            patient = User.objects.get(pk=user_id)

            if not patient.objects.get(user=patient).exists():
                return JsonResponse({'message': 'Patient does not exist'}, status=400)
        else:
            return HttpResponse("???? Man you're not even a user", status=400)

        # check if time is available
        blocks = WorkDay.filters.filter_by_doc_and_date(doc=doc, date=dt.date()).workblocks.all()
        app_hours = get_app_hours(Appointment.objects.filter(doctor=doc, date_time__year=dt.year,
                                                             date_time__month=dt.month, date_time__day=dt.day))

        # check whether user has app at that doc
        try:
            foo = Appointment.objects.get(doctor=doc, patient=patient, status='Upcoming')
            return JsonResponse({'message': 'You already have an upcoming appointment at this doctor.'}, status=400)
        except Appointment.DoesNotExist:
            pass

        print(category)
        cat = Category.objects.get(name=category)

        full_time = dt
        for i in range(cat.duration):
            if full_time.time() in [b.start for b in blocks] and full_time.time() not in app_hours:
                pass
            else:
                raise BadRequest('Invalid appointment. ')
            full_time += settings.WORKBLOCK_DURATION

        appointment = Appointment.objects.create(doctor=doc, date_time=dt, category=cat, patient=patient)

        return JsonResponse({'message': 'Appointment created successfully'}, status=200)

    elif request.method == 'PUT':
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        print('Data:', data)

        # Przykład dostępu do poszczególnych pól
        # field_value = data.get('field_name')

        # Przetwarzaj dane tutaj

        return JsonResponse({'message': 'Data received successfully.'})
