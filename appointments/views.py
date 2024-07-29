from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from appointments.models import Appointment


# Create your views here.


@login_required(redirect_field_name=None)  # only for patients?
def patient_history(request):
    if request.user.role != 'p':
        raise BadRequest('Only Patients can access this page. ')

    appointments = Appointment.objects.filter(patient=request.user)

    if appointments is None:
        return HttpResponse("You haven't scheduled of completed any appointments yet. ")

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


