from app.models import TimeCard
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView
from .models import Employee, Manager, Point, PointRate, Report, TimeCard, ExtraPoint, Quote
from django.contrib import messages
from datetime import datetime, timedelta, date
from django.utils import timezone
from decimal import Context, Decimal
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import PasswordResetForm, ProfileUpdateForm
import pytz
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from .filters import PointFilter, TimeCardFilter, ReportFilter
from django.template.loader import render_to_string

class HomeView(LoginRequiredMixin, FilterView):
    template_name = 'home.html'
    model = TimeCard
    context_object_name = 'cards'
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    filterset_class = TimeCardFilter
    paginate_by = 10

    def get_queryset(self):
        queryset = super(HomeView, self).get_queryset()
        queryset = TimeCard.objects.all().order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(Employee, user=self.request.user)
        if len(Manager.objects.filter(user=self.request.user)) >= 1:
            context['is_manager'] = True
        else:
            context['is_manager'] = False
        point = Point.get_total(Point, employee.id)
        ex_point = ExtraPoint.get_total(ExtraPoint, employee.id)

        if point['earned__sum'] is None and ex_point['ex_point__sum'] is None:
            context['my_point'] = 0
        elif point['earned__sum'] is None:
            context['my_point'] = ex_point['ex_point__sum']
        elif ex_point['ex_point__sum'] is None:
            context['my_point'] = point['earned__sum']
        else:
            context['my_point'] = point['earned__sum'] + ex_point['ex_point__sum']
        
        context['village_point'] = Point.get_grand_total(Point)['earned__sum'] + ExtraPoint.get_grand_total(ExtraPoint)['ex_point__sum']
        
        cards = TimeCard.objects.filter(employee=employee).order_by('-id')
        if len(cards) >= 1:
            if cards.first().clock_out is None and cards.first().clock_in.date() == datetime.today().date():
                self.request.session['clocked_in'] = True
                self.request.session['card_id'] = cards.first().id
            
        yesterday = datetime.strptime(str(date.today()-timedelta(days=1)),"%Y-%m-%d")
        context['yesterday'] = yesterday
        work_start = yesterday.replace(hour=9, minute=00)
        date_list = [work_start + timedelta(minutes=30*x) for x in range(0, 30)]
        datetext=[x.strftime('%B %d, %Y - %I:%M%p') for x in date_list]
        context['times'] = datetext
        context['employees'] = Employee.objects.all()
        context['current_rate'] = PointRate.get_current_rate(PointRate)
        context['quote'] = Quote.objects.last()
        context['form'] = ProfileUpdateForm()
        # whether he was clocked in yesterday or not
        yesterday_card = TimeCard.objects.filter(employee=employee).filter(clock_in__date=yesterday)
        if yesterday_card:
            context['clockedIn_yesterday'] = True
        return context

def clock_in(request):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, user=request.user)
        new_card = TimeCard.objects.create(
            employee = employee,
            clock_in = timezone.now(),
            clock_out = None,
            task = None,
        )
        request.session['clocked_in'] = True
        request.session['card_id'] = new_card.id
    return redirect('home')

def clock_out(request):
    if request.method == 'POST':
        card = get_object_or_404(TimeCard, pk=request.session['card_id'])
        if len(request.POST['task']) < 15:
            messages.error(request, "Please enter at least 15 charactors for today's task")
        elif card.clock_in.date() != datetime.today().date():
            print(card.clock_in.date())
            print(datetime.today().date())
            messages.error(request, "You can't clock out for the past. Go link in below")
        else:        
            card.clock_out = timezone.now()
            card.task = request.POST['task']
            card.save()
            request.session['clocked_in'] = False
            del request.session['card_id']
            current_rate = PointRate.get_current_rate(PointRate)
            Point.objects.create(
                employee = get_object_or_404(Employee, user=request.user),
                timecard = card,
                rate = current_rate,
                earned = Decimal(card.get_spent_time()) * current_rate.rate,
            )
    return redirect('home')

