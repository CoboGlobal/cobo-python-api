from dataclasses import dataclass


@dataclass(frozen=True)
class ApiError:
    errorCode: int
    errorMessage: str
    errorId: str
