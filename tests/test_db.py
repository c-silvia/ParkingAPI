from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime

import parking_app.db
from parking_app.db import DBClient, DBUsers, DBData
import parking_app.exceptions


@patch("parking_app.db._connect_to_db")
class TestDBClient(TestCase):

    def setUp(self):
        self.cursor = MagicMock()

    def test_selection_query(self, db_connector_function):
        db_client = DBClient()
        self.cursor.__iter__.return_value = [("A01", "A02", "A03")]
        db_client._selection_query(self.cursor, "SELECT * FROM table;")
        self.cursor.execute.assert_called_with("SELECT * FROM table;")
        db_client._selection_query(self.cursor, "SELECT * FROM table WHERE column=%s;", ["id"])
        self.cursor.execute.assert_called_with("SELECT * FROM table WHERE column=%s;", ["id"])

    def test_insertion_query(self, db_connector_function):
        db_client = DBClient()
        db_client._insertion_query(self.cursor, "INSERT INTO table (column) VALUES (%s) WHERE id=%s;", ["id"], ["A01"])
        self.cursor.execute.assert_called_with("INSERT INTO table (column) VALUES (%s) WHERE id=%s;",
                                               ["id", "A01"])
        db_client._insertion_query(self.cursor, "INSERT INTO table (column) VALUES (%s)", ["A01"])
        self.cursor.execute.assert_called_with("INSERT INTO table (column) VALUES (%s)", ["A01"])
        db_client._insertion_query(self.cursor, "UPDATE table SET column=NULL where id=%s", [None], ["A01"])
        self.cursor.execute.assert_called_with("UPDATE table SET column=NULL where id=%s", [None, "A01"])
        db_client._insertion_query(self.cursor, "UPDATE table SET column=NULL")
        self.cursor.execute.assert_called_with("UPDATE table SET column=NULL", None)


