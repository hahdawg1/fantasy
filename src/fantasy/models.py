"""Data models for fantasy scoring."""

from dataclasses import dataclass


@dataclass
class Player:
    """Represents a fantasy player."""

    player_name: str
    player_team: str
    player_position: str
    fantasy_team: str

    def __hash__(self) -> int:
        """Make Player hashable for use in sets/dicts."""
        return hash(
            (self.player_name, self.player_team, self.player_position, self.fantasy_team)
        )

    def __eq__(self, other: object) -> bool:
        """Compare players by all attributes."""
        if not isinstance(other, Player):
            return False
        return (
            self.player_name == other.player_name
            and self.player_team == other.player_team
            and self.player_position == other.player_position
            and self.fantasy_team == other.fantasy_team
        )


@dataclass
class PlayerScore:
    """Represents a player's fantasy score for a specific week."""

    player_name: str
    player_team: str
    player_position: str
    week: int
    season: int
    fantasy_points: float

    def __post_init__(self) -> None:
        """Validate fantasy_points is non-negative."""
        if self.fantasy_points < 0:
            raise ValueError("Fantasy points cannot be negative")


@dataclass
class TeamScore:
    """Represents a fantasy team's total score for a week."""

    fantasy_team: str
    week: int
    season: int
    total_points: float
    player_scores: list[PlayerScore]

    def __post_init__(self) -> None:
        """Validate total_points matches sum of player scores."""
        calculated_total = sum(ps.fantasy_points for ps in self.player_scores)
        if abs(self.total_points - calculated_total) > 0.01:  # Allow small floating point differences
            raise ValueError(
                f"Total points {self.total_points} does not match sum of player scores {calculated_total}"
            )

