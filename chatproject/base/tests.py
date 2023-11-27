import unittest
from django.test import TestCase
from django.contrib.messages import get_messages
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from . models import Friend, Requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# class LoginTestCase(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.login_url = reverse('login')

#     # Test that a user can log in with valid credentials
#     def test_login_successful(self):
#         response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'})
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('index'))
#         # Check if the user is now logged in
#         user_is_authenticated = self.client.login(username='testuser', password='testpassword')
#         self.assertTrue(user_is_authenticated)

#     # Test that login fails with invalid credentials
#     def test_login_unsuccessful(self):
#         response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'wrongpassword'})
#         self.assertEqual(response.status_code, 302)
#         messages = [m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Invalid credentials', messages)

#         # Check if the user is not logged in
#         user_is_authenticated = self.client.login(username='testuser', password='wrongpassword')
#         self.assertFalse(user_is_authenticated)

# class RegistrationTestCase(TestCase):
#     def setUp(self):
#         print('setup')
#         self.register_url = reverse('register')
#         User.objects.create_user(username='existing_user', password='t', email='existing@gmail.com')

#         with open("C:/Users/user/Pictures/Screenshots/c1.png", 'rb') as file:
#             file_content = file.read()

#         with open("C:/Users/user/Videos/vid.mkv", 'rb') as file:
#             file_content2 = file.read()
#         self.correct_file = SimpleUploadedFile('c1.png', file_content)
#         self.incorrect_file = SimpleUploadedFile('vid.mkv', file_content2)

#     def test_successful_with_everything(self):
#         response = self.client.post(self.register_url,
#         {'name': 'test', 'surname': 'testov', 'username': 'test', 'password': 't', 'password2': 't', 'email': 'test@gmail.com', 'inputFile': self.correct_file})
#         self.assertEqual(response.status_code, 302)
#         user_is_authenticated = self.client.login(username='test', password='t')
#         self.assertTrue(user_is_authenticated)

#     def test_successful_without_profile_image_file(self):
#         response = self.client.post(self.register_url,
#         {'name': 'test', 'surname': 'testov', 'username': 'test', 'password': 't', 'password2': 't', 'email': 'test@gmail.com'})
#         self.assertEqual(response.status_code, 302)
#         user_is_authenticated = self.client.login(username='test', password='t')
#         self.assertTrue(user_is_authenticated)

#     def test_unmatching_passwords_with_space(self):
#         response = self.client.post(self.register_url,
#         {'name': 'test', 'surname': 'testov', 'username': 'test', 'password': 't', 'password2': 'wrong t', 'email': 'test@gmail.com'})
#         self.assertEqual(response.status_code, 302)
#         messages = [m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Passwords did not match or contains spaces', messages)
#         user_is_authenticated = self.client.login(username='test', password='t')
#         self.assertFalse(user_is_authenticated)

#     def test_with_errors(self):
#         response = self.client.post(self.register_url,
#         {'name': ' ', 'surname': '', 'username': ' test', 'password': ' t', 'password2': 'wrong t', 'email': 'testgmail.com'})
#         self.assertEqual(response.status_code, 302)
#         messages = [m.message for m in get_messages(response.wsgi_request)]
#         self.assertEqual(len(messages), 5)
#         user_is_authenticated = self.client.login(username='test', password='t')
#         self.assertFalse(user_is_authenticated)
    
#     def test_with_incorrect_profile_image_file(self):
#         response = self.client.post(self.register_url,
#         {'name': 'test', 'surname': 'testov', 'username': 'test', 'password': 't', 'password2': 'wrong t', 'email': 'test@gmail.com', 'inputFile': self.incorrect_file})
#         self.assertEqual(response.status_code, 302)
#         messages = [m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Profile Image is not supported upload one of the followings: jpg, png, jpeg', messages)
#         user_is_authenticated = self.client.login(username='test', password='t')
#         self.assertFalse(user_is_authenticated)
    
#     def test_existing_user(self):
#         response = self.client.post(self.register_url,
#         {'name': 'test', 'surname': 'testov', 'username': 'existing_user', 'password': 't', 'password2': 't', 'email': 'existing@gmail.com'})
#         self.assertEqual(response.status_code, 302)
#         messages = [m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Username already exists', messages)
#         self.assertIn('Email already registered', messages)
#         self.assertEqual(len(messages), 2)
#         user_is_authenticated = self.client.login(username='test', password='t')
#         self.assertFalse(user_is_authenticated)



# class SeleniumTestCase(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome()
#         self.user1 = User.objects.get(username='tes1')
#         self.user2 = User.objects.get(username='tes2')
#         Requests.objects.create(from_user=self.user1, to_user=self.user2)
#         self.driver.get("http://localhost:8000/requests")

#     def login_func(self, driver, username, password):
#         username_id = "username"
#         password_id = "password"
#         button_id = "submit"
#         WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.ID, username_id))
#         )
#         username_field = driver.find_element(By.ID, username_id)
#         WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.ID, password_id))
#         )
#         password_field = driver.find_element(By.ID, password_id)
#         WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.ID, button_id))
#         )
#         button = driver.find_element(By.ID, button_id)

#         username_field.send_keys(username)
#         password_field.send_keys(password)
#         button = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.ID, button_id))
#         )
#         button.click()

    
#     def test_accept_request(self):
#         self.login_func(self.driver, 'tes2', 't')
#         self.driver.get("http://localhost:8000/requests")
#         WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "tes1"))
#         )
#         button = self.driver.find_element(By.NAME, 'accept')
#         button.click()
    
#     def test_remove_request(self):
#         self.driver.get("http://localhost:8000/")
#         self.login_func(self.driver, 'tes2', 't')
#         self.driver.get("http://localhost:8000/requests")
#         WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "tes1"))
#         )
#         button = self.driver.find_element(By.NAME, 'remove')
#         button.click()
#         try:
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.ID, "tes1"))
#             )
#             found = True
#         except Exception:
#             found = False
            
#         self.assertTrue(found)
    
#     def test_empty_requests(self):
#         self.login_func(self.driver, 'tes2', 't')
#         self.driver.get("http://localhost:8000/requests")
#         found = False
#         try:
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.ID, "tes1"))
#             )
#             found = True
#         except Exception:
#             found = False
            
#         self.assertTrue(found)
    

#     def tearDown(self):
#         self.driver.quit()


    