# calendars api
from django.http import HttpResponse, JsonResponse

from users.FullHTMLCalendar import FullHTMLCalendar
from users.models import WorkDay, Doctor, User


def doctor_calendar(request):
    doc_id = request.GET.get('doc-id')  # obligatory
    month = request.GET.get('month')  # obligatory
    year = request.GET.get('year')  # obligatory
    week = request.GET.get('week')  # optional
    # validation
    try:
        user = User.doctors.get(pk=doc_id)
        doc = Doctor.objects.get(user=user)
    except Exception:
        return JsonResponse({'error': "doctor wasn't found"}, status=400)

    if not month.isdigit() or not year.isdigit():
        return JsonResponse({'error': "Month and year were not valid"}, status=400)

    month = int(month)
    year = int(year)

    # logic

    default_workdays = WorkDay.objects.filter(doctor=doc, date=None)

    workdays_numeric_list = []

    for workday in default_workdays:
        workdays_numeric_list.append(workday.day)

    custom_workdays = WorkDay.objects.filter(date__month=month, date__year=year, doctor=doc)
    custom_days_data = {"free": [], "working": []}

    for workday in custom_workdays:
        custom_days_data["free"].append(workday.date.day) if workday.workblocks.all().count() == 0 \
            else custom_days_data["working"].append(workday.date.day)

    print(custom_days_data)
    calendar = FullHTMLCalendar(custom_days_data)

    for i in range(7):
        calendar.cssclasses[i] = 'cal-day active' if i in workdays_numeric_list else 'cal-day disabled'

    if week and week.isdigit():
        try:
            wk = calendar.get_full_weeks(year, month)[int(week)]
            print('week', wk)
        except IndexError:
            return JsonResponse({'error': 'Invalid week'}, status=400)

        return JsonResponse({'week': calendar.formatweek(wk, year, month), 'data': {
            'weekNo': week, 'month': month, 'year': year
        }}, status=200)

    return JsonResponse({'month': calendar.formatmonth(year, month), 'data': {'month': month, 'year': year}}, status=200)
