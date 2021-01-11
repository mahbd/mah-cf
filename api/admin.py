from django.contrib import admin
from .models import User, Problem


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'cf_handle', 'solve', 'accepted', 'wrong', 'limit')
    search_fields = ('cf_handle', 'username', 'first_name', 'last_name', 'batch')


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('problem_name', 'total_solve')


admin.site.register(User, UserAdmin)
admin.site.register(Problem, ProblemAdmin)
