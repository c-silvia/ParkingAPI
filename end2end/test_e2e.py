import requests
from unittest import TestCase

root_address = "http://localhost:5000/"

login_details = {"username": "testuser", "password": "Pa55wor!"}
cookies = requests.post(root_address + "log-in", json=login_details).cookies


class Test02UserAccess(TestCase):

    def test_successful_log_in(self):
        result = requests.post(root_address + "log-in", json=login_details)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content.decode(), "Successfully logged in.")

    def test_unsuccessful_log_in_wrong_username(self):
        user_details = {"username": "notthetestuser", "password": "Pa55wor!"}
        result = requests.post(root_address + "log-in", json=user_details)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.content.decode(), "User not found.")

    def test_unsuccessful_log_in_wrong_password(self):
        user_details = {"username": "testuser", "password": "password"}
        result = requests.post(root_address + "log-in", json=user_details)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "Incorrect password entered.")

    def test_successful_log_out(self):
        result = requests.get(root_address + "log-out", cookies=cookies)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content.decode(), "Successfully logged out.")

    def test_unauthorized_action(self):
        result = requests.get(root_address + "log-out")
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")


class Test01UserRegistration(TestCase):

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
        registration_details = {"username": "Username", "email_address": "beethoven0@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "The word 'username' cannot be used as username.")

    def test_unsuccessful_registration_existing_username(self):
        registration_details = {"username": "testuser", "email_address": "beethoven01@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "This username is already linked to an existing user.")

    def test_unsuccessful_registration_existing_email_address(self):
        registration_details = {"username": "Beethoven02", "email_address": "beethoven01@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "This email address is already linked to an existing user.")

    def test_unsuccessful_registration_invalid_username_format(self):
        registration_details = {"username": 112358, "email_address": "beethoven02@test.dummy.com",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        type_error_content = "The username, email address and password should be strings of text.\n" \
                             "Username text must contain characters and/or numbers.\n" \
                             "Password text must be between 8 and 10 characters, must contain at least one uppercase " \
                             "letter, one lowercase letter, one number and one special character."
        self.assertEqual(result.content.decode(), type_error_content)

    def test_unsuccessful_registration_invalid_email_address_format(self):
        registration_details = {"username": "Beethoven02", "email_address": "beethoven01attestdotdummydotcom",
                                "password": "Pa55wor!2"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "Invalid email address entered.")

    def test_unsuccessful_registration_invalid_password_(self):
        registration_details = {"username": "Beethoven02", "email_address": "beethoven02@test.dummy.com",
                                "password": "password"}
        result = requests.post(root_address + "register", json=registration_details)
        self.assertEqual(result.status_code, 400)
        invalid_password_content = "Password must be between 8 and 10 characters, must contain at least one " \
                                   "uppercase letter, one lowercase letter, one number and one special character.\n" \
                                   "The word 'password' cannot be used as a password."
        self.assertEqual(result.content.decode(), invalid_password_content)

    def test_unsuccessful_registration_invalid_password_format(self):
        registration_details = {"username": "Beethoven02", "email_address": "beethoven02@test.dummy.com",
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


class Test03DataRetrieval(TestCase):

    def test_unauthorized_action_search_license_plate(self):
        license_plate = {"license_plate": "Z-810-TU"}
        result = requests.post(root_address + "search-license-plate", json=license_plate)
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")

    def test_searching_existing_license_plate(self):
        license_plate = {"license_plate": "Z-810-TU"}
        result = requests.post(root_address + "search-license-plate", json=license_plate, cookies=cookies)
        self.assertEqual(result.status_code, 200)

    def test_searching_unrecognized_license_plate(self):
        license_plate = {"license_plate": "Q-810-TU"}
        result = requests.post(root_address + "search-license-plate", json=license_plate, cookies=cookies)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.content.decode(), "There are no vehicles with this license plate number currently "
                                                  "parked in the parking lot.")

    def test_searching_invalid_license_plate(self):
        license_plate = {"license_plate": "Q810TU"}
        result = requests.post(root_address + "search-license-plate", json=license_plate, cookies=cookies)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content.decode(), "This is not a valid license plate number.")

    def test_unauthorized_action_search_vacant_spots(self):
        result = requests.get(root_address + "vacant-spots")
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")

    def test_searching_vacant_spots(self):
        result = requests.get(root_address + "vacant-spots", cookies=cookies)
        self.assertEqual(result.status_code, 200)

    def test_unauthorized_action_get_vacant_spots_count(self):
        result = requests.get(root_address + "vacant-spots-count")
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")

    def test_getting_vacant_spots_count(self):
        result = requests.get(root_address + "vacant-spots-count", cookies=cookies)
        self.assertEqual(result.status_code, 200)

    def test_unauthorized_action_get_unavailable_spots_with_plates(self):
        result = requests.get(root_address + "unavailable-spots")
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")

    def test_getting_unavailable_spots_with_plates(self):
        result = requests.get(root_address + "unavailable-spots", cookies=cookies)
        self.assertEqual(result.status_code, 200)

    def test_unauthorized_action_check_next_available_spot(self):
        result = requests.get(root_address + "next-available-spot")
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")

    def test_getting_unavailable_check_next_available_spot(self):
        result = requests.get(root_address + "next-available-spot", cookies=cookies)
        self.assertEqual(result.status_code, 200)


class Test04ParkingAndLeaving(TestCase):
    def test_unauthorized_action_park_car(self):
        result = requests.post(root_address + "park-car")
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")

    def test_unsuccessful_parking_missing_data(self):
        parking_details = {"license_plate": "L-713-KQ", "length_of_stay": "1.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, "Missing data.")

    def test_unsuccessful_parking_invalid_spot_number_format(self):
        parking_details = {"parking_spot": 48, "license_plate": "L-713-KQ", "length_of_stay": "1.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, "This is not a valid parking spot number.")

    def test_unsuccessful_parking_invalid_spot_number(self):
        parking_details = {"parking_spot": "A108", "license_plate": "L-713-KQ", "length_of_stay": "1.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, "This is not a valid parking spot number.")

    def test_unsuccessful_parking_unavailable_spot(self):
        parking_details = {"parking_spot": "A01", "license_plate": "L-713-KQ", "length_of_stay": "1.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.text, "The selected spot is currently not available.")

    def test_unsuccessful_parking_invalid_license_plate(self):
        parking_details = {"parking_spot": "A48", "license_plate": "L713KQ", "length_of_stay": "1.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, "This is not a valid license plate number.")

    def test_unsuccessful_parking_invalid_license_plate_type(self):
        parking_details = {"parking_spot": "A48", "license_plate": 123, "length_of_stay": "1.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        type_error_content = "The parking spot and license plate should be a string of text.\n" \
                             "The length of stay should be a string of text written in the following format: '0.00'."
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, type_error_content)

    def test_unsuccessful_parking_license_plate_already_in_parking_lot(self):
        parking_details = {"parking_spot": "A48", "license_plate": "Z-810-TU", "length_of_stay": "1.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.text, "This license plate is already linked to another parking spot currently in use.")

    def test_unsuccessful_parking_invalid_length_of_stay_type(self):
        parking_details = {"parking_spot": "A48", "license_plate": "L-713-KQ", "length_of_stay": 1.23}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        type_error_content = "The parking spot and license plate should be a string of text.\n" \
                             "The length of stay should be a string of text written in the following format: '0.00'."
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, type_error_content)

    def test_unsuccessful_parking_invalid_length_of_stay(self):
        parking_details = {"parking_spot": "A48", "license_plate": "L-713-KQ", "length_of_stay": "1.233"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        invalid_length_content = "Invalid length of stay entered.\n" \
                                 "The length of stay should be a string of text written in the following format: " \
                                 "'0.00'."
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, invalid_length_content)

    def test_unsuccessful_parking_too_long(self):
        parking_details = {"parking_spot": "A48", "license_plate": "L-713-KQ", "length_of_stay": "9111.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, "A vehicle cannot occupy a spot for longer than a year.")

    def test_successful_parking(self):
        parking_details = {"parking_spot": "A48", "license_plate": "L-713-KQ", "length_of_stay": "1.23"}
        result = requests.post(root_address + "park-car", json=parking_details, cookies=cookies)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.text, "A48")

    def test_unauthorized_action_leave_parking_spot(self):
        license_plate = {"license_plate": "L-713-KQ"}
        result = requests.post(root_address + "leave-parking-spot", json=license_plate)
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.content.decode(), "Please log in to continue.")

    def test_unsuccessfully_leaving_invalid_license_plate(self):
        license_plate = {"license_plate": "L713KQ"}
        result = requests.post(root_address + "leave-parking-spot", json=license_plate, cookies=cookies)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.text, "This is not a valid license plate number.")

    def test_unsuccessfully_leaving_invalid_vehicle_not_in_parking_lot(self):
        license_plate = {"license_plate": "N-713-KQ"}
        result = requests.post(root_address + "leave-parking-spot", json=license_plate, cookies=cookies)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.text, "There are no vehicles with this license plate number currently parked in the "
                                      "parking lot.")

    def test_successfully_leaving(self):
        license_plate = {"license_plate": "L-713-KQ"}
        result = requests.post(root_address + "leave-parking-spot", json=license_plate, cookies=cookies)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.text, "Parking spot now available.")
