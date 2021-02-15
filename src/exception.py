class WrongInputError(Exception):
    """
    Raised if func has wrong input
    """
    def __init__(self, value):
        self.value = str(value)
    def __str__(self):
        return "Wrong Input : " + self.value

class TimeError(Exception):
    """
    Raised if trade time is occured ealier than recent trade.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Time Error <Recent trade is occured earlier than now : " + self.value + ">"
    
