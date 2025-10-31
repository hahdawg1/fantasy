"""CSV parser for fantasy team data."""

import pandas as pd
from pathlib import Path

from fantasy.models import Player


def parse_fantasy_csv(csv_path: str | Path) -> list[Player]:
    """
    Parse a CSV file with fantasy team data.

    Expected columns:
    - fantasy_team: Name of the fantasy team
    - player name: Name of the player
    - player position: Position of the player (e.g., QB, RB, WR, TE)
    - player team: NFL/NBA/etc. team the player belongs to

    Args:
        csv_path: Path to the CSV file

    Returns:
        List of Player objects

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If required columns are missing
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Read CSV with lenient parsing to handle malformed rows
    # on_bad_lines parameter was introduced in pandas 1.3.0
    try:
        df = pd.read_csv(csv_path, on_bad_lines="skip")
    except (TypeError, ValueError):
        # Older pandas versions (< 1.3.0) use error_bad_lines instead
        # This is deprecated but may still exist in older versions
        try:
            df = pd.read_csv(csv_path, error_bad_lines=False, warn_bad_lines=False)
        except TypeError:
            # Very old pandas or parameter doesn't exist, just read normally
            # dropna later will filter out bad rows
            df = pd.read_csv(csv_path)

    # Normalize column names (case-insensitive, strip whitespace)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    required_columns = ["fantasy_team", "player_name", "player_position", "player_team"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    # Try alternative column name formats
    column_mapping = {}
    for required in required_columns:
        if required not in df.columns:
            # Try without underscores
            alt_name = required.replace("_", "")
            if alt_name in df.columns:
                column_mapping[required] = alt_name
            else:
                # Try with spaces
                alt_name = required.replace("_", " ")
                if alt_name in df.columns:
                    column_mapping[required] = alt_name

    if column_mapping:
        df = df.rename(columns=column_mapping)

    # Re-check for missing columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            f"Found columns: {list(df.columns)}"
        )

    # Remove rows with missing values
    df = df.dropna(subset=required_columns)

    players = []
    for _, row in df.iterrows():
        player = Player(
            name=str(row["player_name"]).strip(),
            position=str(row["player_position"]).strip().upper(),
            team=str(row["player_team"]).strip(),
            fantasy_team=str(row["fantasy_team"]).strip(),
        )
        players.append(player)

    return players

