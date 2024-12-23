# app/external_services/github_api.py



import logging
from app.core.logging_config import *
import httpx
from app.core.config import settings
from app.core.exceptions import NotFoundError, ExternalAPIError


# GET https://api.github.com/users/{username}/repos

"""
Github Docs:

Unauthenticated Rate Limit:
The primary rate limit for unauthenticated requests is 60 requests per hour.

Authenticated Rate Limit:
5000 requests per hour
"""


logger = logging.getLogger(__name__)


class GitHubAPIClient:

    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
        } # we need json response
        # if settings.GITHUB_API_TOKEN: # if there is any token specified
        #     self.headers["Authorization"] = f"token {settings.GITHUB_API_TOKEN}"
        self.client = httpx.AsyncClient(headers=self.headers, base_url=self.base_url)

    async def fetch_user_projects(self, username: str):
        """
        Fetches public (Private ?) repositories for the specified GitHub username.
        """
        url = f"/users/{username}/repos"
        try:
            logger.info(f"Fetching projects for user '{username}' from GitHub API.")
            response = await self.client.get(url)
            # raise an exception if the response status code is not 200
            response.raise_for_status()
            projects_data = response.json()
            return projects_data
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 404:
                logger.warning(f"GitHub user '{username}' not found. Status code: {status_code}")
                # return [] # raise NotFoundError(f"User '{username}' not found on Github.")
                raise NotFoundError(f"User '{username}' not found on Github.")
            else:
                logger.error(f"HTTP error occurred: {e}. Status code: {status_code}")
                raise ExternalAPIError("Error fetching projects from GitHub.")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            raise ExternalAPIError("Error fetching projects from GitHub.")

    async def close(self):
        await self.client.aclose()