def clock_out_yesterday(request):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, user=request.user)
        queryset_yesterday = TimeCard.objects.filter(employee=employee).filter(clock_in__date=date.today()-timedelta(days=1))
        card_id = queryset_yesterday[0].id
        card_yesterday = get_object_or_404(TimeCard, pk=card_id)
        if len(request.POST['task']) < 15:
            messages.error(request, "Please enter at least 15 charactors for today's task")
        elif card_yesterday.clock_out is not None:
            messages.error(request, "You did clock out yesterday, No Worries")
        else:
            clock_out_unaware = datetime.strptime(request.POST['clock_out'], '%B %d, %Y - %I:%M%p')
            clock_out_aware = timezone.make_aware(clock_out_unaware, timezone.get_current_timezone())
            card_yesterday.clock_out = clock_out_aware
            card_yesterday.task = request.POST['task']
            card_yesterday.save()
            yesterday_rate = PointRate.get_yesterday_rate(PointRate)
            Point.objects.create(
                employee = get_object_or_404(Employee, user=request.user),
                timecard = card_yesterday,
                rate = yesterday_rate,
                earned = Decimal(card_yesterday.get_spent_time()) * yesterday_rate.rate,
            )
    return redirect('home')

class PointView(FilterView):
    template_name = 'points.html'
    model = Point
    context_object_name = 'points'
    filterset_class = PointFilter
    paginate_by = 10

    def get_queryset(self):
        queryset = super(PointView, self).get_queryset()
        queryset = Point.objects.all().order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(Manager.objects.filter(user=self.request.user)) >= 1:
            context['is_manager'] = True
        else:
            context['is_manager'] = False
        point = Point.get_total(Point, get_object_or_404(Employee, user=self.request.user).id)
        ex_point = ExtraPoint.get_total(ExtraPoint, get_object_or_404(Employee, user=self.request.user).id)

        if point['earned__sum'] is None and ex_point['ex_point__sum'] is None:
            context['my_point'] = 0
        elif point['earned__sum'] is None:
            context['my_point'] = ex_point['ex_point__sum']
        elif ex_point['ex_point__sum'] is None:
            context['my_point'] = point['earned__sum']
        else:
            context['my_point'] = point['earned__sum'] + ex_point['ex_point__sum']
        context['village_point'] = Point.get_grand_total(Point)['earned__sum'] + ExtraPoint.get_grand_total(ExtraPoint)['ex_point__sum']
        context['quote'] = Quote.objects.last()
        return context

class ReportView(TemplateView):
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(Manager.objects.filter(user=self.request.user)) >= 1:
            context['is_manager'] = True
        else:
            context['is_manager'] = False
        point = Point.get_total(Point, get_object_or_404(Employee, user=self.request.user).id)
        ex_point = ExtraPoint.get_total(ExtraPoint, get_object_or_404(Employee, user=self.request.user).id)
        
        if point['earned__sum'] is None and ex_point['ex_point__sum'] is None:
            context['my_point'] = 0
        elif point['earned__sum'] is None:
            context['my_point'] = ex_point['ex_point__sum']
        elif ex_point['ex_point__sum'] is None:
            context['my_point'] = point['earned__sum']
        else:
            context['my_point'] = point['earned__sum'] + ex_point['ex_point__sum']
        context['village_point'] = Point.get_grand_total(Point)['earned__sum'] + ExtraPoint.get_grand_total(ExtraPoint)['ex_point__sum']
        context['quote'] = Quote.objects.last()
        return context
    
    def post(self, request):
        errors = Report.objects.report_validator(request.POST)
        if not errors:
            employee = get_object_or_404(Employee, user=request.user)
            card = TimeCard.objects.filter(employee=employee).filter(clock_in__date=date.today())
            if len(card) == 0:
                # yesterday's card
                card = TimeCard.objects.filter(employee=employee).filter(clock_in__date=date.today()-timedelta(days=1))
            existing = Report.objects.filter(timecard=card[0])
            if existing:
                existing[0].report = self.request.POST['report']
                existing[0].challenge = self.request.POST['challenge']
                existing[0].help = self.request.POST['help']
                existing[0].save()
            else:
                Report.objects.create(
                    created_by = employee,
                    timecard = card[0],
                    report = self.request.POST['report'],
                    challenge = self.request.POST['challenge'],
                    help = self.request.POST['help'],
                )
            return redirect('report')
        else:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return redirect('report')

def settings(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.user, request.POST)
        context = {
            'timezones': pytz.common_timezones,
            'form': form
        }
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('settings')        
    else:
        form = PasswordResetForm(request.user)
        if len(Manager.objects.filter(user=request.user)) >= 1:
            is_manager = True
        else:
            is_manager = False
        context = {
            'timezones': pytz.common_timezones,
            'form': form,
            'is_manager': is_manager,
        }
    return render(request, 'settings.html', context)

