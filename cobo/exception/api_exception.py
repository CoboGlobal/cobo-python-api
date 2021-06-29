from dataclasses import dataclass


@dataclass(frozen=True)
class ApiException:
    errorCode: int
    errorMessage: str
    errorId: str
