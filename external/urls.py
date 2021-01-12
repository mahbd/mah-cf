from django.urls import path

from external import views

urlpatterns = [
    path('cf/uss/handle=<str:handle_name>', views.single_user_single_page),
    path('cf/usa/handle=<str:handle_name>', views.single_user_all_page),
    path('cf/uaa/', views.all_user_all_page),
    path('cf/uas/', views.all_user_single_page),
    path('add_cf_handle/', views.add_cf_handle),
]