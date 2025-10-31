"""Data models for fantasy scoring."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Player:
    """Represents a fantasy player."""

    name: str
    position: str
    team: str
    fantasy_team: str

    def __hash__(self) -> int:
        """Make Player hashable for use in sets/dicts."""
        return hash((self.name, self.position, self.team, self.fantasy_team))

    def __eq__(self, other: object) -> bool:
        """Compare players by all attributes."""
        if not isinstance(other, Player):
            return False
        return (
            self.name == other.name
            and self.position == other.position
            and self.team == other.team
            and self.fantasy_team == other.fantasy_team
        )


@dataclass
class PlayerScore:
    """Represents a player's score for a specific week."""

    player_name: str
    position: str
    team: str
    week: int
    score: float

    def __post_init__(self) -> None:
        """Validate score is non-negative."""
        if self.score < 0:
            raise ValueError("Score cannot be negative")


@dataclass
class TeamScore:
    """Represents a fantasy team's total score for a week."""

    fantasy_team: str
    week: int
    total_score: float
    player_scores: list[PlayerScore]

    def __post_init__(self) -> None:
        """Validate total score matches sum of player scores."""
        calculated_total = sum(ps.score for ps in self.player_scores)
        if abs(self.total_score - calculated_total) > 0.01:  # Allow small floating point differences
            raise ValueError(
                f"Total score {self.total_score} does not match sum of player scores {calculated_total}"
            )

