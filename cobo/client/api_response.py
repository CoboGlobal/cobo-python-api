from dataclasses import dataclass
from typing import Optional, Union

from cobo.exception.api_exception import ApiException


@dataclass
class ApiResponse:
    success: bool
    result: Optional[dict]
    exception: Optional[ApiException]
