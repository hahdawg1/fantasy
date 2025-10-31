"""Abstract base class for fetching player scores."""

from abc import ABC, abstractmethod
from typing import Protocol

from fantasy.models import Player, PlayerScore


class ScoreFetcher(Protocol):
    """
    Protocol for fetching player scores.

    Implement this protocol to provide score fetching from different sources
    (ESPN API, scraping, local data, etc.).
    """

    def fetch_player_score(
        self, player: Player, week: int, season_year: int | None = None
    ) -> PlayerScore | None:
        """
        Fetch a single player's score for a specific week.

        Args:
            player: The player to get the score for
            week: The week number (1-18 for NFL, 1-17 for some seasons)
            season_year: Optional season year (defaults to current season)

        Returns:
            PlayerScore object if found, None otherwise
        """
        ...

    def fetch_player_scores(
        self, players: list[Player], week: int, season_year: int | None = None
    ) -> list[PlayerScore]:
        """
        Fetch scores for multiple players for a specific week.

        Args:
            players: List of players to get scores for
            week: The week number
            season_year: Optional season year (defaults to current season)

        Returns:
            List of PlayerScore objects (may be fewer than input if some not found)
        """
        ...


class BaseScoreFetcher(ABC):
    """
    Abstract base class for score fetchers.

    Provides default implementation for fetch_player_scores that calls
    fetch_player_score for each player.
    """

    @abstractmethod
    def fetch_player_score(
        self, player: Player, week: int, season_year: int | None = None
    ) -> PlayerScore | None:
        """
        Fetch a single player's score for a specific week.

        Args:
            player: The player to get the score for
            week: The week number (1-18 for NFL, 1-17 for some seasons)
            season_year: Optional season year (defaults to current season)

        Returns:
            PlayerScore object if found, None otherwise
        """
        pass

    def fetch_player_scores(
        self, players: list[Player], week: int, season_year: int | None = None
    ) -> list[PlayerScore]:
        """
        Fetch scores for multiple players for a specific week.

        Args:
            players: List of players to get scores for
            week: The week number
            season_year: Optional season year (defaults to current season)

        Returns:
            List of PlayerScore objects (may be fewer than input if some not found)
        """
        scores = []
        for player in players:
            score = self.fetch_player_score(player, week, season_year)
            if score is not None:
                scores.append(score)
        return scores


class MockScoreFetcher(BaseScoreFetcher):
    """
    Mock score fetcher for testing.

    Returns random scores between 0 and 30 for each player.
    """

    def fetch_player_score(
        self, player: Player, week: int, season_year: int | None = None
    ) -> PlayerScore | None:
        """Return a mock score for testing."""
        import random

        # Use player hash for consistent "random" scores
        random.seed(hash((player.name, week, season_year or 2024)))
        score = round(random.uniform(0, 30), 2)

        return PlayerScore(
            player_name=player.name,
            position=player.position,
            team=player.team,
            week=week,
            score=score,
        )

