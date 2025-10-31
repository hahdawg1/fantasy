"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest

from fantasy.models import Player


@pytest.fixture
def sample_players():
    """Return a list of sample players for testing."""
    return [
        Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A"),
        Player(name="Aaron Jones", position="RB", team="GB", fantasy_team="Team A"),
        Player(name="Josh Allen", position="QB", team="BUF", fantasy_team="Team B"),
        Player(name="Davante Adams", position="WR", team="LV", fantasy_team="Team B"),
    ]


@pytest.fixture
def csv_file_with_teams():
    """Create a temporary CSV file with fantasy team data."""
    content = """fantasy_team,player name,player position,player team
Team Alpha,Patrick Mahomes,QB,KC
Team Alpha,Aaron Jones,RB,GB
Team Beta,Josh Allen,QB,BUF
Team Beta,Davante Adams,WR,LV
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def csv_file_with_spaces_in_columns():
    """Create a CSV file with spaces in column names."""
    content = """fantasy_team,player name,player position,player team
Team A,Cooper Kupp,WR,LAR
Team A,Travis Kelce,TE,KC
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    temp_path.unlink(missing_ok=True)


@pytest.fixture
def csv_file_with_underscores_in_columns():
    """Create a CSV file with underscores in column names."""
    content = """fantasy_team,player_name,player_position,player_team
Team A,Derrick Henry,RB,TEN
Team B,Justin Jefferson,WR,MIN
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    temp_path.unlink(missing_ok=True)

