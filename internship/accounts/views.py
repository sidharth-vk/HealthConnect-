from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .decorators import user_type_required
from django.core.files.storage import default_storage
from django.utils import timezone


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
    
    # Get current date and time
    now = timezone.now()
    
    # Fetch upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        date__gte=now.date(),
        start_time__gte=now.time()
    ).order_by('date', 'start_time')

    return render(request, 'patient_dashboard.html', {
        'upcoming_appointments': upcoming_appointments
    })
@login_required
@user_type_required('doctor')
def doctor_dashboard(request):
    if not request.user.is_doctor:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    appointments = Appointment.objects.filter(doctor=request.user)
    
    return render(request, 'doctor_dashboard.html', {'appointments': appointments})


@login_required
def create_blog_post(request):
    if not request.user.is_doctor:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        summary = request.POST.get('summary')
        content = request.POST.get('content')
        draft = request.POST.get('draft') == 'on'
        image = request.FILES.get('image')
        
        category = Category.objects.get(id=category_id)
        blog_post = BlogPost(
            title=title,
            category=category,
            summary=summary,
            content=content,
            draft=draft,
            author=request.user
        )
        if image:
            blog_post.image = default_storage.save(f'blog_images/{image.name}', image)
        blog_post.save()
        return redirect('doctor_blog_list')

    categories = Category.objects.all()
    return render(request, 'create_blog_post.html', {'categories': categories})

def doctor_blog_list(request):
    if not request.user.is_doctor:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    published_posts = BlogPost.objects.filter(author=request.user, draft=False)
    draft_posts = BlogPost.objects.filter(author=request.user, draft=True)
    
    return render(request, 'doctor_blog_list.html', {
        'published_posts': published_posts,
        'draft_posts': draft_posts
    })
@login_required
def patient_blog_list(request):
    if not request.user.is_patient:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    categories = Category.objects.all()
    blog_posts_by_category = {category: BlogPost.objects.filter(category=category, draft=False) for category in categories}
    
    return render(request, 'patient_blog_list.html', {'blog_posts_by_category': blog_posts_by_category})



@login_required
def blog_detail(request, blog_id):
    blog_post = get_object_or_404(BlogPost, id=blog_id)
    if not request.user.is_doctor and blog_post.draft:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    return render(request, 'blog_detail.html', {'blog_post': blog_post})


@login_required
def edit_blog_post(request, blog_id):
    blog_post = get_object_or_404(BlogPost, id=blog_id)
    if blog_post.author != request.user:
        return HttpResponseForbidden("You are not authorized to edit this blog post.")
    
    if request.method == 'POST':
        blog_post.title = request.POST.get('title')
        blog_post.category_id = request.POST.get('category')
        blog_post.summary = request.POST.get('summary')
        blog_post.content = request.POST.get('content')
        blog_post.draft = request.POST.get('draft') == 'on'
        if request.FILES.get('image'):
            blog_post.image = default_storage.save(f'blog_images/{request.FILES.get("image").name}', request.FILES.get('image'))
        blog_post.save()
        return redirect('doctor_blog_list')

    categories = Category.objects.all()
    return render(request, 'edit_blog_post.html', {'blog_post': blog_post, 'categories': categories})





@login_required
def list_doctors(request):
    doctors = User.objects.filter(is_doctor=True)
    return render(request, 'list_doctors.html', {'doctors': doctors})

@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id, is_doctor=True)
    if request.method == 'POST':
        speciality = request.POST.get('speciality')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            speciality=speciality,
            date=date,
            start_time=start_time
        )
        return redirect('appointment_detail', appointment_id=appointment.id)
    return render(request, 'book_appointment.html', {'doctor': doctor})

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user != appointment.patient and request.user != appointment.doctor:
        return HttpResponseForbidden("You are not authorized to view this page.")
    return render(request, 'appointment_detail.html', {'appointment': appointment})