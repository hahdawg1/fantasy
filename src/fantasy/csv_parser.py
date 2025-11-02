"""CSV parser for fantasy team data."""

import pandas as pd
from pathlib import Path

from fantasy.models import Player


def parse_fantasy_csv(csv_path: str | Path) -> list[Player]:
    """
    Parse a CSV file with fantasy team data.

    Expected columns:
    - player_name: Name of the player
    - player_team: NFL team abbreviation the player belongs to
    - player_position: Position of the player (e.g., QB, RB, WR, TE)
    - fantasy_team: Name of the fantasy team

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

    df = pd.read_csv(csv_path)

    # Normalize column names (case-insensitive, strip whitespace, handle underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    required_columns = ["player_name", "player_team", "player_position", "fantasy_team"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            f"Found columns: {list(df.columns)}"
        )

    # Remove rows with missing values in required columns
    df = df.dropna(subset=required_columns)

    players = []
    for _, row in df.iterrows():
        player = Player(
            player_name=str(row["player_name"]).strip(),
            player_team=str(row["player_team"]).strip().upper(),
            player_position=str(row["player_position"]).strip().upper(),
            fantasy_team=str(row["fantasy_team"]).strip(),
        )
        players.append(player)

    return players

