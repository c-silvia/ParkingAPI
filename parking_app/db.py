import os
import mysql.connector
from datetime import datetime
from parking_app.checkers import Checkers

from parking_app.exceptions import NoSpotsAvailable, InvalidPlateNumber, LicensePlateNotFound, AllSpotsAvailable, \
    InvalidSpotNumber, SpotNotAvailable, VehicleAlreadyInOtherSpot, UserNotFound, \
    InvalidLengthOfStay, TooLong, MissingData, UsernameAlreadyUsed, EmailAlreadyUsed, InvalidUsername, InvalidEmail, \
    InvalidPassword


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
        self.checker = Checkers()

    @staticmethod
    def _selection_query(cursor, statement, lookup_value=None):
        if lookup_value is not None:
            cursor.execute(statement, lookup_value)
        else:
            cursor.execute(statement)
        matches = [match for match in cursor]
        return matches

    @staticmethod
    def _insertion_query(cursor, statement, input_values=None, filter_values=None):
        sql_data = None
        if input_values and filter_values:
            sql_data = input_values + filter_values
        elif input_values and not filter_values:
            sql_data = input_values
        elif not input_values and filter_values:
            sql_data = filter_values
        else:
            cursor.execute(statement)
        cursor.execute(statement, sql_data)


class DBUsers(DBClient):

    def create_user(self, username, email, hashed_password):
        with self.cnx.cursor() as cursor:
            query = "INSERT INTO login_data (username, email_address, password) VALUES (%s, %s, %s);"
            self._insertion_query(cursor, query, [username, email, hashed_password])
            self.cnx.commit()

    def check_if_username_already_exists(self, username):
        with self.cnx.cursor() as cursor:
            query = "SELECT EXISTS(SELECT * from login_data WHERE username = %s);"
            matches = self._selection_query(cursor, query, [username])
            name = "".join(
                [str(username) for username in list(sum(matches, ())) if username != 0])
            return False if not name else True

    def check_if_email_address_already_exists(self, email_address):
        with self.cnx.cursor() as cursor:
            query = "SELECT EXISTS(SELECT * from login_data WHERE email_address = %s);"
            matches = self._selection_query(cursor, query, [email_address])
            address = "".join(
                [str(email_address) for email_address in list(sum(matches, ())) if email_address != 0])
            return False if not address else True

    def get_user_data_from_username(self, username):
        login_data_headers = ["user_id", "username", "email_address", "password"]
        with self.cnx.cursor() as cursor:
            query = "SELECT user_id, username, email_address, password FROM login_data WHERE username = %s;"
            matches = self._selection_query(cursor, query, [username])
            if matches:
                raw_values = [value for value in list(sum(matches, ()))]
                user_data = dict(zip(login_data_headers, raw_values))
                return user_data
            raise UserNotFound

    def check_registration_input(self, username, email_address, password):
        if not username or not email_address or not password:
            raise MissingData
        elif self.check_if_username_already_exists(username):
            raise UsernameAlreadyUsed
        elif self.check_if_email_address_already_exists(email_address):
            raise EmailAlreadyUsed
        elif not self.checker.check_if_username_valid(username):
            raise InvalidUsername
        elif not self.checker.check_if_email_address_valid(email_address):
            raise InvalidEmail
        elif not self.checker.check_if_password_valid(password):
            raise InvalidPassword


