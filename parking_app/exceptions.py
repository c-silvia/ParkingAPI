class DbConnectionError(Exception):
    pass


class LicensePlateNotFound(Exception):
    pass


class NoSpotsAvailable(Exception):
    pass


class AllSpotsAvailable(Exception):
    pass


class SpotNotAvailable(Exception):
    pass


class InvalidPlateNumber(Exception):
    pass


class VehicleAlreadyInOtherSpot(Exception):
    pass


class InvalidSpotNumber(Exception):
    pass


class UserNotFound(Exception):
    pass


class NotLoggedIn(Exception):
    pass


class IncorrectPassword(Exception):
    pass
