import os, mysql.connector, math
from mysql.connector import IntegrityError
from re import compile
from datetime import datetime

from exceptions import NoSpotsAvailable, InvalidPlateNumber, LicensePlateNotFound, AllSpotsAvailable, \
    InvalidSpotNumber, SpotNotAvailable, VehicleAlreadyInOtherSpot, DbConnectionError, UserNotFound, NotLoggedIn, \
    IncorrectPassword, InvalidLengthOfStay, TooLong

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
            query = "SELECT EXISTS(SELECT * from parking_spot_data WHERE spot_id = %s);"
            matches = self._selection_query(cursor, query, [parking_spot])
            spot = "".join(
                [str(parking_spot) for parking_spot in list(sum(matches, ())) if parking_spot != 0])  # fix syntax
            return False if not spot else True

    def _check_if_spot_available(self, parking_spot):
        with self.cnx.cursor() as cursor:
            query = "SELECT vehicle_number FROM parking_spot_data WHERE spot_id = %s;"
            matches = self._selection_query(cursor, query, [parking_spot])
            spot = "".join(
                [parking_spot for parking_spot in list(sum(matches, ())) if parking_spot is not None])  # fix syntax
            return True if not spot else False

    @staticmethod
    def _check_if_length_of_stay_valid(length_of_stay):
        length_of_stay_format = compile(r'^\d{1,4}\.\d{2}$')
        return False if not length_of_stay_format.match(length_of_stay) else True

    @staticmethod
    def _round_up_length_of_stay(length_of_stay):
        if length_of_stay[-1] != 0:
            rounded_up_length_of_stay = math.ceil(float(length_of_stay) * 10) / 10
            return str(rounded_up_length_of_stay)
        return length_of_stay

    @staticmethod
    def _check_if_length_of_stay_over_a_year(length_of_stay):
        return False if float(length_of_stay) > 8765.80 else True  # n of hours in a year

    def check_incoming_values_before_parking(self, spot, plate, length_of_stay):
        if not self._check_if_length_of_stay_valid(length_of_stay):
            raise InvalidLengthOfStay
        rounded_length_of_stay = self._round_up_length_of_stay(length_of_stay)
        if not self._check_if_length_of_stay_over_a_year(rounded_length_of_stay):
            raise TooLong
        elif not self._check_if_spot_exists(spot):
            raise InvalidSpotNumber
        elif not self._check_if_spot_available(spot):
            raise SpotNotAvailable
        elif not self._check_if_license_plate_valid(plate):
            raise InvalidPlateNumber
        try:
            self.get_spot_from_plate(plate)
            raise VehicleAlreadyInOtherSpot
        except LicensePlateNotFound:
            pass
        return rounded_length_of_stay

    def get_vacant_spots(self):
        with self.cnx.cursor() as cursor:
            query = "SELECT spot_id FROM parking_spot_data WHERE vehicle_number IS NULL ORDER BY spot_id;"
            matches = self._selection_query(cursor, query)
            if matches:
                vacant_spots = list(sum(matches, ()))  # fix syntax
                return vacant_spots
            raise NoSpotsAvailable

    def get_vacant_spots_count(self):
        vacant_spots_count = str(len(self.get_vacant_spots()))
        return vacant_spots_count

    def get_spot_from_plate(self, license_plate):
        with self.cnx.cursor() as cursor:
            query = "SELECT spot_id FROM parking_spot_data WHERE vehicle_number = %s;"
            matches = self._selection_query(cursor, query, [license_plate])
            if matches:
                return "".join([parking_spot for parking_spot in list(sum(matches, ()))])  # fix syntax
            elif not self._check_if_license_plate_valid(license_plate):
                raise InvalidPlateNumber
            raise LicensePlateNotFound

    def get_unavailable_spots_and_plates(self):
        with self.cnx.cursor() as cursor:
            query = "SELECT spot_id, vehicle_number FROM parking_spot_data WHERE vehicle_number IS NOT NULL " \
                    "ORDER BY spot_id;"
            matches = self._selection_query(cursor, query)
            if matches:
                unavailable_spots_and_plates = {pair[0]: pair[1] for pair in matches}
                return unavailable_spots_and_plates
            raise AllSpotsAvailable

    def park_car(self, parking_spot, license_plate):
        with self.cnx.cursor() as cursor:
            query = "UPDATE parking_spot_data SET vehicle_number = %s WHERE spot_id = %s;"
            self._insertion_query(cursor, query, [license_plate], [parking_spot])
            self.cnx.commit()
            # returning spot where car has been parked in endpoint

    def store_parking_time(self, license_plate, arrival_time, length_of_stay, expected_departure_time, spot_id,
                           has_left, actual_departure_time, has_expired):
        with self.cnx.cursor() as cursor:
            query = "INSERT INTO parked_vehicles_data (spot_id, vehicle_number, arrival_time, " \
                    "selected_length_of_stay, expected_departure_time, has_left, actual_departure_time, has_expired) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            incoming_data = [spot_id, license_plate, arrival_time.strftime("%Y-%m-%d %H:%M:%S"), length_of_stay,
                             expected_departure_time.strftime("%Y-%m-%d %H:%M:%S"), int(has_left),
                             actual_departure_time.strftime("%Y-%m-%d %H:%M:%S"), int(has_expired)]
            self._insertion_query(cursor, query, incoming_data)
            self.cnx.commit()

    def leave_parking_spot(self, license_plate):
        with self.cnx.cursor() as cursor:
            if not self._check_if_license_plate_valid(license_plate):
                raise InvalidPlateNumber
            parking_spot = self.get_spot_from_plate(license_plate)
            update_parking_spot_data_query = "UPDATE parking_spot_data SET vehicle_number = NULL WHERE spot_id = %s;"
            update_parked_vehicles_data_query = "UPDATE parked_vehicles_data SET has_left = 1, has_expired = 1 WHERE " \
                                                "vehicle_number = %s;"
            self._insertion_query(cursor, update_parking_spot_data_query, filter_values=[parking_spot])
            self._insertion_query(cursor, update_parked_vehicles_data_query, filter_values=[license_plate])
            self.cnx.commit()

    def get_next_available_spot(self):
        with self.cnx.cursor() as cursor:
            query = "SELECT spot_id, expected_departure_time FROM parked_vehicles_data WHERE has_left = 0;"
            matches = self._selection_query(cursor, query)
            if matches:
                spots_and_departure_times = {pair[0]: pair[1] for pair in matches}
                now = datetime.now()
                next_available_spot = min(list(spots_and_departure_times.items()), key=lambda x: abs(x[1] - now))[0]
            else:
                next_available_spot = self.get_vacant_spots()[0]
            return next_available_spot  # fix syntax



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
