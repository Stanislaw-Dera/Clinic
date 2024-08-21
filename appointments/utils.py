from datetime import time

from django.db.models import QuerySet

from clinic import settings


def get_app_hours(appointments: QuerySet) -> list[time]:
    app_hours = []

    for appointment in appointments:
        for i in range(appointment.category.duration):
            app_hours.append(time(appointment.date_time.hour, appointment.date_time.minute))
            appointment.date_time += settings.WORKBLOCK_DURATION

    return app_hours