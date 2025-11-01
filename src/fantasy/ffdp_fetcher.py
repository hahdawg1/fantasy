"""Fantasy Football Data Pros (FFDP) API score fetcher."""

import time
from typing import Optional
from datetime import datetime

import requests

from fantasy.models import Player, PlayerScore
from fantasy.score_fetcher import BaseScoreFetcher


class FFDPFetcher(BaseScoreFetcher):
    """
    Score fetcher using the Fantasy Football Data Pros API.

    API endpoint: https://www.fantasyfootballdatapros.com/api/players/{year}/{week}
    """

    BASE_URL = "https://www.fantasyfootballdatapros.com/api/players"

    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Initialize the FFDP fetcher.

        Args:
            rate_limit_delay: Delay in seconds between API requests to avoid rate limiting
        """
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0
        self._cache: dict[tuple[int, int], list[dict]] = {}

    def _rate_limit(self) -> None:
        """Ensure we don't make requests too quickly."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self._last_request_time = time.time()

    def _fetch_week_data(self, week: int, season_year: int) -> list[dict]:
        """
        Fetch all player data for a specific week from FFDP API.

        Args:
            week: Week number
            season_year: Season year

        Returns:
            List of player data dictionaries from the API

        Raises:
            requests.RequestException: If the API request fails
        """
        cache_key = (season_year, week)
        if cache_key in self._cache:
            return self._cache[cache_key]

        self._rate_limit()

        url = f"{self.BASE_URL}/{season_year}/{week}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to fetch data from FFDP API for {season_year} week {week}: {e}"
            ) from e

        # Cache the response
        self._cache[cache_key] = data

        return data

    def _normalize_name(self, name: str) -> str:
        """
        Normalize player name for matching.

        Args:
            name: Player name to normalize

        Returns:
            Normalized name (lowercase, stripped)
        """
        return name.lower().strip()

    def _normalize_team(self, team: str) -> str:
        """
        Normalize team abbreviation for matching.

        Args:
            team: Team abbreviation to normalize

        Returns:
            Normalized team abbreviation (uppercase, stripped)
        """
        return team.upper().strip()

    def _normalize_position(self, position: str) -> str:
        """
        Normalize position for matching.

        Args:
            position: Position to normalize

        Returns:
            Normalized position (uppercase, stripped)
        """
        return position.upper().strip()

    def _find_player_in_data(
        self, player: Player, week_data: list[dict]
    ) -> Optional[dict]:
        """
        Find a player in the week data.

        Args:
            player: Player to find
            week_data: List of player data from API

        Returns:
            Player data dictionary if found, None otherwise
        """
        normalized_name = self._normalize_name(player.name)
        normalized_team = self._normalize_team(player.team)
        normalized_position = self._normalize_position(player.position)

        for player_data in week_data:
            # Try to match by name, team, and position
            api_name = self._normalize_name(player_data.get("player_name", ""))
            api_team = self._normalize_team(player_data.get("team", ""))
            api_position = self._normalize_position(player_data.get("position", ""))

            # Match name (exact or partial) and team
            if (
                normalized_name in api_name or api_name in normalized_name
            ) and normalized_team == api_team:
                # If position matches, definitely use it
                if normalized_position == api_position:
                    return player_data
                # If no position specified in our data, still match by name/team
                if not player.position:
                    return player_data

        # Try again with just name and team (position might be different format)
        for player_data in week_data:
            api_name = self._normalize_name(player_data.get("player_name", ""))
            api_team = self._normalize_team(player_data.get("team", ""))

            if (
                normalized_name in api_name or api_name in normalized_name
            ) and normalized_team == api_team:
                return player_data

        return None

    def fetch_player_score(
        self, player: Player, week: int, season_year: Optional[int] = None
    ) -> Optional[PlayerScore]:
        """
        Fetch a single player's score from FFDP API.

        Args:
            player: The player to get the score for
            week: The week number (1-18 for NFL)
            season_year: Season year (defaults to current year if not provided)

        Returns:
            PlayerScore object if found, None otherwise
        """
        if season_year is None:
            season_year = datetime.now().year

        try:
            week_data = self._fetch_week_data(week, season_year)
        except requests.RequestException:
            # Return None if API call fails - let calculator raise error
            return None

        player_data = self._find_player_in_data(player, week_data)

        if player_data is None:
            return None

        # Extract fantasy score from API response
        # FFDP API typically uses 'fantasy_points' or 'pts' field
        score = None
        for field in ["fantasy_points", "pts", "points", "fantasy_pts", "score"]:
            if field in player_data:
                score_value = player_data[field]
                try:
                    score = float(score_value)
                    break
                except (ValueError, TypeError):
                    continue

        if score is None:
            # Couldn't find score field
            return None

        # Get position and team from API data or use from player
        position = player_data.get("position", player.position)
        team = player_data.get("team", player.team)
        player_name = player_data.get("player_name", player.name)

        return PlayerScore(
            player_name=player_name,
            position=position.upper(),
            team=team.upper(),
            week=week,
            score=round(score, 2),
        )

