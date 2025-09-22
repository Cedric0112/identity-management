from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('prefer_not', 'Prefer Not to Say'),
    ]

    PRONOUN_CHOICES = [
        ('he_him', 'He/Him'),
        ('she_her', 'She/Her'),
        ('they_them', 'They/Them'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    context = models.CharField(max_length=50)  # e.g., 'work', 'social', 'legal'
    display_name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True) #new
    pronouns = models.CharField(max_length=20, choices=PRONOUN_CHOICES, blank=True, null=True) #new
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True) # new
    visibility = models.CharField(
        max_length=10,
        choices=[('public', 'Public'), ('private', 'Private'), ('restricted', 'Restricted')],
        default='public'
    )

    def __str__(self):
        return f"{self.user.username} ({self.context})"

class DeletedAccountLog(models.Model):
    username = models.CharField(max_length=150)
    deleted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} deleted at {self.deleted_at}"
