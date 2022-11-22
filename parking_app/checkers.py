from re import compile
from datetime import datetime, timedelta


class Checkers:

    @staticmethod
    def check_if_username_valid(username):
        username_format = compile(r'[A-Za-z\d]+')
        return False if not username_format.match(username) or username.lower() == "username" else True

    @staticmethod
    def check_if_email_address_valid(email_address):
        email_address_format = compile(r'[^@]+@[^@]+\.[^@]+')
        return False if not email_address_format.match(email_address) else True

    @staticmethod
    def check_if_password_valid(password):
        password_format = compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,10}$')
        return False if not password_format.match(password) or password.lower() == "password" else True

    @staticmethod
    def check_if_license_plate_valid(plate_number):
        license_plate_format = compile(r'^[A-Z\d]{1,3}-[A-Z\d]{1,3}-[A-Z\d]{1,3}$')
        return False if len(plate_number) != 8 or not license_plate_format.match(plate_number) or not \
            isinstance(plate_number, str) else True

    @staticmethod
    def check_if_length_of_stay_valid(length_of_stay):
        length_of_stay_format = compile(r'^\d{1,4}\.\d{2}$')
        return False if not length_of_stay_format.match(length_of_stay) else True

    @staticmethod
    def parse_length_of_stay(length_of_stay):
        length_of_stay_hours, length_of_stay_minutes = length_of_stay.split(".")
        selected_length_of_stay = timedelta(hours=int(length_of_stay_hours), minutes=int(length_of_stay_minutes))
        return selected_length_of_stay

    def calculate_arrival_and_departure_time(self, length_of_stay):
        arrival_time = datetime.now()
        selected_length_of_stay = self.parse_length_of_stay(length_of_stay)
        departure_time = arrival_time + selected_length_of_stay
        return arrival_time, departure_time

    @staticmethod
    def check_if_length_of_stay_over_a_year(length_of_stay):
        return False if float(length_of_stay) > 8765.82 else True
