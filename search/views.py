from django.core.exceptions import BadRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from users.models import User, Doctor


# Create your views here.

def search(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        specialization = request.POST.get('specialization')
        filters = request.POST.get('filters')

        doctors = Doctor.objects.all()

        if name:
            doctors = doctors(name__icontains=name)

        if specialization:
            doctors = doctors.filter(specializations__icontains=specialization)

        if filters == 'reviews':
            pass # order_by when reviews implemented
        elif filters == 'experience':
            pass # order_by when implemented
        # else:
        #     raise BadRequest('Invalid filter. ')

        return JsonResponse([doctor.short_serialize() for doctor in doctors], safe=False)

    return HttpResponse("foo")