def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('settings')
    else:
        form = PasswordResetForm(request.user)
        context = {
            'timezones': pytz.common_timezones,
            'form': form
        }
    return render(request, 'template.html', context)

def admin_view(request):
    if len(Manager.objects.filter(user=request.user)) >= 1:
        request.session['admin_view'] = True
        return redirect('home')

def user_view(request):
    if len(Manager.objects.filter(user=request.user)) >= 1:
        del request.session['admin_view']
        return redirect('home')

def set_quote(request):
    if request.method == 'POST':
        manager = Manager.objects.filter(user=request.user)
        print(manager)
        Quote.objects.create(
            created_by = manager[0],
            quote = request.POST['quote']
        )
        return redirect('home')

class AdminReportView(LoginRequiredMixin, FilterView):
    template_name = 'daily_updates.html'
    model = Report
    context_object_name = 'reports'
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    filterset_class = ReportFilter

    def get_queryset(self):
        queryset = super(AdminReportView, self).get_queryset()
        queryset = Report.objects.all().order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(Employee, user=self.request.user)
        if len(Manager.objects.filter(user=self.request.user)) >= 1:
            context['is_manager'] = True
        else:
            context['is_manager'] = False
        point = Point.get_total(Point, employee.id)
        ex_point = ExtraPoint.get_total(ExtraPoint, employee.id)

        if point['earned__sum'] is None and ex_point['ex_point__sum'] is None:
            context['my_point'] = 0
        elif point['earned__sum'] is None:
            context['my_point'] = ex_point['ex_point__sum']
        elif ex_point['ex_point__sum'] is None:
            context['my_point'] = point['earned__sum']
        else:
            context['my_point'] = point['earned__sum'] + ex_point['ex_point__sum']
        
        context['village_point'] = Point.get_grand_total(Point)['earned__sum'] + ExtraPoint.get_grand_total(ExtraPoint)['ex_point__sum']
        
        cards = TimeCard.objects.filter(employee=Employee.objects.get(user=self.request.user)).order_by('-id')
        if len(cards) >= 1:
            if cards.first().clock_out is None and cards.first().clock_in.date() == datetime.today().date():
                self.request.session['clocked_in'] = True
                self.request.session['card_id'] = cards.first().id
            
        yesterday = datetime.strptime(str(date.today()-timedelta(days=1)),"%Y-%m-%d")
        work_start = yesterday.replace(hour=9, minute=00)
        date_list = [work_start + timedelta(minutes=30*x) for x in range(0, 30)]
        datetext=[x.strftime('%B %d, %Y - %I:%M%p') for x in date_list]
        context['times'] = datetext
        context['employees'] = Employee.objects.all()
        context['current_rate'] = PointRate.get_current_rate(PointRate)
        context['quote'] = Quote.objects.last()
        return context

def add_point(request):
    if request.method == 'POST':
        manager = Manager.objects.filter(user=request.user)
        if 'employee_id' in request.POST :
            # employee = Employee.objects.filter(id=request.POST['employee_id'])
            employee = get_object_or_404(Employee, pk=request.POST['employee_id'])
        else:
            employee = None
        try:
            report = get_object_or_404(Report, pk=request.POST['report_id'])
        except:
            report = None
        ExtraPoint.objects.create(
            report = report,
            created_by = manager[0],
            employee = employee,
            ex_point = request.POST['ex_point'],
            reason = request.POST['reason'],
        )
        if employee:
            return redirect('home')
        else:
            return redirect('daily_updates')

def update_employee(request):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, pk=request.POST['employee_id'])
        form = ProfileUpdateForm(request.POST or None, instance=employee.user)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.date_joined = request.POST['date_joined']
            form.save()
            if request.POST['role']=='admin' and len(Manager.objects.filter(user=employee.user)) <= 1:
                Manager.objects.create(
                    user = employee.user
                )
            if request.POST['role']=='user' and len(Manager.objects.filter(user=employee.user)) >= 1:
                manager = Manager.objects.get(user=employee.user)
                manager.delete()

            PointRate.objects.create(
                employee=employee,
                rate=request.POST['rate'],
                effective_date=request.POST['effective_date'],
            )

            context = {
                'employees': Employee.objects.all(),
                'form': ProfileUpdateForm(),
            }
            table = render_to_string('partial/table.html', context, request=request)
            return JsonResponse({'success': table})
        else:
            return JsonResponse({'errors': form.errors})