@patch("parking_app.db._connect_to_db")
class TestDBUsers(TestCase):

    def test_user_creation(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        db_user.create_user("Beethoven01", "address@email.com", "Pa55wor!")
        cursor.execute.assert_called_with("INSERT INTO login_data (username, email_address, password) VALUES "
                                          "(%s, %s, %s);", ["Beethoven01", "address@email.com", "Pa55wor!"])

    def test_check_for_existing_user_negative(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = [()]
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_user.check_if_username_already_exists("a_username")
        self.assertEqual(False, result)

    def test_check_for_existing_user_positive(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = [(1,)]
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_user.check_if_username_already_exists("a_username")
        self.assertEqual(True, result)

    def test_check_for_existing_address_negative(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = [()]
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_user.check_if_email_address_already_exists("address@email.com")
        self.assertEqual(False, result)

    def test_check_for_existing_address_positive(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = [(1,)]
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_user.check_if_email_address_already_exists("address@email.com")
        self.assertEqual(True, result)

    def test_getting_user_data_from_username_negative(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = []
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.UserNotFound):
            db_user.get_user_data_from_username("Beethoven01")

    def test_getting_user_data_from_username_positive(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = [(1, "Beethoven01", "address@email.com", "Pa55wor!",)]
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_user.get_user_data_from_username("Beethoven01")
        self.assertEqual(
            {"user_id": 1, "username": "Beethoven01", "email_address": "address@email.com", "password": "Pa55wor!"},
            result)

    def test_registration_input_missing_data(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.MissingData):
            db_user.check_registration_input("Beethoven01", "address@email.com", None)

    def test_registration_input_same_username(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("Beethoven01", "address@email.com", "Pa55wor!")]
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.UsernameAlreadyUsed):
            db_user.check_registration_input("Beethoven01", "address@email.com", "Pa55wor!")

    def test_registration_input_same_email(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("Beethoven01", "address@email.com", "Pa55wor!")]
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.UsernameAlreadyUsed):
            db_user.check_registration_input("Beethoven01", "address@email.com", "Pa55wor!")

    def test_registration_input_invalid_username(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.InvalidUsername):
            db_user.check_registration_input("username", "address@email.com", "Pa55wor!")

    def test_registration_input_invalid_username_format(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(TypeError):
            db_user.check_registration_input(111, "address@email.com", "Pa55wor!")

    def test_registration_input_invalid_email_address(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.InvalidEmail):
            db_user.check_registration_input("Beethoven01", "addressatemaildotcom", "Pa55wor!")

    def test_registration_input_invalid_password(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.InvalidPassword):
            db_user.check_registration_input("Beethoven01", "address@email.com", "password")

    def test_registration_input_short_password(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.InvalidPassword):
            db_user.check_registration_input("Beethoven01", "address@email.com", "Pa5!")

    def test_correct_registration_input(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        db_user.check_registration_input("Beethoven01", "address@email.com", "Pa55wor!")


@patch("parking_app.db._connect_to_db")
class TestDBData(TestCase):

    def test_check_for_existing_spot_negative(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [()]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data._check_if_spot_exists("A48")
        self.assertEqual(False, result)

    def test_check_for_existing_spot_positive(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [(1,)]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data._check_if_spot_exists("A48")
        self.assertEqual(True, result)

    def test_spot_availability_unavailable(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("S-627-JM",)]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data._check_if_spot_available("A48")
        self.assertEqual(False, result)

    def test_spot_availability_available(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [()]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data._check_if_spot_available("A48")
        self.assertEqual(True, result)

    def test_parking_data_checks_invalid_length_of_stay_type(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(TypeError):
            db_data.check_incoming_values_before_parking("A48", "S-627-JM", 11111.22)

    def test_parking_data_checks_invalid_length_of_stay(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.InvalidLengthOfStay):
            db_data.check_incoming_values_before_parking("A48", "S-627-JM", "1111.22m")

    def test_parking_data_checks_length_of_stay_over_a_year(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.TooLong):
            db_data.check_incoming_values_before_parking("A48", "S-627-JM", "9111.22")

    def test_parking_data_checks_invalid_spot_number(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.InvalidSpotNumber):
            db_data.check_incoming_values_before_parking("48", "S-627-JM", "1111.22")

    def test_parking_data_checks_spot_unavailable(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("K-267-MJ",)]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.SpotNotAvailable):
            db_data.check_incoming_values_before_parking("A48", "S-627-JM", "1111.22")

    def test_no_vacant_spots(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = []
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.NoSpotsAvailable):
            db_data.get_vacant_spots()

    def test_get_vacant_spots(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("A48", "A01",)]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data.get_vacant_spots()
        self.assertEqual(["A48", "A01"], result)

    def test_no_vacant_spots_count(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = []
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.NoSpotsAvailable):
            db_data.get_vacant_spots_count()

    def test_get_vacant_spots_count(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("A48", "A01",)]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data.get_vacant_spots_count()
        self.assertEqual("2", result)

    def test_get_spot_from_plate_plate_not_in_db(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = []
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.LicensePlateNotFound):
            db_data.get_spot_from_plate("S-627-JM")

    def test_get_spot_from_plate_invalid_plate_format(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.InvalidPlateNumber):
            db_data.get_spot_from_plate("S627JM")

    def test_get_spot_from_plate_positive(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("A48",)]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data.get_spot_from_plate("S-627-JM")
        self.assertEqual("A48", result)

    def test_no_unavailable_spots(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = []
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.AllSpotsAvailable):
            db_data.get_unavailable_spots_and_plates()

    def test_get_unavailable_spots_and_plates(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("A48", "S-627-JM",)]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data.get_unavailable_spots_and_plates()
        self.assertEqual({"A48": "S-627-JM"}, result)

    def test_parking(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        db_data.park_car("A48", "S-627-JM")
        cursor.execute.assert_called_with("UPDATE parking_spot_data SET vehicle_number = %s WHERE spot_id = %s;",
                                          ["S-627-JM", "A48"])

    def test_storing_parking_time(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        db_data.store_parking_time("A48", "S-627-JM", datetime(2022, 11, 22, 11, 51, 19), "00.01",
                                   datetime(2022, 11, 22, 11, 52, 19), 0, None, 0)
        cursor.execute.assert_called_with("INSERT INTO parked_vehicles_data (spot_id, vehicle_number, arrival_time, "
                                          "selected_length_of_stay, expected_departure_time, has_left, "
                                          "actual_departure_time, has_expired) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                                          ["A48", "S-627-JM", "2022-11-22 11:51:19", "00.01",
                                           "2022-11-22 11:52:19", 0, None, 0])

    def test_unable_to_leave_parking_spot_invalid_plate_format(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = []
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.InvalidPlateNumber):
            db_data.leave_parking_spot("S627JM")

    def test_unable_to_leave_parking_spot_no_plate(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = []
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        with self.assertRaises(parking_app.exceptions.LicensePlateNotFound):
            db_data.leave_parking_spot("S-627-JM")

    def test_leaving_parking_spot(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("S-627-JM",)]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        db_data.leave_parking_spot("S-627-JM")
        cursor.execute.assert_called_with("UPDATE parked_vehicles_data SET has_left = 1, actual_departure_time = %s  "
                                          "WHERE vehicle_number = %s and has_left = 0;",
                                          [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "S-627-JM"])

    def test_getting_next_available_spot(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        db_data._selection_query = MagicMock(side_effect=[[], [("A48", datetime.strptime("2022-11-28 08:25:46", "%Y-%m-%d %H:%M:%S")),
                                        ("A100", datetime.strptime("2022-11-27 17:46:00", "%Y-%m-%d %H:%M:%S"))]])
        cursor.__iter__.return_value = [("A48", datetime.strptime("2022-11-28 08:25:46", "%Y-%m-%d %H:%M:%S")),
                                        ("A100", datetime.strptime("2022-11-27 17:46:00", "%Y-%m-%d %H:%M:%S"))]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_data.get_next_available_spot()
        self.assertEqual("A100", result)

    def test_check_if_stay_expired(self, db_connector_function):
        db_data = DBData()
        cursor = MagicMock()
        cursor.__iter__.return_value = [("A48", datetime.strptime("2022-11-21 08:25:46", "%Y-%m-%d %H:%M:%S"))]
        db_data.cnx.cursor.return_value.__enter__.return_value = cursor
        db_data.check_if_stay_expired()
        cursor.execute.assert_called_with("UPDATE parked_vehicles_data SET has_expired = 1 WHERE spot_id = %s;",
                                          ["A48"])
