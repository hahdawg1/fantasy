"""Tests for CSV parser."""

import tempfile
from pathlib import Path

import pytest

from fantasy.csv_parser import parse_fantasy_csv
from fantasy.models import Player


class TestCSVParser:
    """Tests for CSV parser."""

    def test_parse_valid_csv_with_spaces(self, csv_file_with_teams):
        """Test parsing a valid CSV file with spaces in column names."""
        players = parse_fantasy_csv(csv_file_with_teams)

        assert len(players) == 4

        # Check first player
        assert players[0].name == "Patrick Mahomes"
        assert players[0].position == "QB"
        assert players[0].team == "KC"
        assert players[0].fantasy_team == "Team Alpha"

        # Check that all positions are uppercase
        for player in players:
            assert player.position == player.position.upper()

    def test_parse_csv_with_underscores(self, csv_file_with_underscores_in_columns):
        """Test parsing CSV with underscores in column names."""
        players = parse_fantasy_csv(csv_file_with_underscores_in_columns)

        assert len(players) == 2
        assert players[0].name == "Derrick Henry"
        assert players[0].position == "RB"
        assert players[1].name == "Justin Jefferson"

    def test_parse_nonexistent_file(self):
        """Test that parsing a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_fantasy_csv("nonexistent_file.csv")

    def test_parse_csv_missing_columns(self):
        """Test that missing required columns raise ValueError."""
        content = "fantasy_team,player_name\nTeam A,Player 1"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Missing required columns"):
                parse_fantasy_csv(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_parse_csv_with_empty_rows(self):
        """Test that empty rows are filtered out."""
        content = """fantasy_team,player name,player position,player team
Team A,Player 1,Qb,KC
, , ,
Team B,Player 2,RB,GB
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            players = parse_fantasy_csv(temp_path)
            # Should only have 2 players, empty row should be filtered
            assert len(players) == 2
        finally:
            temp_path.unlink(missing_ok=True)

    def test_parse_csv_normalizes_position(self):
        """Test that positions are normalized to uppercase."""
        content = """fantasy_team,player name,player position,player team
Team A,Player 1,qb,KC
Team A,Player 2,rb,GB
Team A,Player 3,Wr,LAR
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            players = parse_fantasy_csv(temp_path)
            assert players[0].position == "QB"
            assert players[1].position == "RB"
            assert players[2].position == "WR"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_parse_csv_strips_whitespace(self):
        """Test that whitespace is stripped from values."""
        content = """fantasy_team,player name,player position,player team
 Team A , Patrick Mahomes , QB , KC 
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            players = parse_fantasy_csv(temp_path)
            assert players[0].fantasy_team == "Team A"
            assert players[0].name == "Patrick Mahomes"
            assert players[0].position == "QB"
            assert players[0].team == "KC"
        finally:
            temp_path.unlink(missing_ok=True)

