from django.contrib import admin
from .models import *
from users.models import CustomUser

class EmployeeInline(admin.TabularInline):
    can_delete = False
    model = CustomUser
    fields = ('username', 'work_email', 'role', 'employee_id', 'job_title', 'employee_status', 'contract_type')
    extra = 0

class JobTitleInline(admin.TabularInline):
    model = JobTitle
    extra = 0

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0

class VacationRequestInline(admin.StackedInline):
    model = VacationRequest
    extra = 0

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_type', 'industry', 'created_at')
    search_fields = ('name', 'industry', 'email', 'city', 'country')
    list_filter = ('company_type', 'industry', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    inlines = [JobTitleInline, ExpenseInline, EmployeeInline]

admin.site.register(VacationRequest)
admin.site.register(Document)
admin.site.register(Expense)