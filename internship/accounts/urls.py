from django.urls import path
from .views import  *

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('patient_dashboard/', patient_dashboard, name='patient_dashboard'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
     path('create-blog/', create_blog_post, name='create_blog_post'),
    path('doctor-blogs/', doctor_blog_list, name='doctor_blog_list'),
    path('patient-blogs/', patient_blog_list, name='patient_blog_list'),
    path('blog/<int:blog_id>/',blog_detail, name='blog_detail'),
    path('edit-blog/<int:blog_id>/', edit_blog_post, name='edit_blog_post'),
]
