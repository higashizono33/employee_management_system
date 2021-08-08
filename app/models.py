from django.db import models
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models.deletion import CASCADE, DO_NOTHING
from datetime import date, timedelta 
import math

User = get_user_model()

class Validator(models.Manager):
    def report_validator(self, postData):
        errors = {}
        if len(postData['report']) < 15:
            errors["report"] = "Please enter at least 15 characters"
        if len(postData['challenge']) < 15:
            errors["challenge"] = "Please enter at least 15 characters"
        if len(postData['help']) < 15:
            errors["help"] = "Please enter at least 15 characters"
        return errors

class Employee(models.Model):
    user = models.ForeignKey(User, related_name='employees', on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'E-{self.user.first_name} {self.user.last_name}'

    def get_point(self):
        point = Point.get_total(Point, self.id)
        ex_point = ExtraPoint.get_total(ExtraPoint, self.id)
        without_report = ExtraPoint.objects.filter(employee=self).aggregate(models.Sum('ex_point'))
        if point['earned__sum'] is None and ex_point['ex_point__sum'] is None:
            my_point = 0
        elif point['earned__sum'] is None:
            my_point = ex_point['ex_point__sum']
        elif ex_point['ex_point__sum'] is None:
            my_point = point['earned__sum']
        else:
            my_point = point['earned__sum'] + ex_point['ex_point__sum']
        # to include extra point without assigned report
        if without_report['ex_point__sum']:
            my_point += without_report['ex_point__sum']

        return my_point
    
    def get_rate(self):
        myself = Employee.objects.get(id=self.id)
        rates = PointRate.objects.all().filter(employee=myself).order_by('-id')
        current_rate = 0
        for rate in rates:
            today = date.today()
            if rate.effective_date < today:
                current_rate = rate
                break
            else:
                # this is base rate
                current_rate = PointRate.objects.get(id=1)
        return current_rate
    
    def is_manager(self):
        managers = Manager.objects.all()
        for manager in managers:
            if manager.user == self.user:
                result = True
                break
            else:
                result = False
        return result
        
class Manager(models.Model):
    user = models.ForeignKey(User, related_name='managers', on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Manager-{self.user.first_name} {self.user.last_name}'

class TimeCard(models.Model):
    employee = models.ForeignKey(Employee, related_name='timecards', on_delete=CASCADE)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    task = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Card-ID#{self.employee.id}-{self.clock_in.strftime("%m.%d.%Y")}'
    
    def save(self, *args, **kwargs):
        if not self.clock_out:
            self.clock_out = None
        super(TimeCard, self).save(*args, **kwargs)
    
    def get_spent_time(self):
        if self.clock_out is not None:
            spent = (self.clock_out - self.clock_in).total_seconds()
            hours = math.floor(spent/3600)
            minutes = (spent % 3600)/60
            if minutes > 30:
                hours += 0.5
            return hours
        else:
            pass

    def get_point(self):
        return get_object_or_404(Point, timecard=self).earned

class Report(models.Model):
    created_by = models.ForeignKey(Employee, related_name='reports', on_delete=CASCADE)
    timecard = models.ForeignKey(TimeCard, related_name='reports', on_delete=CASCADE, null=True)
    report = models.TextField()
    challenge = models.TextField()
    help = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Validator()

    def __str__(self):
        return f'Report-ID#{self.created_by.id}-{self.timecard.clock_in.strftime("%m.%d.%Y")}'

class PointRate(models.Model):
    employee = models.ForeignKey(Employee, related_name='point_rates', on_delete=CASCADE, null=True)
    rate = models.DecimalField(max_digits=4, decimal_places=2)
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Rate#{self.id}'

    def get_current_rate(self):
        rates = PointRate.objects.all().order_by('-id')
        for rate in rates:
            today = date.today()
            if rate.effective_date < today:
                current_rate = rate
                break
            else:
                current_rate = PointRate.objects.get(id=1)
        return current_rate
    
    def get_yesterday_rate(self):
        rates = PointRate.objects.all().order_by('-id')
        for rate in rates:
            yesterday = date.today() - timedelta(days=1)
            if rate.effective_date < yesterday:
                yesterday_rate = rate
                break
            else:
                yesterday_rate = PointRate.objects.get(id=1)
        return yesterday_rate

class Point(models.Model):
    employee = models.ForeignKey(Employee, related_name='points', on_delete=CASCADE)
    timecard = models.ForeignKey(TimeCard, related_name='points', on_delete=CASCADE, null=True)
    rate = models.ForeignKey(PointRate, related_name='points', on_delete=DO_NOTHING, null=True)
    earned = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Point-ID#{self.employee.id}-{self.timecard.clock_in.strftime("%m.%d.%Y")}'
    
    def get_total(self, employee_id):
        employee = get_object_or_404(Employee, pk=employee_id)
        total = Point.objects.filter(employee=employee).aggregate(models.Sum('earned'))
        return total
    
    def get_grand_total(self):
        grand_total = Point.objects.all().aggregate(models.Sum('earned'))
        return grand_total

class ExtraPoint(models.Model):
    report = models.ForeignKey(Report, related_name='ex_points', on_delete=CASCADE, null=True)
    employee = models.ForeignKey(Employee, related_name='ex_points', on_delete=CASCADE, null=True)
    created_by = models.ForeignKey(Manager, related_name='give_points', on_delete=CASCADE)
    ex_point = models.DecimalField(max_digits=4, decimal_places=2)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'EX_Point-ID#{self.id}'

    def get_total(self, employee_id):
        employee = get_object_or_404(Employee, pk=employee_id)
        reports = Report.objects.filter(created_by=employee)
        # without_report = 0
        # if self.employee:
        #     without_report = ExtraPoint.objects.filter(employee=employee).aggregate(models.Sum('ex_point'))
        # print(without_report)
        total = ExtraPoint.objects.filter(report__in=reports).aggregate(models.Sum('ex_point'))
        # print(total)
        return total
    
    def get_grand_total(self):
        grand_total = ExtraPoint.objects.all().aggregate(models.Sum('ex_point'))
        return grand_total

class Quote(models.Model):
    created_by = models.ForeignKey(Manager, related_name='quotes', on_delete=CASCADE)
    quote = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Quote-ID#{self.id}'