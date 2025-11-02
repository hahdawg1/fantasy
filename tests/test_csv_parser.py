"""Tests for CSV parser."""

import tempfile
from pathlib import Path

import pytest

from fantasy.csv_parser import parse_fantasy_csv
from fantasy.models import Player


class TestCSVParser:
    """Tests for CSV parser."""

    def test_parse_valid_csv(self, csv_file_with_teams):
        """Test parsing a valid CSV file."""
        players = parse_fantasy_csv(csv_file_with_teams)

        assert len(players) == 4

        # Check first player
        assert players[0].player_name == "Patrick Mahomes"
        assert players[0].player_position == "QB"
        assert players[0].player_team == "KC"
        assert players[0].fantasy_team == "Team Alpha"

        # Check that all positions are uppercase
        for player in players:
            assert player.player_position == player.player_position.upper()
            assert player.player_team == player.player_team.upper()

    def test_parse_nonexistent_file(self):
        """Test that parsing a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_fantasy_csv("nonexistent_file.csv")

    def test_parse_csv_missing_columns(self):
        """Test that missing required columns raise ValueError."""
        content = "player_name,player_team\nPatrick Mahomes,KC"
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
        content = """player_name,player_team,player_position,fantasy_team
Patrick Mahomes,KC,QB,Team A
, , ,
Josh Allen,BUF,QB,Team B
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
        content = """player_name,player_team,player_position,fantasy_team
Patrick Mahomes,KC,qb,Team A
Aaron Jones,GB,rb,Team A
Cooper Kupp,LAR,Wr,Team A
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            players = parse_fantasy_csv(temp_path)
            assert players[0].player_position == "QB"
            assert players[1].player_position == "RB"
            assert players[2].player_position == "WR"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_parse_csv_strips_whitespace(self):
        """Test that whitespace is stripped from values."""
        content = """player_name,player_team,player_position,fantasy_team
 Patrick Mahomes , KC , QB , Team A 
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            players = parse_fantasy_csv(temp_path)
            assert players[0].fantasy_team == "Team A"
            assert players[0].player_name == "Patrick Mahomes"
            assert players[0].player_position == "QB"
            assert players[0].player_team == "KC"
        finally:
            temp_path.unlink(missing_ok=True)

