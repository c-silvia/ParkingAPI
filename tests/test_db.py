import mysql.connector
from mysql.connector import errorcode
from unittest import TestCase
from unittest.mock import patch, MagicMock

import parking_app.db
from parking_app.db import DBClient, DBUsers, DBData
import parking_app.exceptions


@patch("parking_app.db._connect_to_db")  # mocking something from another file
class TestDBClient(TestCase):

    def setUp(self):
        self.cursor = MagicMock()  # mocking something to pass to a function

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


class TestDBData(TestCase):
    pass
