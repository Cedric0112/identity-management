from rest_framework import viewsets, permissions,filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Profile
from .forms import ProfileForm
from .serializers import ProfileSerializer, UserSerializer
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser
from allauth.account.models import EmailAddress
from django.contrib.auth import logout
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import ProfileFilter
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from .models import DeletedAccountLog

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

     #Filtering & searching config
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProfileFilter
    search_fields = ["display_name", "context", "gender", "pronouns"]
    ordering_fields = ["id", "display_name", "context"]
    ordering = ["id"]

   
    def get_queryset(self):
        user = self.request.user
        context = self.request.query_params.get('context')

        # Show public profiles + user's private/restricted profiles
        queryset = Profile.objects.filter(
            Q(visibility='public') |
            Q(user=user)
        )

        # If user is authenticated, include restricted profiles
        if user.is_authenticated:
            queryset = Profile.objects.filter(
                Q(visibility='public') |
                Q(visibility='restricted') |
                Q(user=user)
            )

        if context:
            queryset = queryset.filter(context=context)

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # If no pagination, fallback
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def home_view(request):
    return render(request, 'home.html')

@api_view(['GET'])
def public_profiles(request):
    context = request.query_params.get('context')
    queryset = Profile.objects.filter(visibility='public')
    if context:
        queryset = queryset.filter(context=context)
    serializer = ProfileSerializer(queryset, many=True)
    return Response(serializer.data)

def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Create email address record
            email_address, created = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"verified": False, "primary": True},
            )

            # Send confirmation email (new API)
            email_address.send_confirmation(request)

            # Add message to show on login page
            messages.success(
                request,
                "Account created! Please check your email to verify before logging in."
            )

            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile created successfully.')
            return redirect('profile-list')
        else:
            messages.error(request, 'Error creating profile. Please check the form.')
    else:
        form = ProfileForm()
    return render(request, 'profiles/profile_form.html', {'form': form})

@login_required
def update_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk, user=request.user)

    if request.method == 'POST':
        # Check if user clicked "Remove Profile Picture"
        if "remove_pic" in request.POST:
            if profile.profile_pic:
                profile.profile_pic.delete(save=False)  # remove file from storage
                profile.profile_pic = None
                profile.save()
                messages.success(request, "Profile picture removed.")
            return redirect('update_profile', pk=profile.pk)

        # Otherwise, normal update form handling
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile-list')
        else:
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profiles/profile_form.html', {'form': form})


@login_required
def delete_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk, user=request.user)
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Profile deleted successfully.')
        return redirect('profile-list')
    return redirect('profile-list')

@login_required
def profile_list_view(request):
    profiles = Profile.objects.filter(user=request.user)

    if request.user.is_staff and "staff_deletion_notices" in request.session:
        for notice in request.session["staff_deletion_notices"]:
            messages.warning(request, notice)
        # Clear after displaying once
        del request.session["staff_deletion_notices"]
    return render(request, 'profiles/profile_list.html', {'profiles': profiles})

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        username = user.username

        # Log the deletion before removing user
        DeletedAccountLog.objects.create(username=username)

        # Delete the user and logout
        user.delete()
        logout(request)

        # Show styled confirmation page
        return render(request, "profiles/account_deleted.html", {"username": username})

    return render(request, "profiles/delete_account.html")

@login_required
def public_profiles_page(request):
    profiles = Profile.objects.filter(visibility="public")
    return render(request, "profiles/public_profiles.html", {"profiles": profiles})

@receiver(user_logged_in)
def notify_account_deleted(sender, request, user, **kwargs):
    deleted_username = request.session.pop("account_deleted", None)
    if deleted_username and user.is_staff:
        messages.warning(
            request,
            f"User {deleted_username} has deleted their account.",
            extra_tags="safe"
        )

class UserListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        print("DEBUG USER:", request.user)
        print("IS AUTHENTICATED:", request.user.is_authenticated)
        print("IS STAFF:", request.user.is_staff)
        return super().list(request, *args, **kwargs)
