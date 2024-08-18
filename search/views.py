from django.core.exceptions import BadRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from users.models import User, Doctor


# Create your views here.

def search(request):
    if request.method == 'POST':
        specialization = request.POST.get('specialization')  # obligatory
        name = request.POST.get('name')
        filters = request.POST.get('filters')

        doctors = Doctor.objects.all()

        if name:
            doctors = doctors.filter(user__name__icontains=name) | doctors.filter(user__surname__icontains=name)

        if specialization:
            doctors = doctors.filter(specializations__icontains=specialization)

        if filters == 'reviews':
            pass # order_by when reviews implemented
        elif filters == 'experience':
            pass # order_by when implemented
        # by default by reviews

        return JsonResponse([doctor.short_serialize() for doctor in doctors], safe=False, status=200)

    specializations = [spec[0] for spec in Doctor.SPECIALIZATIONS]
    return render(request, "search/find-specialists.html", {
        'specializations': specializations
    })
