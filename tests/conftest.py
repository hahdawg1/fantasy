"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest

from fantasy.models import Player


@pytest.fixture
def sample_players():
    """Return a list of sample players for testing."""
    return [
        Player(
            player_name="Patrick Mahomes",
            player_team="KC",
            player_position="QB",
            fantasy_team="Team A",
        ),
        Player(
            player_name="Aaron Jones",
            player_team="GB",
            player_position="RB",
            fantasy_team="Team A",
        ),
        Player(
            player_name="Josh Allen",
            player_team="BUF",
            player_position="QB",
            fantasy_team="Team B",
        ),
        Player(
            player_name="Davante Adams",
            player_team="LV",
            player_position="WR",
            fantasy_team="Team B",
        ),
    ]


@pytest.fixture
def csv_file_with_teams():
    """Create a temporary CSV file with fantasy team data."""
    content = """player_name,player_team,player_position,fantasy_team
Patrick Mahomes,KC,QB,Team Alpha
Aaron Jones,GB,RB,Team Alpha
Josh Allen,BUF,QB,Team Beta
Davante Adams,LV,WR,Team Beta
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink(missing_ok=True)

