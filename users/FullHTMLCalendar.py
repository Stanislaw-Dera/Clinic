import calendar


# with the HELP of AI :P
class FullHTMLCalendar(calendar.HTMLCalendar):
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
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)