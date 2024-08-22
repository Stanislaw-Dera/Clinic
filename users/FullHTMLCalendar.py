import calendar
from datetime import datetime, date


def get_months(theyear, themonth):
    return {
        'prev_month': (themonth - 1) if themonth > 1 else 12,
        'next_month': (themonth + 1) if themonth < 12 else 1,
        'prev_year': theyear if themonth > 1 else theyear - 1,
        'next_year': theyear if themonth < 12 else theyear + 1
    }

# with the HELP of AI :P
class FullHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, special_dates=None):
        super().__init__()
        self.today = date.today()
        self.special_dates = special_dates
        self.is_first_week = False  # very bad way to achieve previous and next month days disabled
        self.is_last_week = False

    def formatmonth(self, theyear, themonth, withyear=True):
        v = []
        a = v.append
        a('<div class="calendar">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')

        weeks = self.get_full_weeks(theyear, themonth)
        self.is_first_week = True
        self.is_last_week = False
        i = 1
        for week in weeks:
            if i == self.get_total_weeks(theyear, themonth):
                self.is_last_week = True
            a(self.formatweek(week, theyear, themonth))
            a('\n')
            self.is_first_week = False
            i += 1
        a('</div>')
        a('\n')
        return ''.join(v)

    def get_full_weeks(self, theyear, themonth):
        cal = calendar.Calendar(firstweekday=self.firstweekday)
        month_days = cal.monthdays2calendar(theyear, themonth)

        # Add the last days of the previous month and the first days of the next month
        months = get_months(theyear, themonth)

        prev_month_days = cal.monthdays2calendar(months["prev_year"], months["prev_month"])
        next_month_days = cal.monthdays2calendar(months["next_year"], months["next_month"])

        # Ensure the first and last week are full
        for i in month_days[0]:
            if i[0] == 0:
                month_days[0][i[1]] = prev_month_days[-1][i[1]]
        for i in month_days[-1]:
            if i[0] == 0:
                month_days[-1][i[1]] = next_month_days[0][i[1]]

        return month_days

    def get_total_weeks(self, theyear, themonth):
        """Returns the total number of full weeks in the month including partial weeks."""
        full_weeks = self.get_full_weeks(theyear, themonth)
        return len(full_weeks)

    def formatweek(self, theweek, theyear, themonth, *args):
        """IF args are present, generate a header. First argument must be week number"""

        if args:
            if args[0] == 0:
                self.is_first_week = True
            elif args[0] == self.get_total_weeks(theyear, themonth) - 1:
                self.is_last_week = True

        print("formatweek args:", args)
        # s = ''.join(self.formatday(d, wd, theyear, themonth) for (d, wd) in theweek)
        s: str = ''
        for d, wd in theweek:
            if d > theweek[6][0] and self.is_first_week:
                s += self.formatday(d, wd, theyear, themonth-1)
            elif d < theweek[0][0] and self.is_last_week:
                s += self.formatday(d, wd, theyear, themonth + 1)
            else:
                s += self.formatday(d, wd, theyear, themonth)

        if not args:
            self.is_first_week = False
            self.is_last_week = False # fix last / first week
            return '<div class="week">%s</div>' % s

        months = get_months(theyear, themonth)

        m_range = calendar.monthrange(theyear, themonth)

        week_num = int(args[0])  # Value error? Hopefully

        if theweek[0][0] < 8:
            previous = {'week': self.get_total_weeks(months['prev_year'], months['prev_month'])-1,
                        'month': months['prev_month'], 'year': months['prev_year']}
        else:
            previous = {'week': week_num - 1, 'month': themonth, 'year': theyear}

        if theweek[6][0] == m_range[1]:
            next = {'week': 0, 'month': months['next_month'], 'year': months['next_year']}
        elif theweek[0][0] > theweek[6][0]:
            next = {'week': 1, 'month': months['next_month'], 'year': months['next_year']}
        else:
            next = {'week': week_num + 1, 'month': themonth, 'year': theyear}

        return ('<div class="calendar">'
                '<div class="calendar-header">'
                f'<img class="calendar-nav-image" src="/static/functional/calendar/polygon-left.svg" '
                f'data-month="{previous["month"]}" data-year="{previous["year"]}" data-week="{previous["week"]}">'  # nav button
                f'<div>Week {week_num + 1} of {calendar.month_name[themonth]}</div>'  # +1 for visual purposes
                f'<img class="calendar-nav-image" src="/static/functional/calendar/polygon-right.svg" '
                f'data-month="{next["month"]}" data-year="{next["year"]}" data-week="{next["week"]}">'  # nav button
                '</div>'
                f'<div class="week">{s}</div>'
                f'</div>')

    def formatday(self, day, weekday, theyear, themonth):
        css_class = self.cssclasses[weekday]

        if day in self.special_dates['free']: # bug - prev/next month
            css_class = 'cal-day disabled'

        elif day in self.special_dates['working']:
            css_class = 'cal-day active'

        if date(theyear, themonth, day) < self.today:
            css_class = 'cal-day disabled'

        return f'<div class="{css_class}" data-day="{day}" data-month="{themonth}" data-year="{theyear}">{day}</div>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        months = get_months(theyear, themonth)

        if withyear:
            s = '%s %s' % (calendar.month_name[themonth], theyear)
        else:
            s = '%s' % calendar.month_name[themonth]
        return (f'<div class="calendar-header">'
                f'<img class="calendar-nav-image" src="/static/functional/calendar/polygon-left.svg" '
                f'data-month="{months["prev_month"]}" data-year="{months["prev_year"]}">'  # nav button
                f'<div>{s}</div>'
                f'<img class="calendar-nav-image" src="/static/functional/calendar/polygon-right.svg" '
                f'data-month="{months["next_month"]}" data-year="{months["next_year"]}">'  # nav button
                '</div>')
