import os, mysql.connector
from mysql.connector import IntegrityError
from re import compile

from exceptions import NoSpotsAvailable, InvalidPlateNumber, LicensePlateNotFound, AllSpotsAvailable, \
    InvalidSpotNumber, SpotNotAvailable, VehicleAlreadyInOtherSpot, DbConnectionError, UserNotFound, NotLoggedIn, \
    IncorrectPassword

DB_NAME = "parking_app"


# Need to close the db?? - already closing cursor

def _connect_to_db():
    cnx = mysql.connector.connect(
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        auth_plugin='mysql_native_password',
        database=os.getenv('DATABASE_DB')
    )
    return cnx


class DBClient:
    def __init__(self):
        self.cnx = _connect_to_db()

    @staticmethod
    def _selection_query(cursor, statement, lookup_value=None):
        if lookup_value is not None:
            cursor.execute(statement, lookup_value)
        else:
            cursor.execute(statement)
        matches = [match for match in cursor]  # fix formatting
        return matches

    @staticmethod
    def _insertion_query(cursor, statement, input_values=None, filter_values=None):
        if input_values and filter_values:
            sql_data = input_values + filter_values
        elif input_values and not filter_values:
            sql_data = input_values
        else:
            sql_data = filter_values
        cursor.execute(statement, sql_data)


class DBUsers(DBClient):

    def create_user(self, username, email, hashed_password):
        with self.cnx.cursor() as cursor:
            query = "INSERT INTO login_data (username, email_address, password) VALUES (%s, %s, %s);"
            self._insertion_query(cursor, query, [username, email, hashed_password])
            self.cnx.commit()

    def get_user_data(self, username):
        with self.cnx.cursor() as cursor:
            login_data_headers = ["user_id", "username", "email_address", "password"]
            query = "SELECT user_id, username, email_address, password FROM login_data WHERE username = %s;"
            matches = self._selection_query(cursor, query, [username])
            if matches:
                raw_values = [value for value in list(sum(matches, ()))]  # fix syntax
                user_data = dict(zip(login_data_headers, raw_values))
                return user_data
            raise UserNotFound


class DBData(DBClient):

    @staticmethod
    def _check_if_license_plate_valid(plate_number):
        license_plate_format = compile(r'^[A-Z\d]{1,3}-[A-Z\d]{1,3}-[A-Z\d]{1,3}$')
        if len(plate_number) != 8 or not license_plate_format.match(plate_number) or not isinstance(plate_number, str):
            return False
        return True

    def _check_if_spot_exists(self, parking_spot):
        with self.cnx.cursor() as cursor:
            query = "SELECT EXISTS(SELECT * from parking_spot_status WHERE spot_id = %s);"
            matches = self._selection_query(cursor, query, [parking_spot])
            spot = "".join(
                [str(parking_spot) for parking_spot in list(sum(matches, ())) if parking_spot != 0])  # fix syntax
            return False if not spot else True

    def _check_if_spot_available(self, parking_spot):
        with self.cnx.cursor() as cursor:
            query = "SELECT vehicle_number FROM parking_spot_status WHERE spot_id = %s;"
            matches = self._selection_query(cursor, query, [parking_spot])
            spot = "".join(
                [parking_spot for parking_spot in list(sum(matches, ())) if parking_spot is not None])  # fix syntax
            return True if not spot else False

    # new function to check if length of stay is valid

    # recursion?
    def get_vacant_spots(self):
        with self.cnx.cursor() as cursor:
            query = "SELECT spot_id FROM parking_spot_status WHERE vehicle_number IS NULL ORDER BY spot_id;"
            matches = self._selection_query(cursor, query)
            if matches:
                vacant_spots = list(sum(matches, ())) # fix syntax
                return vacant_spots
            raise NoSpotsAvailable

    def get_vacant_spots_count(self):
        vacant_spots_count = str(len(self.get_vacant_spots()))
        return vacant_spots_count

    def get_spot_from_plate(self, license_plate):
        with self.cnx.cursor() as cursor:
            query = "SELECT spot_id FROM parking_spot_status WHERE vehicle_number = %s;"
            matches = self._selection_query(cursor, query, [license_plate])
            if matches:
                return "".join([parking_spot for parking_spot in list(sum(matches, ()))])  # fix syntax
            elif not self._check_if_license_plate_valid(license_plate):
                raise InvalidPlateNumber
            raise LicensePlateNotFound

    # Handle if all spots are available: recursion?
    def get_unavailable_spots_and_plates(self):
        with self.cnx.cursor() as cursor:
            query = "SELECT spot_id, vehicle_number FROM parking_spot_status WHERE vehicle_number IS NOT NULL " \
                    "ORDER BY spot_id;"
            matches = self._selection_query(cursor, query)
            if matches:
                unavailable_spots_and_plates = {pair[0]: pair[1] for pair in matches}
                return unavailable_spots_and_plates
            raise AllSpotsAvailable

    # Handle edge cases
    def store_parking_time(self, license_plate, arrival_time, length_of_stay, departure_time):
        with self.cnx.cursor() as cursor:
            query = "INSERT INTO vehicle_permanence (vehicle_number, vehicle_arrival_time, selected_length_of_stay, " \
                    "vehicle_departure_time) VALUES (%s, %s, %s %s); "
            self._insertion_query(cursor, query, [license_plate, arrival_time, length_of_stay, departure_time])
            self.cnx.commit()

    # rollback code?
    # recursion?
    # extend to include datetime
    def park_car(self, parking_spot, license_plate):
        with self.cnx.cursor() as cursor:
            if not self._check_if_spot_exists(parking_spot):
                raise InvalidSpotNumber
            elif not self._check_if_spot_available(parking_spot):
                raise SpotNotAvailable
            elif not self._check_if_license_plate_valid(license_plate):
                raise InvalidPlateNumber
            try:
                self.get_spot_from_plate(license_plate)
                raise VehicleAlreadyInOtherSpot
            except LicensePlateNotFound:
                pass
            query = "UPDATE parking_spot_status SET vehicle_number = %s WHERE spot_id = %s;"
            self._insertion_query(cursor, query, [license_plate], [parking_spot])
            self.cnx.commit()
            # returning spot where car has been parked in endpoint

    # recursion?
    # extend to include datetime
    def leave_parking_spot(self, license_plate):
        with self.cnx.cursor() as cursor:
            if not self._check_if_license_plate_valid(license_plate):
                raise InvalidPlateNumber
            parking_spot = self.get_spot_from_plate(license_plate)
            query = "UPDATE parking_spot_status SET vehicle_number = NULL WHERE spot_id = %s"
            self._insertion_query(cursor, query, filter_values=[parking_spot])
            self.cnx.commit()


# def store_news_articles(news_articles_list):
#     db_name = DB_NAME
#     db_connection = _connect_to_db()
#     try:
#         cur = db_connection.cursor()
#         print("Connected to DB: %s" % db_name)
#         with cur as cursor:
#             for news_piece in news_articles_list:
#                 try:
#                     title = news_piece["title"]
#                     article_url = news_piece["article_url"]
#                     article_published_date = news_piece["article_published_date"]
#                     sql_statement = "INSERT INTO news_articles (News_Title, News_URL, News_Date) VALUES (%s, %s, %s)"
#                     sql_data = (title, article_url, article_published_date)
#                     cursor.execute(sql_statement, sql_data)
#                 except IntegrityError:
#                     db_connection.rollback()
#                     continue
#         db_connection.commit()
#     except DbConnectionError:
#         raise
#     finally:
#         db_connection.close()
