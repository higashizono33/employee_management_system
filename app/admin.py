from django.contrib import admin
from .models import Employee, Manager, TimeCard, Report, Point, ExtraPoint, PointRate, Quote

class EmployeeAdmin(admin.ModelAdmin):
    pass
class ManagerAdmin(admin.ModelAdmin):
    pass
class TimeCardAdmin(admin.ModelAdmin):
    pass
class ReportAdmin(admin.ModelAdmin):
    pass
class PointAdmin(admin.ModelAdmin):
    pass
class ExtraPointAdmin(admin.ModelAdmin):
    pass
class PointRateAdmin(admin.ModelAdmin):
    pass
class QuoteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(TimeCard, TimeCardAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(ExtraPoint, ExtraPointAdmin)
admin.site.register(PointRate, PointRateAdmin)
admin.site.register(Quote, QuoteAdmin)