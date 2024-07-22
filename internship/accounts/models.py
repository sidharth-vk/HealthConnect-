from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from datetime import datetime, timedelta

class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Unique related name for custom User model
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',  # Unique related name for custom User model
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user'
    )

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)




from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blog_images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    summary = models.TextField(max_length=500)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


User = get_user_model()

class Appointment(models.Model):
    patient = models.ForeignKey(User, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, related_name='doctor_appointments', on_delete=models.CASCADE)
    speciality = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def save(self, *args, **kwargs):
        # Convert date and start_time from strings to their respective objects if needed
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").date()
        if isinstance(self.start_time, str):
            self.start_time = datetime.strptime(self.start_time, "%H:%M").time()

        # Calculate end time based on start time and duration (45 minutes)
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = start_datetime + timedelta(minutes=45)
        self.end_time = end_datetime.time()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Appointment with {self.doctor} on {self.date} at {self.start_time}"