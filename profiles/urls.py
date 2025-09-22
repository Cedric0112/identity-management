from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import ProfileViewSet, public_profiles,profile_list_view,create_profile,update_profile, delete_profile, register_user, delete_account , public_profiles_page, UserListViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'users', UserListViewSet, basename='user')
router.register(r'identities', ProfileViewSet, basename='identities')

urlpatterns = [
    path('', include(router.urls)),
    path('public/', public_profiles),
    path('myprofiles/', profile_list_view, name='profile-list'),
    path('profiles/create/', create_profile, name='create_profile'),
    path('profiles/<int:pk>/edit/', update_profile, name='update_profile'),
    path('profiles/<int:pk>/delete/', delete_profile, name='delete_profile'),
    path('accounts/register/', register_user, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/delete/', delete_account, name='delete_account'),
    path("profiles/public/", public_profiles_page, name="public_profiles_page"),


] 
