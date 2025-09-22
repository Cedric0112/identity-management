from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile

class IdentityManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_list_url = reverse('profile-list')
        self.create_profile_url = reverse('create_profile')
        
        self.user = User.objects.create_user(username='john', password='pass1234')
    
    def test_user_registration(self):
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        })
        # Should redirect to login page after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())


    def test_user_login_and_logout(self):
        login_response = self.client.post(self.login_url, {
            'username': 'john',
            'password': 'pass1234'
        })
        self.assertEqual(login_response.status_code, 302)  # Redirect to /myprofiles/

        logout_response = self.client.post(self.logout_url)
        self.assertEqual(logout_response.status_code, 302)

    def test_profile_creation(self):
        self.client.login(username='john', password='pass1234')
        response = self.client.post(self.create_profile_url, {
            'context': 'work',
            'display_name': 'John W.',
            'bio': 'This is John.',
            'visibility': 'public'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to profile list
        self.assertEqual(Profile.objects.count(), 1)
        profile = Profile.objects.first()
        self.assertEqual(profile.user.username, 'john')

    def test_profile_visibility_and_access(self):
        # Create a profile for the user
        profile = Profile.objects.create(
            user=self.user,
            context='social',
            display_name='JohnSocial',
            bio='Social bio',
            visibility='private'
        )
        # Login and view profile list
        self.client.login(username='john', password='pass1234')
        response = self.client.get(self.profile_list_url)
        self.assertContains(response, 'JohnSocial')
        self.assertEqual(response.status_code, 200)

    def test_profile_edit(self):
        self.client.login(username='john', password='pass1234')
        profile = Profile.objects.create(
            user=self.user,
            context='test',
            display_name='Old Name',
            bio='Old bio',
            visibility='public'
        )
        edit_url = reverse('update_profile', args=[profile.id])
        response = self.client.post(edit_url, {
            'context': 'test',
            'display_name': 'New Name',
            'bio': 'Updated bio',
            'visibility': 'private'
        })
        self.assertRedirects(response, self.profile_list_url)
        profile.refresh_from_db()
        self.assertEqual(profile.display_name, 'New Name')
        self.assertEqual(profile.visibility, 'private')

class UserAccountTests(TestCase):
    def test_user_signup_and_login(self):
        response = self.client.post('/api/accounts/register/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after signup
        self.assertTrue(User.objects.filter(username='testuser').exists())


    def test_profile_creation(self):
        user = User.objects.create_user(username='u1', password='pw12345')
        self.client.login(username='u1', password='pw12345')
        response = self.client.post('/api/profiles/create/', {
            'context': 'social',
            'display_name': 'CoolKid',
            'visibility': 'public',
        })
        self.assertEqual(Profile.objects.count(), 1)

