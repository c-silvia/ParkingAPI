from flask import Flask, request, redirect, url_for, session, make_response
from datetime import timedelta
import json, os, atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask_bcrypt import Bcrypt
from db import *  # update
from auth import *  # update
from exceptions import NoSpotsAvailable, InvalidPlateNumber, LicensePlateNotFound, AllSpotsAvailable, \
    InvalidSpotNumber, SpotNotAvailable, VehicleAlreadyInOtherSpot, UserNotFound, InvalidLengthOfStay, \
    TooLong, MissingData, UsernameAlreadyUsed, EmailAlreadyUsed, InvalidUsername, InvalidEmail, InvalidPassword

app = Flask(__name__)

bcrypt = Bcrypt(app)
app.secret_key = os.getenv("SECRET_KEY")


def parking_expiration_checker():
    db_data = DBData()
    db_data.check_if_stay_expired()


scheduler = BackgroundScheduler()
scheduler.add_job(func=parking_expiration_checker, trigger="interval", seconds=60)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


# login_manager = LoginManager()
# login_manager.init_app(app)


# upper or lower everything

def check_session(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("login_success") or not session.get("username"):
            return "Please log in to continue.", 403  # Forbidden
        # if not request.cookies.get("LoginCookie", None):
        #     return "Please log in to continue.", 403
        return function(*args, **kwargs)

    return wrapper


@app.route('/')
def index():
    return "Welcome to this parking app!"


# hide password when typed
@app.route('/register', methods=["GET", "POST"])
def create_user():
    incoming_data = request.get_json()
    db_users = DBUsers()
    try:
        username = incoming_data["username"]
        email_address = incoming_data["email_address"]
        password = incoming_data["password"]
        db_users.check_registration_input(username, email_address, password)
        db_users.create_user(username, email_address, bcrypt.generate_password_hash(password))
        return "User successfully created.", 200  # OK
    except MissingData:
        return "Missing data.", 400  # Bad request
    except UsernameAlreadyUsed:
        return "This username is already linked to an existing user.", 403  # Forbidden
    except EmailAlreadyUsed:
        return "This email address is already linked to an existing user.", 403  # Forbidden
    except InvalidUsername:
        return "Username must contain characters and/or numbers.", 400  # Bad request
    except InvalidEmail:
        return "Invalid email address entered.", 400  # Bad request
    except InvalidPassword:
        return "Password must be between 8 and 10 characters, must contain at least one uppercase letter, " \
               "one lowercase letter, one number and one special character.", 400  # Bad request


# if logged in don't do it again
@app.route('/log-in', methods=["GET", "POST"])
def log_in():
    incoming_data = request.get_json()
    db_users = DBUsers()
    try:
        username = incoming_data["username"]
        password = incoming_data["password"]
        user_data = db_users.get_user_data_from_username(username)
        if bcrypt.check_password_hash(user_data["password"], password):
            session["login_success"] = True
            session["username"] = username  # what if multiple users are logged in
            # response = make_response("Successfully logged in.", 200)
            # response.set_cookie("LoginCookie", username, secure=True, httponly=True)
            # return response  # OK
            return "Successfully logged in.", 200
    except KeyError:
        return "Missing data.", 404  # Not found
    except UserNotFound:  # expand
        return "User not found.", 404  # Not found
    except ValueError:
        return "Incorrect password entered.", 400  # Bad Request


@app.route('/log-out')
@check_session
def log_out():
    session.pop("login_success", None)
    session.pop("username", None)
    # response = make_response("Successfully logged out.", 200)
    # response.set_cookie("LoginCookie", "", expires=0, httponly=True, secure=True)
    # return response
    return "Successfully logged out.", 200  # OK


@app.route('/search-license-plate', methods=["POST"])
@check_session
def search_license_plate():
    incoming_data = request.get_json()
    db_data = DBData()
    try:
        parking_spot = db_data.get_spot_from_plate(incoming_data["license_plate"])
        return parking_spot, 200  # OK
    except InvalidPlateNumber:
        return "This is not a valid license plate number.", 400  # Bad Request
    except LicensePlateNotFound:
        return "There are no vehicles with this license plate number currently parked in the parking lot.", 404
        # Not found


@app.route('/vacant-spots', methods=["GET"])
@check_session
def retrieve_vacant_spots():
    db_data = DBData()
    try:
        vacant_spots = db_data.get_vacant_spots()
        return vacant_spots, 200  # OK
    except NoSpotsAvailable:
        return "There are no spots available at the moment.", 404  # Not found


@app.route('/vacant-spots-count', methods=["GET"])
@check_session
def retrieve_vacant_spots_count():
    db_data = DBData()
    try:
        vacant_spots_count = db_data.get_vacant_spots_count()
        return vacant_spots_count, 200  # OK
    except NoSpotsAvailable:
        return "There are no spots available at the moment.", 404  # Not found


@app.route('/unavailable-spots', methods=["GET"])
@check_session
def retrieve_unavailable_spots_and_plates():
    db_data = DBData()
    try:
        unavailable_spots_and_plates = db_data.get_unavailable_spots_and_plates()
        return unavailable_spots_and_plates, 200  # OK
    except AllSpotsAvailable:
        return "All parking spots are currently available", 404  # Not found


# check if single spot is available
@app.route('/park-car', methods=["POST"])
@check_session
def park_car():
    incoming_data = request.get_json()
    db_data = DBData()
    try:
        parking_spot = incoming_data["parking_spot"]
        license_plate = incoming_data["license_plate"]
        length_of_stay = incoming_data["length_of_stay"]
        round_length_of_stay = db_data.check_incoming_values_before_parking(parking_spot, license_plate, length_of_stay)
        # make function
        arrival_time = datetime.now()
        length_of_stay_hours, length_of_stay_minutes = round_length_of_stay.split(".")
        selected_length_of_stay = timedelta(hours=int(length_of_stay_hours), minutes=int(length_of_stay_minutes))
        departure_time = arrival_time + selected_length_of_stay
        db_data.park_car(parking_spot, license_plate)
        db_data.store_parking_time(license_plate, arrival_time, round_length_of_stay, departure_time, parking_spot, 0,
                                   None, 0)
        confirmed_spot = db_data.get_spot_from_plate(incoming_data["license_plate"])
        return confirmed_spot
    except KeyError:
        return "Missing data.", 400  # Bad Request
    except InvalidSpotNumber:
        return "This is not a valid parking spot number.", 400  # Bad Request
    except SpotNotAvailable:
        return "The selected spot is currently not available.", 403  # Forbidden
    except InvalidPlateNumber:
        return "This is not a valid license plate number.", 400  # Bad Request
    except VehicleAlreadyInOtherSpot:
        return "This license plate is already linked to another parking spot currently in use.", 403  # Forbidden
    except InvalidLengthOfStay:
        return "Invalid length of stay entered.", 400  # Bad Request
    except TooLong:
        return "A vehicle cannot occupy a spot for longer than a year.", 400  # Forbidden


@app.route('/leave-parking-spot', methods=["POST"])
@check_session
def leave_parking_spot():
    incoming_data = request.get_json()
    db_data = DBData()
    try:
        db_data.leave_parking_spot(incoming_data["license_plate"])
        return "Parking spot now available.", 200  # OK
    except InvalidPlateNumber:
        return "This is not a valid license plate number.", 400  # Bad Request
    except LicensePlateNotFound:
        return "There are no vehicles with this license plate number currently parked in the parking lot.", 404
        # Not found


@app.route('/next-available-spot', methods=["GET"])
@check_session
def check_next_available_spot():
    db_data = DBData()
    db_data.get_next_available_spot()
    return db_data.get_next_available_spot(), 200  # OK


if __name__ == '__main__':
    app.run(debug=True, port=5000)
