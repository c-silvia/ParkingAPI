import mysql.connector
from mysql.connector import errorcode
from unittest import TestCase
from unittest.mock import patch, MagicMock

import parking_app.db
from parking_app.db import DBClient, DBUsers, DBData


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


@patch("parking_app.db._connect_to_db")  # mocking something from another file
class TestDBUsers(TestCase):

    def test_user_creation(self, db_connector_function):
        db_user = DBUsers()
        #("INSERT INTO login_data (username, email_address, password) "VALUES (%s, %s, %s);", ["a_username", "email@address.com", "Pa55wor!"])

    def test_check_for_non_existing_user(self, db_connector_function):
        db_user = DBUsers()
        result = db_user.check_if_username_already_exists("a_username")
        self.assertEqual(False, result)

    def test_check_for_existing_user(self, db_connector_function):
        db_user = DBUsers()
        cursor = MagicMock()
        cursor.__iter__.return_value = [(1,)]
        db_user.cnx.cursor.return_value.__enter__.return_value = cursor
        result = db_user.check_if_username_already_exists("a_username")
        self.assertEqual(True, result)

    def test_check_if_email_address_already_exists(self, db_connector_function):
        db_user = DBUsers()
        result = db_user.check_if_username_already_exists("address@email.com")
        self.assertEqual(False, result)


class MockDBData(TestCase):
    pass
