from datetime import datetime, timezone
from .base import BaseTool

class GetCurrentTimeTool(BaseTool):
    name = "get_current_time"
    description = "Returns the current date and time in UTC"

    def run(self, **kwargs) -> str:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%d %H:%M:%S UTC")