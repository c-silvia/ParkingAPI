import requests
from unittest import TestCase

root_address = "http://localhost:5000/"

login_details = {"username": "silvia", "password": "Pa55wor!"}
cookies = requests.post(root_address + "log-in", json=login_details).cookies


class TestUserAccess(TestCase):

    def test_successful_log_in(self):
        result = requests.post(root_address + "log-in", json=login_details)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content.decode(), "Successfully logged in.")

    def test_unsuccessful_log_in_wrong_username(self):
        user_details = {"username": "notsilvia", "password": "Pa55wor!"}
        result = requests.post(root_address + "log-in", json=user_details)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.content.decode(), "User not found.")

    def test_unsuccessful_log_in_wrong_password(self):
        user_details = {"username": "silvia", "password": "password"}
        result = requests.post(root_address + "log-in", json=user_details)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "Incorrect password entered.")

    def test_successful_log_out(self):
        result = requests.get(root_address + "log-out", cookies=cookies)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content.decode(), "Successfully logged out.")

    def test_unsuccessful_log_out(self):
        result = requests.get(root_address + "log-out")
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")


class TestUserRegistration(TestCase):

    def test_unsuccessful_registration_missing_key(self):
        registration_details = {"username": "Beethoven01", "email_address": "beethoven01@test.dummy.com"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "Missing data.")

    def test_unsuccessful_registration_missing_value(self):
        registration_details = {"username": "Beethoven01", "email_address": "", "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "Missing data.")

    def test_unsuccessful_registration_invalid_username(self):
        registration_details = {"username": "Username", "email_address": "beethoven01@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "The word 'username' cannot be used as username.")

    def test_unsuccessful_registration_existing_username(self):
        registration_details = {"username": "silvia", "email_address": "beethoven01@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "This username is already linked to an existing user.")

    def test_unsuccessful_registration_existing_email_address(self):
        registration_details = {"username": "Beethoven01", "email_address": "silvia@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "This email address is already linked to an existing user.")

    def test_unsuccessful_registration_invalid_username_format(self):
        registration_details = {"username": 112358, "email_address": "beethoven01@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        type_error_content = "The username, email address and password should be strings of text.\n" \
                             "Username text must contain characters and/or numbers.\n" \
                             "Password text must be between 8 and 10 characters, must contain at least one uppercase " \
                             "letter, one lowercase letter, one number and one special character."
        self.assertEqual(result.content.decode(), type_error_content)

    def test_unsuccessful_registration_invalid_email_address_format(self):
        registration_details = {"username": "Beethoven01", "email_address": "beethoven01attestdotdummydotcom",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "Invalid email address entered.")

    def test_unsuccessful_registration_invalid_password_(self):
        registration_details = {"username": "Beethoven01", "email_address": "beethoven01@test.dummy.com",
                                "password": "password"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        invalid_password_content = "Password must be between 8 and 10 characters, must contain at least one " \
                                   "uppercase letter, one lowercase letter, one number and one special character.\n" \
                                   "The word 'password' cannot be used as a password."
        self.assertEqual(result.content.decode(), invalid_password_content)

    def test_unsuccessful_registration_invalid_password_format(self):
        registration_details = {"username": "Beethoven01", "email_address": "beethoven01@test.dummy.com",
                                "password": "Pa55word"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        invalid_password_content = "Password must be between 8 and 10 characters, must contain at least one " \
                                   "uppercase letter, one lowercase letter, one number and one special character.\n" \
                                   "The word 'password' cannot be used as a password."
        self.assertEqual(result.content.decode(), invalid_password_content)

    def test_successful_registration(self):
        registration_details = {"username": "Beethoven01", "email_address": "beethoven01@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content.decode(), "User successfully created.")
