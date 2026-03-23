from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_code, name='analyze_code'),
    path('compare/', views.compare_code, name='compare_code'),
    path('fix/', views.fix_code, name='fix_code'),
    path('explain/', views.explain_code, name='explain_code'),
    path('login/', views.login_code, name='login_code'),
    path('learn/', views.learn_code, name='learn_code'),
    path('history/', views.get_history, name='get_history'),
]
