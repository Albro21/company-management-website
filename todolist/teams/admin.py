from django.contrib import admin
from .models import Company, Role, Member

class MemberInline(admin.TabularInline):
    model = Member
    extra = 1
    
class RoleInline(admin.TabularInline):
    model = Role
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_type', 'industry', 'created_by', 'created_at')
    search_fields = ('name', 'industry', 'email', 'city', 'country')
    list_filter = ('company_type', 'industry', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    inlines = [RoleInline, MemberInline]

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role')
    list_filter = ('role',)
