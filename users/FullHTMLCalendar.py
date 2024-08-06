import calendar


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
        prev_month = (themonth - 1) if themonth > 1 else 12
        next_month = (themonth + 1) if themonth < 12 else 1
        prev_year = theyear if themonth > 1 else theyear - 1
        next_year = theyear if themonth < 12 else theyear + 1

        prev_month_days = cal.monthdays2calendar(prev_year, prev_month)
        next_month_days = cal.monthdays2calendar(next_year, next_month)

        # Ensure the first and last week are full
        for i in month_days[0]:
            if i[0] == 0:
                month_days[0][i[1]] = prev_month_days[-1][i[1]]
        for i in month_days[-1]:
            if i[0] == 0:
                month_days[-1][i[1]] = next_month_days[0][i[1]]

        return month_days

    def formatweek(self, theweek, theyear, themonth):
        s = ''.join(self.formatday(d, wd, theyear, themonth) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

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
        # duplicate :(
        prev_month = (themonth - 1) if themonth > 1 else 12
        next_month = (themonth + 1) if themonth < 12 else 1
        prev_year = theyear if themonth > 1 else theyear - 1
        next_year = theyear if themonth < 12 else theyear + 1

        if withyear:
            s = '%s %s' % (calendar.month_name[themonth], theyear)
        else:
            s = '%s' % calendar.month_name[themonth]
        return (f'<tr><th colspan="7" class="{self.cssclass_month_head}">'
                f'<img class="calendar-nav-image" src="" '
                f'data-prev-month="{prev_month}" data-prev-year="{prev_year}">'  # nav button
                f'{s}'
                f'<img class="calendar-nav-image" src="" '
                f'data-next-month="{next_month}" data-next-year="{next_year}">'  # nav button
                '</th></tr>')
