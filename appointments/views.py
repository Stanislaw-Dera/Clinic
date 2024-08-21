from datetime import date, datetime, time

from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from appointments.models import Appointment, Category
from appointments.utils import get_app_hours
from users.models import WorkDay, Doctor, User

from clinic import settings


# Create your views here.


@login_required(redirect_field_name=None)  # only for patients?
def patient_history(request):
    if request.user.role != 'p':
        raise BadRequest('Only Patients can access this page. ')

    appointments = Appointment.objects.filter(patient=request.user)

    if appointments is None:
        return HttpResponse("You haven't scheduled nor completed any appointments yet. ")

    date_filter = request.GET.get('date')
    status_filter = request.GET.get('status')
    print(date_filter, '|', status_filter)

    if not status_filter or status_filter not in ['upcoming', 'cancelled', 'finished', 'all']:
        raise BadRequest('Invalid status filter. Available options are: upcoming, cancelled, finished, all')
    else:
        if status_filter != 'all':
            appointments = appointments.filter(status=status_filter.capitalize())

    if not date_filter or date_filter not in ['asc', 'desc']:
        raise BadRequest('Invalid date filter. Available options are: asc, desc')
    else:
        appointments = appointments.order_by('-date_time' if date_filter == "desc" else 'date_time')

    print(appointments)
    return JsonResponse([appointment.serialize() for appointment in appointments], safe=False)


#doc history for one day

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

    dt = dt.replace(hour=11, minute=23)

    closure = dt.replace(hour=settings.CLINIC_CLOSURE.hour, minute=settings.CLINIC_CLOSURE.minute)

    doc = User.objects.get(id=doc_id)
    blocks = WorkDay.filters.filter_by_doc_and_date(doc=doc, date=dt.date()).workblocks.filter(start__range=(dt.time(), closure.time()))

    appointments = Appointment.objects.filter(doctor=doc, date_time=dt)

    app_hours = get_app_hours(appointments)

    available_hours = [block.start for block in blocks if block.start not in app_hours]

    categories = []
    if request.user.role == 'p':
        categories = Category.objects.for_patient()

    elif request.user.role == 'd':
        categories = Category.objects.for_doctor()

    return JsonResponse({'bookingHours': available_hours, 'categories': [c.name for c in categories], 'date': dt.date()}, safe=False, status=200)

def manage_appointment(request, doc_id):
    pass
    # POST, PUT, DELETE appointments
    # one at the time at one doctor.
