class NoStopDefinedException(Exception):
    """Exception raised for errors when setting stops and limits.

    message -- explanation of the error
    """

    def __init__(
        self, message: str = "cannot initiate a trade without any stops"
    ):
        self.message = message
        super().__init__(self.message)


class InvalidTradeParameter(Exception):
    """Exception raised for errors when setting stops and limits.

    message -- explanation of the error
    """

    def __init__(self, message: str = "invalid trading parameters"):
        self.message = message
        super().__init__(self.message)


class NoEconomicImpactDefined(Exception):
    """Exception raised for errors when no impact found.

    message -- explanation of the error
    """

    def __init__(self, message: str = "Cannot identify the impact"):
        self.message = message
        super().__init__(self.message)


class InvalidEventTypeException(Exception):
    """Exception raised for invalid event types.

    message -- explanation of the error
    """

    def __init__(self, message: str = "Invalid Event type"):
        self.message = message
        super().__init__(self.message)
