"""Data models for fantasy scoring."""

from dataclasses import dataclass


@dataclass
class Player:
    """
    Represents a fantasy player.

    Attributes
    ----------
    player_name : str
        Name of the player.
    player_team : str
        NFL team abbreviation the player belongs to.
    player_position : str
        Position of the player (e.g., QB, RB, WR, TE).
    fantasy_team : str
        Name of the fantasy team that owns this player.
    """

    player_name: str
    player_team: str
    player_position: str
    fantasy_team: str

    def __hash__(self) -> int:
        """
        Make Player hashable for use in sets/dicts.

        Returns
        -------
        int
            Hash value based on all player attributes.
        """
        return hash(
            (self.player_name, self.player_team, self.player_position, self.fantasy_team)
        )

    def __eq__(self, other: object) -> bool:
        """
        Compare players by all attributes.

        Parameters
        ----------
        other : object
            Object to compare with.

        Returns
        -------
        bool
            True if all attributes match, False otherwise.
        """
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
    """
    Represents a player's fantasy score for a specific week.

    Attributes
    ----------
    player_name : str
        Name of the player.
    player_team : str
        NFL team abbreviation the player belongs to.
    player_position : str
        Position of the player.
    week : int
        Week number.
    season : int
        Season year.
    fantasy_points : float
        Fantasy points scored by the player.

    Raises
    ------
    ValueError
        If fantasy_points is negative.
    """

    player_name: str
    player_team: str
    player_position: str
    week: int
    season: int
    fantasy_points: float

    def __post_init__(self) -> None:
        """
        Validate fantasy_points is non-negative.

        Raises
        ------
        ValueError
            If fantasy_points is less than 0.
        """
        if self.fantasy_points < 0:
            raise ValueError("Fantasy points cannot be negative")


@dataclass
class TeamScore:
    """
    Represents a fantasy team's total score for a week.

    Attributes
    ----------
    fantasy_team : str
        Name of the fantasy team.
    week : int
        Week number.
    season : int
        Season year.
    total_points : float
        Total fantasy points scored by the team.
    player_scores : list[PlayerScore]
        List of individual player scores for the team.

    Raises
    ------
    ValueError
        If total_points does not match the sum of player scores.
    """

    fantasy_team: str
    week: int
    season: int
    total_points: float
    player_scores: list[PlayerScore]

    def __post_init__(self) -> None:
        """
        Validate total_points matches sum of player scores.

        Raises
        ------
        ValueError
            If total_points does not match the sum of fantasy_points from
            player_scores (allowing for small floating point differences).
        """
        calculated_total = sum(ps.fantasy_points for ps in self.player_scores)
        if abs(self.total_points - calculated_total) > 0.01:  # Allow small floating point differences
            raise ValueError(
                f"Total points {self.total_points} does not match sum of player scores {calculated_total}"
            )

