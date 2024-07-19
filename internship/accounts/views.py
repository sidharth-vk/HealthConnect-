from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import User, Patient, Doctor
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .decorators import user_type_required

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        address = request.POST['address']
        profile_picture = request.FILES.get('profile_picture')
        is_patient = 'is_patient' in request.POST
        is_doctor = 'is_doctor' in request.POST

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=make_password(password),
            address=address,
            profile_picture=profile_picture,
            is_patient=is_patient,
            is_doctor=is_doctor
        )
        user.save()

        if user.is_patient:
            Patient.objects.create(user=user)
        if user.is_doctor:
            Doctor.objects.create(user=user)
        
        login(request, user)
        if user.is_patient:
            return redirect('patient_dashboard')
        elif user.is_doctor:
            return redirect('doctor_dashboard')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_patient:
                return redirect('patient_dashboard')
            elif user.is_doctor:
                return redirect('doctor_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_type_required('patient')
def patient_dashboard(request):
    if not request.user.is_patient:
        return HttpResponseForbidden("You are not authorized to view this page.")
    return render(request, 'patient_dashboard.html')

@login_required
@user_type_required('doctor')
def doctor_dashboard(request):
    if not request.user.is_doctor:
        return HttpResponseForbidden("You are not authorized to view this page.")
    return render(request, 'doctor_dashboard.html')