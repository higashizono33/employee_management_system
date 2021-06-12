import django_filters
from django_filters import DateRangeFilter, DateFilter, CharFilter
from .models import TimeCard, Report, Point
from django import forms
from datetime import datetime, timedelta, date
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

def _truncate(dt):
    return dt.date()

week_start = date.today()
week_start -= timedelta(days=week_start.weekday())
week_end = week_start + timedelta(days=7)

class TimeCardFilter(django_filters.FilterSet):
    choices = [
            ('this_week', _('This Week')),
            ('last_week', _('Last Week')),
            ('this_month', _('This Month')),
            ('last_month', _('Last Month'))
        ]
    
    filters = {
        'this_week': lambda qs, name: qs.filter(**{
            '%s__gte' % name: week_start,
            '%s__lt' % name: week_end
        }),
        'last_week': lambda qs, name: qs.filter(**{
            '%s__gte' % name: week_start - timedelta(days=7),
            '%s__lt' % name: week_end - timedelta(days=7)
        }),
        'this_month': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__month' % name: now().month
        }),
        'last_month': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__month' % name: now().month - 1
        })
    }

    date_range = DateRangeFilter(field_name='clock_in', choices=choices, filters=filters)
    start_date = DateFilter(label='Start date', field_name='clock_in', lookup_expr=('gt'), widget=forms.TextInput(attrs={'type': 'date'})) 
    end_date = DateFilter(label='End date', field_name='clock_in', lookup_expr=('lt'), widget=forms.TextInput(attrs={'type': 'date'}))
    
    class Meta:
        model = TimeCard
        fields = ['employee', 'date_range', 'start_date', 'end_date']

class ReportFilter(django_filters.FilterSet):
    choices = [
            ('this_week', _('This Week')),
            ('last_week', _('Last Week')),
            ('this_month', _('This Month')),
            ('last_month', _('Last Month'))
        ]
    
    filters = {
        'this_week': lambda qs, name: qs.filter(**{
            '%s__gte' % name: week_start,
            '%s__lt' % name: week_end
        }),
        'last_week': lambda qs, name: qs.filter(**{
            '%s__gte' % name: week_start - timedelta(days=7),
            '%s__lt' % name: week_end - timedelta(days=7)
        }),
        'this_month': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__month' % name: now().month
        }),
        'last_month': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__month' % name: now().month - 1
        })
    }

    date_range = DateRangeFilter(field_name='created_at', choices=choices, filters=filters)
    start_date = DateFilter(label='Start date', field_name='created_at', lookup_expr=('gt'), widget=forms.TextInput(attrs={'type': 'date'})) 
    end_date = DateFilter(label='End date', field_name='created_at', lookup_expr=('lt'), widget=forms.TextInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Report
        fields = ['created_by', 'date_range', 'start_date', 'end_date']

class PointFilter(django_filters.FilterSet):
    choices = [
            ('this_week', _('This Week')),
            ('last_week', _('Last Week')),
            ('this_month', _('This Month')),
            ('last_month', _('Last Month'))
        ]
    
    filters = {
        'this_week': lambda qs, name: qs.filter(**{
            '%s__gte' % name: week_start,
            '%s__lt' % name: week_end
        }),
        'last_week': lambda qs, name: qs.filter(**{
            '%s__gte' % name: week_start - timedelta(days=7),
            '%s__lt' % name: week_end - timedelta(days=7)
        }),
        'this_month': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__month' % name: now().month
        }),
        'last_month': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__month' % name: now().month - 1
        })
    }

    date_range = DateRangeFilter(field_name='timecard__clock_in', choices=choices, filters=filters)
    start_date = DateFilter(label='Start date', field_name='timecard__clock_in', lookup_expr=('gt'), widget=forms.TextInput(attrs={'type': 'date'})) 
    end_date = DateFilter(label='End date', field_name='timecard__clock_in', lookup_expr=('lt'), widget=forms.TextInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Point
        fields = ['employee', 'date_range', 'start_date', 'end_date']
