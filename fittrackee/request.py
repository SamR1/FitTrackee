from typing import Optional, Tuple

from flask import Request
from ua_parser import user_agent_parser
from werkzeug.user_agent import UserAgent as IUserAgent


class UserAgent(IUserAgent):
    def __init__(self, string: str):
        super().__init__(string)
        self.platform, self.browser = self._parse_user_agent(self.string)

    @staticmethod
    def _parse_user_agent(
        user_agent: str,
    ) -> Tuple[Optional[str], Optional[str]]:
        parsed_string = user_agent_parser.Parse(user_agent)
        platform = parsed_string.get('os', {}).get('family')
        browser = parsed_string.get('user_agent', {}).get('family')
        return platform, browser


class CustomRequest(Request):
    user_agent_class = UserAgent
