# calendars api
from datetime import timedelta, datetime, date, time, timezone

from django.core.exceptions import BadRequest
from django.http import HttpResponse, JsonResponse

import appointments.utils
from appointments.models import Appointment
from users.FullHTMLCalendar import FullHTMLCalendar
from users.models import WorkDay, Doctor, User, WorkBlock

from clinic.settings import CLINIC_CLOSURE, CLINIC_OPENING, WORKBLOCK_DURATION
from users.utils import is_hour_valid


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

    default_workdays = WorkDay.objects.filter(doctor=user, date=None)

    workdays_numeric_list = []

    for workday in default_workdays:
        workdays_numeric_list.append(workday.day)

    custom_workdays = WorkDay.objects.filter(date__month=month, date__year=year, doctor=user)
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

    now = datetime.now()

    if wday_date < now.date():
        return JsonResponse({'message': "You can't change past days"}, status=206)

    # getting working hours
    try:
        w_day = WorkDay.objects.get(doctor=user, date=wday_date)
    except WorkDay.DoesNotExist:
        try:
            w_day = WorkDay.objects.get(doctor=user, day=wday_date.weekday())
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

    # getting visits hours (not changeable)

    today_appointments = Appointment.objects.filter(doctor=user, date_time__year=year, date_time__month=month,
                                                    date_time__day=day)
    print("today appointments:", today_appointments)

    app_hours = appointments.utils.get_app_hours(today_appointments)

    opening = CLINIC_OPENING

    # convert to json

    hours = {}

    while opening < CLINIC_CLOSURE:
        dt = datetime(year, month, day, opening.hour, opening.minute, tzinfo=timezone.utc)
        t = dt.time()

        # print("time: ", opening.hour, opening.minute, "| working" if t in working_hours else "", "| visit"
        #       if t in app_hours else "")

        if dt < datetime.now(timezone.utc):
            status = 'outdated'
        elif t in app_hours:
            status = "appointment"
        elif t in working_hours:
            status = "working"
        else:
            status = "free"

        hours.update({opening.strftime("%H:%M"): {"status": status}})

        opening = opening + WORKBLOCK_DURATION

    return JsonResponse({'hours': hours}, status=200)


def change_workblock(request):
    if request.method == 'POST':
        doc_id = request.POST.get('doc-id')
        block_date = request.POST.get('date')

        try:
            user = User.doctors.get(pk=doc_id)
        except User.DoesNotExist:
            raise BadRequest("Doctor does not exist")

        block_date = datetime.strptime(block_date, '%Y %m %d %H:%M')

        if not is_hour_valid(block_date):
            raise BadRequest("Invalid hour. ")

        try:
            appointments = Appointment.doc_appointments.filter_by_doc(user).filter(date_time__year=block_date.year,
                                                                                   date_time__month=block_date.month,
                                                                                   date_time__day=block_date.day)

            print(appointments)
            app_hours = [appointment.date_time.hour for appointment in appointments]
            if block_date.hour in app_hours:
                raise BadRequest(f"There is an appointment on {block_date}")

        except Appointment.DoesNotExist:
            pass

        try:
            day = WorkDay.objects.get(date=block_date.date(), doctor=user)
        except WorkDay.DoesNotExist:
            day = WorkDay.objects.create(doctor=user, date=block_date)
            try:
                blocks = WorkDay.objects.get(doctor=user, day=block_date.weekday()).workblocks.all()
            except WorkDay.DoesNotExist:
                blocks = WorkBlock.objects.none()

            for block in blocks:
                block.pk = None
                block.work_day = day
                block.save()

        work_hours = [block.start for block in day.workblocks.all()]

        if block_date.time() in work_hours:
            day.workblocks.get(start=block_date.time()).delete()
            return JsonResponse({"block_status": "free"}, status=200)
        else:
            day.workblocks.create(start=block_date.time())
            return JsonResponse({"block_status": "working"}, status=200)
