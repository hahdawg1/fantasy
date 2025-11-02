"""Calculate fantasy team scores using nflreadpy."""

from collections import defaultdict
from typing import Iterable

import nflreadpy as nfl
import polars as pl

from fantasy.models import Player, PlayerScore, TeamScore
from fantasy.player_matcher import find_player_match


def calculate_week_score(
    players: list[Player],
    week: int,
    season: int,
) -> list[TeamScore]:
    """
    Calculate fantasy scores for all fantasy teams for a given week.

    Uses nflreadpy to load player stats and calculates standard fantasy points:
    - QB: 1 point per 25 passing yards, 4 points per passing TD, -2 per INT, 1 point per 10 rushing yards, 6 points per rushing TD
    - RB/WR/TE: 1 point per 10 rushing/receiving yards, 6 points per TD, 0.5 points per reception (half-PPR)

    Args:
        players: List of all players across all fantasy teams
        week: Week number to calculate scores for
        season: Season year

    Returns:
        List of TeamScore objects, one per fantasy team

    Raises:
        ValueError: If a player's score cannot be found for the specified week
    """
    # Load player stats for the specified week and season
    try:
        player_stats = nfl.load_player_stats(seasons=[season])
    except Exception as e:
        raise ValueError(f"Failed to load player stats from nflreadpy: {e}") from e

    # Convert to pandas if needed (nflreadpy uses Polars)
    if isinstance(player_stats, pl.DataFrame):
        player_stats = player_stats.to_pandas()

    # Check if DataFrame is empty or missing required columns
    if player_stats.empty:
        raise ValueError(f"No player stats found for season {season}, week {week}")

    # Check if required columns exist
    required_columns = ["season", "week"]
    missing_columns = [col for col in required_columns if col not in player_stats.columns]
    if missing_columns:
        raise ValueError(
            f"Player stats DataFrame missing required columns: {missing_columns}"
        )

    # Filter to the specific week
    week_stats = player_stats[
        (player_stats["season"] == season) & (player_stats["week"] == week)
    ].copy()

    if week_stats.empty:
        raise ValueError(f"No player stats found for season {season}, week {week}")

    # Group players by fantasy team
    teams_dict: dict[str, list[Player]] = defaultdict(list)
    for player in players:
        teams_dict[player.fantasy_team].append(player)

    # Calculate team scores using player matcher
    team_scores = []
    for fantasy_team, team_players in teams_dict.items():
        player_scores = []
        for player in team_players:
            # Use player matcher to find the player in the stats
            matched_player = find_player_match(
                player.player_name,
                player.player_position,
                player.player_team,
                week_stats,
                strict_team_match=False,
            )

            if matched_player is None:
                raise ValueError(
                    f"Could not find score for player: {player.player_name} "
                    f"({player.player_position}, {player.player_team}) on {fantasy_team} "
                    f"for {season} week {week}"
                )

            # Extract player info from matched row
            api_player_name = str(matched_player.get("player_name", player.player_name))
            api_player_team = str(
                matched_player.get("recent_team", matched_player.get("team", player.player_team))
            )
            api_player_position = str(
                matched_player.get("position", player.player_position)
            )

            # Calculate fantasy points
            fantasy_points = calculate_player_fantasy_points(matched_player, api_player_position)

            player_score = PlayerScore(
                player_name=api_player_name,
                player_team=api_player_team.upper(),
                player_position=api_player_position.upper(),
                week=week,
                season=season,
                fantasy_points=round(fantasy_points, 2),
            )

            player_scores.append(player_score)

        total_points = sum(ps.fantasy_points for ps in player_scores)

        team_score = TeamScore(
            fantasy_team=fantasy_team,
            week=week,
            season=season,
            total_points=round(total_points, 2),
            player_scores=player_scores,
        )
        team_scores.append(team_score)

    # Sort by total points (descending)
    team_scores.sort(key=lambda ts: ts.total_points, reverse=True)

    return team_scores


def calculate_player_fantasy_points(player_row: dict, position: str) -> float:
    """
    Calculate fantasy points for a player based on their stats.

    Scoring:
    - QB: 1 pt per 25 passing yards, 4 pts per passing TD, -2 per INT,
          1 pt per 10 rushing yards, 6 pts per rushing TD
    - RB/WR/TE: 1 pt per 10 rushing/receiving yards, 6 pts per TD,
                0.5 pts per reception (half-PPR)

    Args:
        player_row: Row from nflreadpy player stats DataFrame
        position: Player position

    Returns:
        Fantasy points total
    """
    position = position.upper()

    points = 0.0

    if position == "QB":
        # Passing stats
        passing_yards = float(player_row.get("passing_yards", 0) or 0)
        passing_tds = float(player_row.get("passing_tds", 0) or 0)
        interceptions = float(player_row.get("interceptions", 0) or 0)

        points += passing_yards / 25.0
        points += passing_tds * 4.0
        points -= interceptions * 2.0

        # Rushing stats for QB
        rushing_yards = float(player_row.get("rushing_yards", 0) or 0)
        rushing_tds = float(player_row.get("rushing_tds", 0) or 0)

        points += rushing_yards / 10.0
        points += rushing_tds * 6.0

    else:  # RB, WR, TE, etc.
        # Rushing stats
        rushing_yards = float(player_row.get("rushing_yards", 0) or 0)
        rushing_tds = float(player_row.get("rushing_tds", 0) or 0)

        points += rushing_yards / 10.0
        points += rushing_tds * 6.0

        # Receiving stats
        receiving_yards = float(player_row.get("receiving_yards", 0) or 0)
        receiving_tds = float(player_row.get("receiving_tds", 0) or 0)
        receptions = float(player_row.get("receptions", 0) or 0)

        points += receiving_yards / 10.0
        points += receiving_tds * 6.0
        points += receptions * 0.5  # Half-PPR

    return points


def format_team_scores(team_scores: Iterable[TeamScore]) -> str:
    """
    Format team scores as a human-readable string.

    Args:
        team_scores: Iterable of TeamScore objects

    Returns:
        Formatted string with team scores
    """
    lines = []
    for team_score in team_scores:
        lines.append(
            f"\n{team_score.fantasy_team} - {team_score.season} Week {team_score.week}"
        )
        lines.append(f"  Total Points: {team_score.total_points}")
        lines.append("  Player Scores:")
        for ps in team_score.player_scores:
            lines.append(
                f"    {ps.player_name} ({ps.player_position}, {ps.player_team}): {ps.fantasy_points}"
            )
    return "\n".join(lines)

