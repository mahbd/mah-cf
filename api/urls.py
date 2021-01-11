from django.urls import path

from . import views

urlpatterns = [
    path('problems/cf_handle=<str:cf_handle>/', views.ProblemList.as_view()),
    path('problems/batch=<int:batch>/', views.ProblemList.as_view()),
    path('problems/', views.ProblemList.as_view()),
    path('submissions/cf_handle=<str:cf_handle>/', views.CfSubmissionList.as_view()),
    path('submissions/batch=<int:batch>/', views.CfSubmissionList.as_view()),
    path('submissions/', views.CfSubmissionList.as_view()),
    path('users/id=<str:pk>/', views.UserDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('login/', views.login_user),
    path('logout/', views.logout_user),
    # path('test/', views.test_params),
]
