import security

class User:
    def __init__(self, pin, username):
        self.derived_key = security.calculate_key(pin)
        self.username = username
        self.notes = []
        self.pin_tip = "Your pin is: " + pin