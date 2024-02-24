

class InvalidModuleError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class CallableTypeError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
