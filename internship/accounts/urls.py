from django.urls import path
from .views import signup_view, login_view, logout_view, patient_dashboard, doctor_dashboard

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('patient_dashboard/', patient_dashboard, name='patient_dashboard'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
]
