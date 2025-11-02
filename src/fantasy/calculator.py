"""Calculate fantasy team scores."""

from collections import defaultdict
from typing import Iterable

from fantasy.models import Player, PlayerScore, TeamScore
from fantasy.score_fetcher import ScoreFetcher


def calculate_team_scores(
    players: list[Player],
    week: int,
    score_fetcher: ScoreFetcher,
    season_year: int | None = None,
) -> list[TeamScore]:
    """
    Calculate scores for all fantasy teams for a given week.

    Args:
        players: List of all players across all fantasy teams
        week: Week number to calculate scores for
        score_fetcher: ScoreFetcher implementation to get player scores
        season_year: Optional season year

    Returns:
        List of TeamScore objects, one per fantasy team

    Raises:
        ValueError: If a player's score cannot be found by the score fetcher
    """
    # Group players by fantasy team
    teams_dict: dict[str, list[Player]] = defaultdict(list)
    for player in players:
        teams_dict[player.fantasy_team].append(player)

    # Fetch scores for all players
    all_scores = score_fetcher.fetch_player_scores(players, week, season_year)

    # Helper function to normalize keys for matching (case-insensitive)
    def normalize_key(name: str, position: str, team: str) -> tuple[str, str, str]:
        """Normalize player key for matching."""
        return (name.lower().strip(), position.upper().strip(), team.upper().strip())

    # Group scores by player name, position, team (for matching)
    # Use normalized keys to handle team abbreviation variations (KC vs KAN, etc.)
    score_lookup: dict[tuple[str, str, str], PlayerScore] = {}
    for score in all_scores:
        key = normalize_key(score.player_name, score.position, score.team)
        score_lookup[key] = score

    # Calculate team scores
    team_scores = []
    for fantasy_team, team_players in teams_dict.items():
        player_scores = []
        for player in team_players:
            # Try to find matching score using normalized key
            key = normalize_key(player.name, player.position, player.team)
            score = score_lookup.get(key)
            
            # If not found with exact match, try matching just by name and position
            # (in case team abbreviations differ)
            if score is None:
                for lookup_key, lookup_score in score_lookup.items():
                    if (
                        lookup_key[0] == key[0]  # name matches
                        and lookup_key[1] == key[1]  # position matches
                    ):
                        score = lookup_score
                        break

            if score is None:
                # Player score not found, raise an error
                raise ValueError(
                    f"Could not find score for player: {player.name} "
                    f"({player.position}, {player.team}) on {fantasy_team} for week {week}"
                )

            player_scores.append(score)

        total_score = sum(ps.score for ps in player_scores)

        team_score = TeamScore(
            fantasy_team=fantasy_team,
            week=week,
            total_score=round(total_score, 2),
            player_scores=player_scores,
        )
        team_scores.append(team_score)

    # Sort by total score (descending)
    team_scores.sort(key=lambda ts: ts.total_score, reverse=True)

    return team_scores


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
        lines.append(f"\n{team_score.fantasy_team} - Week {team_score.week}")
        lines.append(f"  Total Score: {team_score.total_score}")
        lines.append("  Player Scores:")
        for ps in team_score.player_scores:
            lines.append(f"    {ps.player_name} ({ps.position}, {ps.team}): {ps.score}")
    return "\n".join(lines)

