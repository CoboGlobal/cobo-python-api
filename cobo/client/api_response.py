from dataclasses import dataclass
from typing import Optional

from cobo.error.api_error import ApiError


@dataclass
class ApiResponse:
    success: bool
    result: Optional[dict]
    exception: Optional[ApiError]
