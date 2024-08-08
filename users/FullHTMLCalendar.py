import calendar

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
        self.special_dates = special_dates

    def formatmonth(self, theyear, themonth, withyear=True):
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')

        weeks = self.get_full_weeks(theyear, themonth)
        for week in weeks:
            a(self.formatweek(week, theyear, themonth))
            a('\n')
        a('</table>')
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

    def formatweek(self, theweek, theyear, themonth, *args):
        """IF args are present, generate a header. First argument must be week number"""

        print("args:", args)
        s = ''.join(self.formatday(d, wd, theyear, themonth) for (d, wd) in theweek)

        if not args:
            return '<tr>%s</tr>' % s

        months = get_months(theyear, themonth)

        m_range = calendar.monthrange(theyear, themonth)

        week_num = args[0]

        week_num = int(week_num)  # Value error? Hopefully

        if theweek[0][0] < 8:
            previous = {'week': len(self.get_full_weeks(theyear, themonth)) - 1, 'month': months['prev_month'],
                        'year': months['prev_year']}
        else:
            previous = {'week': week_num - 1, 'month': themonth, 'year': theyear}

        if theweek[6][0] == m_range[1]:
            next = {'week': 0, 'month': months['next_month'], 'year': months['next_year']}
        elif theweek[0][0] > theweek[6][0]:
            next = {'week': 1, 'month': months['next_month'], 'year': months['next_year']}
        else:
            next = {'week': week_num + 1, 'month': themonth, 'year': theyear}

        return (f'<table><tr><th colspan="7" class="week-header">'
                f'<img class="calendar-nav-image" src="" '
                f'data-prev-month="{previous["month"]}" data-prev-year="{previous["year"]}" data-prev-week="{previous["week"]}">'  # nav button
                f'<div>Week {week_num + 1} of {calendar.month_name[themonth]}</div>'  # +1 for visual purposes
                f'<img class="calendar-nav-image" src="" '
                f'data-next-month="{next["month"]}" data-next-year="{next["year"]}" data-next-week="{next["week"]}">'  # nav button
                '</th></tr>'
                f'<tr>{s}</tr>'
                '</table>')


    def formatday(self, day, weekday, theyear, themonth):
        css_class = self.cssclasses[weekday]

        if day in self.special_dates['free']:
            css_class = 'cal-day disabled'

        elif day in self.special_dates['working']:
            css_class = 'cal-day active'

        return f'<td class="{css_class}">{day}</td>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        months = get_months(theyear, themonth)

        if withyear:
            s = '%s %s' % (calendar.month_name[themonth], theyear)
        else:
            s = '%s' % calendar.month_name[themonth]
        return (f'<tr><th colspan="7" class="{self.cssclass_month_head}">'
                f'<img class="calendar-nav-image" src="" '
                f'data-prev-month="{months["prev_month"]}" data-prev-year="{months["prev_year"]}">'  # nav button
                f'{s}'
                f'<img class="calendar-nav-image" src="" '
                f'data-next-month="{months["next_month"]}" data-next-year="{months["next_year"]}">'  # nav button
                '</th></tr>')
