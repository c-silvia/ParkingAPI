# Install

To run this application, create a new virtual environment in PyCharm and install the packages in the requirements.txt file:

`pip install -r requirements`

In your PyCharm configuration, set the following:

**Script path:** `[PROJECT_ROOT]\parking_app\main.py`

**Working directory:** `[PROJECT_ROOT]\parking_app`

**Environment variables:**

`PYTHONUNBUFFERED=1;DATABASE_DB=parking_app;DATABASE_HOST=localhost;DATABASE_PASSWORD=YourOwnPassword;DATABASE_USER=root;SECRET_KEY=YourOwnSecretKey`

If you'd like to run the application from the command line, make sure to export the PYTHONPATH to the root of the repository.

# Database

**Database:** Create the `parking_app` database by executing the script available at `resources\parking_app.sql` in your MySQL Workbench.

# **Running and interacting with the application**

Proceed to run the application by executing the `main.py` file. 

To interact with the app, execute `curl` commands in the terminal. For instance:

**Create a new user**:

`curl -b cookies.txt -X POST -H "Content-Type: application/json" localhost:5000/register -d '{"username": "appuser", "email_address": "appuser@test.dummy.com", "password": "S7r0ngPW!"}'`

**Log in:**

`curl -c cookies.txt -X POST -H "Content-Type: application/json" localhost:5000/log-in -d '{"username": "appuser", "password": "S7r0ngPW!"}'`

**Look up a license plate to retrieve the parking spot where the related vehicle is parked:**

`curl -b cookies.txt -X POST -H "Content-Type: application/json" localhost:5000/search-license-plate -d '{"license_plate":"F-130-AE"}'`

**View all available spots:**

`curl -b cookies.txt localhost:5000/vacant-spots`

**View how many available spots there are:**

`curl -b cookies.txt localhost:5000/vacant-spots-count`

**View which spots are unavailable and which license plates are linked to them:**

`curl -b cookies.txt localhost:5000/unavailable-spots`

**View which one spot is directly available (if one or more spots are directly available) or will first become available as soon as the vehicle occupying it has left (if no spots are directly available):**

`curl -b cookies.txt localhost:5000/next-available-spot`

**Park a vehicle:**

`curl -b cookies.txt -X POST -H "Content-Type: application/json" localhost:5000/park-car -d '{"parking_spot":"A48","license_plate":"L-713-KQ", "length_of_stay": "1.23"}'`

**Park a vehicle at the next available spot without having to specify the spot number:**

Please note: should no spots be available, an error message will be returned, with information on which spot will become available next.

`curl -b cookies.txt -X POST -H "Content-Type: application/json" localhost:5000/park-at-next-available-spot -d '{"license_plate":"N-184-NS", "length_of_stay": "4.55"}'`

**Leave a parking spot:**

`curl -b cookies.txt -X POST -H "Content-Type: application/json" localhost:5000/leave-parking-spot -d '{"license_plate":"K-452-BM"}'`

**Log out:**

`curl -c cookies.txt -b cookies.txt localhost:5000/log-out`

**Attempt accessing an endpoint when not logged in/after logging out:**

`curl -b cookies.txt localhost:5000/next-available-spot`

# Running tests

To run the tests available at `[PROJECT_ROOT]\tests`, export the PYTHONPATH to the root of the repository first, then from the root directory run the following:

`pytest tests`

