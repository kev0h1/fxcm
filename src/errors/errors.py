class NoStopDefinedException(Exception):
    """Exception raised for errors when setting stops and limits.

    message -- explanation of the error
    """

    def __init__(
        self, message: str = "cannot initiate a trade without any stops"
    ):
        self.message = message
        super().__init__(self.message)
