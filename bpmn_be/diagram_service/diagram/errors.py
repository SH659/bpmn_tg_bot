class BotNotFoundError(Exception):
    pass


class NoResponseError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message


class DiagramNotFoundError(Exception):
    pass