class DBData(DBClient):

    def _check_if_spot_exists(self, parking_spot):
        with self.cnx.cursor() as cursor:
            query = "SELECT EXISTS(SELECT * from parking_spot_data WHERE spot_id = %s);"
            matches = self._selection_query(cursor, query, [parking_spot])
            spot = "".join(
                [str(parking_spot) for parking_spot in list(sum(matches, ())) if parking_spot != 0])
            return False if not spot else True

    def _check_if_spot_available(self, parking_spot):
        with self.cnx.cursor() as cursor:
            query = "SELECT vehicle_number FROM parking_spot_data WHERE spot_id = %s;"
            matches = self._selection_query(cursor, query, [parking_spot])
            spot = "".join(
                [parking_spot for parking_spot in list(sum(matches, ())) if parking_spot is not None])
            return True if not spot else False

    def check_incoming_values_before_parking(self, spot, plate, length_of_stay):
        if not self.checker.check_if_length_of_stay_valid(length_of_stay):
            raise InvalidLengthOfStay
        if not self.checker.check_if_length_of_stay_over_a_year(length_of_stay):
            raise TooLong
        elif not self._check_if_spot_exists(spot):
            raise InvalidSpotNumber
        elif not self._check_if_spot_available(spot):
            raise SpotNotAvailable
        elif not self.checker.check_if_license_plate_valid(plate):
            raise InvalidPlateNumber
        try:
            self.get_spot_from_plate(plate)
            raise VehicleAlreadyInOtherSpot
        except LicensePlateNotFound:
            pass

    def get_vacant_spots(self):
        with self.cnx.cursor() as cursor:
            query = "SELECT spot_id FROM parking_spot_data WHERE vehicle_number IS NULL ORDER BY spot_id;"
            matches = self._selection_query(cursor, query)
            if matches:
                vacant_spots = list(sum(matches, ()))
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
                return "".join([parking_spot for parking_spot in list(sum(matches, ()))])
            elif not self.checker.check_if_license_plate_valid(license_plate):
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

    def store_parking_time(self, spot_id, license_plate, arrival_time, length_of_stay, expected_departure_time,
                           has_left, actual_departure_time, has_expired):
        with self.cnx.cursor() as cursor:
            query = "INSERT INTO parked_vehicles_data (spot_id, vehicle_number, arrival_time, " \
                    "selected_length_of_stay, expected_departure_time, has_left, actual_departure_time, has_expired) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            incoming_data = [spot_id, license_plate, arrival_time.strftime("%Y-%m-%d %H:%M:%S"), length_of_stay,
                             expected_departure_time.strftime("%Y-%m-%d %H:%M:%S"), int(has_left),
                             actual_departure_time, int(has_expired)]
            self._insertion_query(cursor, query, incoming_data)
            self.cnx.commit()

    def leave_parking_spot(self, license_plate):
        with self.cnx.cursor() as cursor:
            if not self.checker.check_if_license_plate_valid(license_plate):
                raise InvalidPlateNumber
            parking_spot = self.get_spot_from_plate(license_plate)
            update_parking_spot_data_query = "UPDATE parking_spot_data SET vehicle_number = NULL WHERE spot_id = %s;"
            actual_departure_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_parked_vehicles_data_query = "UPDATE parked_vehicles_data SET has_left = 1, actual_departure_time " \
                                                "= %s  WHERE vehicle_number = %s and has_left = 0;"
            self._insertion_query(cursor, update_parking_spot_data_query, filter_values=[parking_spot])
            self._insertion_query(cursor, update_parked_vehicles_data_query, [actual_departure_time], [license_plate])
            self.cnx.commit()

    def get_next_available_spot(self):
        with self.cnx.cursor() as cursor:
            try:
                if self.get_vacant_spots():
                    next_available_spot = self.get_vacant_spots()[0]
                    return next_available_spot
            except NoSpotsAvailable:
                pass
            query = "SELECT spot_id, expected_departure_time FROM parked_vehicles_data WHERE has_left = 0;"
            matches = self._selection_query(cursor, query)
            if matches:
                spots_and_departure_times = {spot_id: expected_departure_time for spot_id, expected_departure_time
                                             in matches}
                now = datetime.now()
                next_available_spot = min(list(spots_and_departure_times.items()), key=lambda x: abs(x[1] - now))[0]
                return next_available_spot

    def check_if_stay_expired(self):
        with self.cnx.cursor() as cursor:
            selection_query = "SELECT spot_id, expected_departure_time FROM parked_vehicles_data WHERE has_expired = 0;"
            matches = self._selection_query(cursor, selection_query)
            if matches:
                now = datetime.now()
                spots_and_departure_times = {spot_id: expected_departure_time for spot_id, expected_departure_time
                                             in matches if now > expected_departure_time}
                for parking_spot in spots_and_departure_times.keys():
                    insertion_query = "UPDATE parked_vehicles_data SET has_expired = 1 WHERE spot_id = %s;"
                    self._insertion_query(cursor, insertion_query, filter_values=[parking_spot])
                self.cnx.commit()