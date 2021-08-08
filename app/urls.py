from django.urls import path
from .views import *
from accounts.views import SignUpView

urlpatterns = [
    path('', SignUpView.as_view()),
    path('home', HomeView.as_view(), name='home'),
    path('clockin', clock_in, name='clock_in'),
    path('clockout', clock_out, name='clock_out'),
    path('clockout/yesterday', clock_out_yesterday, name='clock_out_yesterday'),
    path('report', ReportView.as_view(), name='report'),
    path('points', PointView.as_view(), name='points'),
    path('settings', settings, name='settings'),
    path('set_timezone', set_timezone, name='set_timezone'),
    path('admin_view', admin_view, name='admin_view'),
    path('user_view', user_view, name='user_view'),
    path('set_quote', set_quote, name='set_quote'),
    path('daily_updates', AdminReportView.as_view(), name='daily_updates'),
    path('add_point', add_point, name='add_point'),
    path('update_employee', update_employee, name='update_employee'),
]