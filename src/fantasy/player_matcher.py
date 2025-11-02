"""Utility for matching player names from CSV to nflreadpy data."""

import re
from typing import Optional

import pandas as pd


def normalize_name(name: str) -> str:
    """
    Normalize a player name for matching.

    Removes common suffixes, converts to lowercase, and strips whitespace.
    Handles abbreviated names like "J.Love" by replacing periods with spaces.

    Args:
        name: Player name to normalize

    Returns:
        Normalized name
    """
    name = str(name).strip()
    # Remove common suffixes (Jr., Sr., II, III, IV, etc.)
    name = re.sub(r'\s+(Jr\.?|Sr\.?|II|III|IV|V)$', '', name, flags=re.IGNORECASE)
    # Replace periods followed by capitals (like "J.Love" or "J. Love") with spaces
    # This helps match abbreviated names
    name = re.sub(r'\.([A-Z])', r' \1', name)
    name = re.sub(r'\.', ' ', name)  # Replace any remaining periods with spaces
    # Convert to lowercase and strip
    return name.lower().strip()


def fuzzy_match_name(csv_name: str, api_name: str, threshold: float = 0.8) -> bool:
    """
    Perform fuzzy matching between two player names.

    Uses simple heuristics for name matching:
    - Exact normalized match
    - One name contains the other
    - First and last name match (in any order)

    Args:
        csv_name: Name from CSV
        api_name: Name from API
        threshold: Similarity threshold (currently unused, for future expansion)

    Returns:
        True if names likely match, False otherwise
    """
    csv_normalized = normalize_name(csv_name)
    api_normalized = normalize_name(api_name)

    # Exact match
    if csv_normalized == api_normalized:
        return True

    # One contains the other (handles nicknames or extra words)
    if csv_normalized in api_normalized or api_normalized in csv_normalized:
        return True

    # Split into words and check if all words from shorter name are in longer name
    csv_words = csv_normalized.split()
    api_words = api_normalized.split()

    if not csv_words or not api_words:
        return False

    # Handle initials (e.g., "P. Mahomes" should match "Patrick Mahomes")
    # Remove single characters and single characters with periods (initials)
    # but keep numbers
    def is_initial(word: str) -> bool:
        """Check if a word is likely an initial."""
        # Remove periods and check if it's a single character
        word_clean = word.strip(".")
        return len(word_clean) == 1 and not word_clean.isdigit()

    csv_non_initials = [w for w in csv_words if not is_initial(w)]
    api_non_initials = [w for w in api_words if not is_initial(w)]

    # Check if all non-initial words from one name appear in the other
    # This handles cases like "P. Mahomes" vs "Patrick Mahomes" or "J.Love" vs "Jordan Love"
    if csv_non_initials and api_non_initials:
        csv_set = set(csv_non_initials)
        api_set = set(api_non_initials)
        # If one set is a subset of the other, it's a match
        # (e.g., {"mahomes"} is subset of {"patrick", "mahomes"})
        # (e.g., {"love"} is subset of {"jordan", "love"})
        if csv_set.issubset(api_set) or api_set.issubset(csv_set):
            return True
        # Also check if they share at least the last name
        if csv_non_initials and api_non_initials:
            if csv_non_initials[-1] == api_non_initials[-1]:
                # Last names match, this is likely the same player
                return True

    # Check if last names match when one has an initial
    # This handles "P. Mahomes" vs "Patrick Mahomes" where both end with "Mahomes"
    csv_meaningful = csv_non_initials if csv_non_initials else csv_words
    api_meaningful = api_non_initials if api_non_initials else api_words

    # If both have at least one meaningful word, check if last names match
    if csv_meaningful and api_meaningful:
        # Last meaningful word (usually the last name)
        if csv_meaningful[-1] == api_meaningful[-1]:
            # If one name has only one word (initial + last name), match by last name
            if len(csv_meaningful) == 1 or len(api_meaningful) == 1:
                return True
            # If both have multiple words, require first and last to match
            if len(csv_meaningful) >= 2 and len(api_meaningful) >= 2:
                csv_first_last = {csv_meaningful[0], csv_meaningful[-1]}
                api_first_last = {api_meaningful[0], api_meaningful[-1]}
                if csv_first_last == api_first_last:
                    return True

    return False


def find_player_match(
    csv_player_name: str,
    csv_player_position: str,
    csv_player_team: str,
    player_stats_df: pd.DataFrame,
    strict_team_match: bool = False,
) -> Optional[pd.Series]:
    """
    Find a matching player in the nflreadpy stats DataFrame.

    Args:
        csv_player_name: Player name from CSV
        csv_player_position: Player position from CSV
        csv_player_team: Player team abbreviation from CSV
        player_stats_df: DataFrame from nflreadpy with player stats
        strict_team_match: If True, requires exact team match. If False, tries team match first,
                          then falls back to name+position only.

    Returns:
        Series with the matched player's stats, or None if no match found
    """
    csv_position = csv_player_position.upper().strip()
    csv_team = csv_player_team.upper().strip()

    # Normalize CSV name
    csv_normalized = normalize_name(csv_player_name)

    # Filter by position first (required)
    position_matches = player_stats_df[
        player_stats_df["position"].str.upper().str.strip() == csv_position
    ].copy()

    if position_matches.empty:
        return None

    # Try exact team match first
    team_column = "recent_team" if "recent_team" in position_matches.columns else "team"
    if team_column in position_matches.columns:
        exact_team_matches = position_matches[
            position_matches[team_column].str.upper().str.strip() == csv_team
        ]

        # Try fuzzy name matching within exact team matches
        for idx, row in exact_team_matches.iterrows():
            api_name = str(row.get("player_name", ""))
            if fuzzy_match_name(csv_player_name, api_name):
                return row

        # If strict_team_match is False, fall back to name+position only
        if not strict_team_match:
            # Try fuzzy matching on all position matches (ignoring team)
            for idx, row in position_matches.iterrows():
                api_name = str(row.get("player_name", ""))
                if fuzzy_match_name(csv_player_name, api_name):
                    return row

    else:
        # No team column, just match by name and position
        for idx, row in position_matches.iterrows():
            api_name = str(row.get("player_name", ""))
            if fuzzy_match_name(csv_player_name, api_name):
                return row

    return None


def find_players_in_stats(
    csv_players: list[tuple[str, str, str]],
    player_stats_df: pd.DataFrame,
    strict_team_match: bool = False,
) -> dict[tuple[str, str, str], pd.Series]:
    """
    Find multiple players in the stats DataFrame.

    Args:
        csv_players: List of tuples (player_name, player_position, player_team) from CSV
        player_stats_df: DataFrame from nflreadpy with player stats
        strict_team_match: If True, requires exact team match for all players

    Returns:
        Dictionary mapping (player_name, player_position, player_team) to matched Series
    """
    matches = {}
    for player_name, player_position, player_team in csv_players:
        match = find_player_match(
            player_name, player_position, player_team, player_stats_df, strict_team_match
        )
        if match is not None:
            matches[(player_name, player_position, player_team)] = match

    return matches

