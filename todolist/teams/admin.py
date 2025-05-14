from django.contrib import admin
from .models import *

class MemberInline(admin.TabularInline):
    model = Member
    extra = 1
    
class JobTitleInline(admin.TabularInline):
    model = JobTitle
    extra = 1

class DocumentInline(admin.TabularInline):
    model = Document
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
    inlines = [JobTitleInline, MemberInline]

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title')
    search_fields = ('user__username', 'job_title')
    inlines = [DocumentInline, VacationRequestInline]

admin.site.register(VacationRequest)
admin.site.register(Document)