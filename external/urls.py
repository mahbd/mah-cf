from django.http import JsonResponse
from django.urls import path

from external import views

urlpatterns = [
    path('cf/uss/handle=<str:handle_name>', lambda x: JsonResponse({'status': 'Removed'})),
    path('cf/usa/handle=<str:handle_name>', views.single_user),
    path('cf/uaa/', views.all_user),
    path('cf/uas/', lambda x: JsonResponse({'status': 'Removed'})),
    path('add_cf_handle/', views.add_cf_handle),
    path('transfer_problems/', views.transfer_problems)
]
