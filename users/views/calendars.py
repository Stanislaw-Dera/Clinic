# calendars api
from datetime import timedelta, datetime, date, time

from django.core.exceptions import BadRequest
from django.http import HttpResponse, JsonResponse

from appointments.models import Appointment
from users.FullHTMLCalendar import FullHTMLCalendar
from users.models import WorkDay, Doctor, User, WorkBlock

CLINIC_OPENING = datetime.combine(date.today(), time(7, 0))
CLINIC_CLOSURE = datetime.combine(date.today(), time(21, 0))
WORKBLOCK_DURATION = timedelta(minutes=30)


def doctor_calendar(request):
    doc_id = request.GET.get('doc-id')  # obligatory
    month = request.GET.get('month')  # obligatory
    year = request.GET.get('year')  # obligatory
    week = request.GET.get('week')  # optional
    # validation
    try:
        user = User.doctors.get(pk=doc_id)
        doc = Doctor.objects.get(user=user)
    except (User.DoesNotExist, Doctor.DoesNotExist):
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
        except IndexError:
            return JsonResponse({'error': 'Invalid week'}, status=400)

        return JsonResponse({'week': calendar.formatweek(wk, year, month, week)}, status=200)

    return JsonResponse({'month': calendar.formatmonth(year, month)}, status=200)
# teraz pobierz dane na profilu doktora, napisz view do odczytywania workdayów (asynchronicznie)
# i umieść te dane w ładny sposoób :)


def get_workhours(request):
    doc_id = request.GET.get('doc-id')
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')

    try:
        user = User.doctors.get(pk=doc_id)
        doc = Doctor.objects.get(user=user)
    except (User.DoesNotExist, Doctor.DoesNotExist):
        raise BadRequest("Doctor does not exist")

    if month is None or year is None or day is None or not month.isdigit() or not year.isdigit() or not day.isdigit():
        raise BadRequest("Month, year or day are not valid")

    print("get_workhours args: ", doc_id, year, month, day)

    month = int(month)
    year = int(year)
    day = int(day)

    wday_date = date(year, month, day)

    # getting working hours
    try:
        w_day = WorkDay.objects.get(doctor=doc, date=wday_date)
    except WorkDay.DoesNotExist:
        try:
            w_day = WorkDay.objects.get(doctor=doc, day=wday_date.weekday())
        except WorkDay.DoesNotExist:  # in case routine day does not exist (which means it's empty!)
            opening = CLINIC_OPENING
            # convert to json
            hours = {}

            while opening < CLINIC_CLOSURE:
                t = time(opening.hour, opening.minute)

                status = "free"

                hours.update({opening.strftime("%H:%M"): {"status": status}})

                opening = opening + WORKBLOCK_DURATION

            return JsonResponse({'hours': hours}, status=200)

    print("workday:", w_day)
    print("work blocks:", w_day.workblocks.all())

    working_hours = []

    for block in w_day.workblocks.all().values("start"):
        working_hours.append(block["start"])

    print("hours:", working_hours)

    # getting visits hours (not changeable)

    today_appointments = Appointment.objects.filter(doctor=user, date_time__year=year, date_time__month=month,
                                                    date_time__day=day)
    print("today appointments:", today_appointments)

    app_hours = []

    for appointment in today_appointments:
        for i in range(appointment.category.duration):
            app_hours.append(time(appointment.date_time.hour, appointment.date_time.minute))
            appointment.date_time += WORKBLOCK_DURATION

    opening = CLINIC_OPENING

    # convert to json

    hours = {}

    while opening < CLINIC_CLOSURE:
        t = time(opening.hour, opening.minute)

        # print("time: ", opening.hour, opening.minute, "| working" if t in working_hours else "", "| visit"
        #       if t in app_hours else "")

        if t in app_hours:
            status = "appointment"
        elif t in working_hours:
            status = "working"
        else:
            status = "free"

        hours.update({opening.strftime("%H:%M"): {"status": status}})

        opening = opening + WORKBLOCK_DURATION

    return JsonResponse({'hours': hours}, status=200)

