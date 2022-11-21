from unittest import TestCase
from parking_app.checkers import Checkers
from datetime import timedelta


class TestCheckers(TestCase):
    def setUp(self):
        self.checker = Checkers()

    def test_invalid_username(self):
        result = self.checker.check_if_username_valid("Username")
        expected = False
        self.assertEqual(expected, result)

    def test_invalid_username_type(self):
        with self.assertRaises(TypeError):
            self.checker.check_if_username_valid(123)

    def test_invalid_username_format(self):
        result = self.checker.check_if_username_valid("!23")
        expected = False
        self.assertEqual(expected, result)

    def valid_username(self):
        result = self.checker.check_if_username_valid("Beethoven01")
        expected = True
        self.assertEqual(expected, result)

    def test_invalid_email_address(self):
        result = self.checker.check_if_email_address_valid("addressatemaildotcom")
        expected = False
        self.assertEqual(expected, result)

    def test_email_address_missing_at_sign(self):
        result = self.checker.check_if_email_address_valid("addressatemail.com")
        expected = False
        self.assertEqual(expected, result)

    def test_email_address_missing_dot(self):
        result = self.checker.check_if_email_address_valid("address@emaildotcom")
        expected = False
        self.assertEqual(expected, result)

    def test_email_address_at_sign_before_and_after_at_sign(self):
        result = self.checker.check_if_email_address_valid("address@@@email.com")
        expected = False
        self.assertEqual(expected, result)

    def test_valid_email_address(self):
        result = self.checker.check_if_email_address_valid("address@email.com")
        expected = True
        self.assertEqual(expected, result)

    def test_invalid_password(self):
        result = self.checker.check_if_password_valid("Password")
        expected = False
        self.assertEqual(expected, result)

    def test_invalid_password_type(self):
        with self.assertRaises(TypeError):
            self.checker.check_if_password_valid(123)

    def test_password_missing_symbol(self):
        result = self.checker.check_if_password_valid("Pa55word")
        expected = False
        self.assertEqual(expected, result)

    def test_password_missing_uppercase(self):
        result = self.checker.check_if_password_valid("pa55wor!")
        expected = False
        self.assertEqual(expected, result)

    def test_password_missing_lowercase(self):
        result = self.checker.check_if_password_valid("PA55WOR!")
        expected = False
        self.assertEqual(expected, result)

    def test_password_missing_digit(self):
        result = self.checker.check_if_password_valid("Passwor!")
        expected = False
        self.assertEqual(expected, result)

    def test_short_password(self):
        result = self.checker.check_if_password_valid("Pa5!")
        expected = False
        self.assertEqual(expected, result)

    def test_long_password(self):
        result = self.checker.check_if_password_valid("Pa55wor!!!!!!!!!!")
        expected = False
        self.assertEqual(expected, result)

    def test_valid_password(self):
        result = self.checker.check_if_password_valid("Pa55wor!")
        expected = True
        self.assertEqual(expected, result)

    def test_invalid_license_plate(self):
        result = self.checker.check_if_license_plate_valid("L1C3NS3P")
        expected = False
        self.assertEqual(expected, result)

    def test_invalid_license_plate_type(self):
        with self.assertRaises(TypeError):
            self.checker.check_if_license_plate_valid(11122333)

    def test_license_plate_lower(self):
        result = self.checker.check_if_license_plate_valid("a-123-bc")
        expected = False
        self.assertEqual(expected, result)

    def test_short_license_plate(self):
        result = self.checker.check_if_license_plate_valid("a-1-b")
        expected = False
        self.assertEqual(expected, result)

    def test_long_license_plate(self):
        result = self.checker.check_if_license_plate_valid("A-123-BCD")
        expected = False
        self.assertEqual(expected, result)

    def test_valid_license_plate(self):
        result = self.checker.check_if_license_plate_valid("A-123-BC")
        expected = True
        self.assertEqual(expected, result)

    def test_length_of_stay_over_4_integers(self):
        result = self.checker.check_if_length_of_stay_valid("11111.22")
        expected = False
        self.assertEqual(expected, result)

    def test_length_of_stay_under_integer(self):
        result = self.checker.check_if_length_of_stay_valid(".22")
        expected = False
        self.assertEqual(expected, result)

    def test_length_of_stay_over_2_decimals(self):
        result = self.checker.check_if_length_of_stay_valid("1111.222")
        expected = False
        self.assertEqual(expected, result)

    def test_length_of_stay_under_1_decimal(self):
        result = self.checker.check_if_length_of_stay_valid("1111.2")
        expected = False
        self.assertEqual(expected, result)

    def test_length_of_stay_no_decimals(self):
        result = self.checker.check_if_length_of_stay_valid("111122")
        expected = False
        self.assertEqual(expected, result)

    def test_invalid_length_of_stay_type(self):
        with self.assertRaises(TypeError):
            self.checker.check_if_license_plate_valid(1.23)

    def test_valid_length_of_stay(self):
        result = self.checker.check_if_length_of_stay_valid("1111.22")
        expected = True
        self.assertEqual(expected, result)

    def test_invalid_length_of_stay_parsing(self):
        with self.assertRaises(AttributeError):
            self.checker.parse_length_of_stay(1111.22)

    def test_valid_length_of_stay_parsing(self):
        result = self.checker.parse_length_of_stay("1111.22")
        expected = timedelta(hours=1111, minutes=22)
        self.assertEqual(expected, result)

    def test_invalid_arrival_and_departure_time(self):
        with self.assertRaises(AttributeError):
            self.checker.calculate_arrival_and_departure_time(1111.22)

    def test_valid_arrival_and_departure_time(self):
        result = self.checker.check_if_length_of_stay_over_a_year("1111.22")
        expected = True
        self.assertEqual(expected, result)

    def test_invalid_length(self):
        result = self.checker.check_if_length_of_stay_over_a_year("11111.22")
        expected = False
        self.assertEqual(expected, result)

    def test_valid_length(self):
        result = self.checker.check_if_length_of_stay_over_a_year("1111.22")
        expected = True
        self.assertEqual(expected, result)

