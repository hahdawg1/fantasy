"""Tests for calculator module."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from fantasy.calculator import (
    calculate_player_fantasy_points,
    calculate_week_score,
    format_team_scores,
)
from fantasy.models import Player, PlayerScore, TeamScore


class TestCalculatePlayerFantasyPoints:
    """Tests for calculate_player_fantasy_points function."""

    def test_qb_passing_points(self):
        """Test QB fantasy points calculation for passing stats."""
        player_row = {
            "passing_yards": 300,
            "passing_tds": 3,
            "interceptions": 1,
            "rushing_yards": 0,
            "rushing_tds": 0,
        }
        points = calculate_player_fantasy_points(player_row, "QB")
        # 300/25 + 3*4 - 1*2 = 12 + 12 - 2 = 22
        assert points == 22.0

    def test_qb_rushing_points(self):
        """Test QB fantasy points calculation including rushing."""
        player_row = {
            "passing_yards": 200,
            "passing_tds": 2,
            "interceptions": 0,
            "rushing_yards": 50,
            "rushing_tds": 1,
        }
        points = calculate_player_fantasy_points(player_row, "QB")
        # 200/25 + 2*4 + 50/10 + 1*6 = 8 + 8 + 5 + 6 = 27
        assert points == 27.0

    def test_rb_points(self):
        """Test RB fantasy points calculation."""
        player_row = {
            "rushing_yards": 100,
            "rushing_tds": 1,
            "receiving_yards": 50,
            "receiving_tds": 0,
            "receptions": 5,
        }
        points = calculate_player_fantasy_points(player_row, "RB")
        # 100/10 + 1*6 + 50/10 + 0*6 + 5*0.5 = 10 + 6 + 5 + 0 + 2.5 = 23.5
        assert points == 23.5

    def test_wr_points(self):
        """Test WR fantasy points calculation."""
        player_row = {
            "rushing_yards": 0,
            "rushing_tds": 0,
            "receiving_yards": 150,
            "receiving_tds": 2,
            "receptions": 10,
        }
        points = calculate_player_fantasy_points(player_row, "WR")
        # 0 + 0 + 150/10 + 2*6 + 10*0.5 = 0 + 0 + 15 + 12 + 5 = 32
        assert points == 32.0

    def test_te_points(self):
        """Test TE fantasy points calculation."""
        player_row = {
            "rushing_yards": 0,
            "rushing_tds": 0,
            "receiving_yards": 80,
            "receiving_tds": 1,
            "receptions": 8,
        }
        points = calculate_player_fantasy_points(player_row, "TE")
        # 0 + 0 + 80/10 + 1*6 + 8*0.5 = 0 + 0 + 8 + 6 + 4 = 18
        assert points == 18.0


class TestCalculateWeekScore:
    """Tests for calculate_week_score function."""

    @patch("fantasy.calculator.nfl.load_player_stats")
    def test_calculate_week_score_success(self, mock_load_stats):
        """Test successfully calculating week scores."""
        # Mock nflreadpy response
        mock_data = pd.DataFrame(
            {
                "season": [2023, 2023, 2023, 2023],
                "week": [5, 5, 5, 5],
                "player_name": [
                    "Patrick Mahomes",
                    "Aaron Jones",
                    "Josh Allen",
                    "Davante Adams",
                ],
                "recent_team": ["KC", "GB", "BUF", "LV"],
                "team": ["KC", "GB", "BUF", "LV"],
                "position": ["QB", "RB", "QB", "WR"],
                "passing_yards": [300, 0, 250, 0],
                "passing_tds": [2, 0, 3, 0],
                "interceptions": [1, 0, 0, 0],
                "rushing_yards": [20, 100, 30, 0],
                "rushing_tds": [0, 1, 0, 0],
                "receiving_yards": [0, 50, 0, 150],
                "receiving_tds": [0, 0, 0, 2],
                "receptions": [0, 5, 0, 10],
            }
        )
        mock_load_stats.return_value = mock_data

        players = [
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

        team_scores = calculate_week_score(players, week=5, season=2023)

        assert len(team_scores) == 2
        team_names = {ts.fantasy_team for ts in team_scores}
        assert "Team A" in team_names
        assert "Team B" in team_names

        # Verify scores are calculated
        for team_score in team_scores:
            assert team_score.week == 5
            assert team_score.season == 2023
            assert team_score.total_points > 0

    @patch("fantasy.calculator.nfl.load_player_stats")
    def test_calculate_week_score_no_data(self, mock_load_stats):
        """Test error handling when no data is available."""
        mock_load_stats.return_value = pd.DataFrame()

        players = [
            Player(
                player_name="Patrick Mahomes",
                player_team="KC",
                player_position="QB",
                fantasy_team="Team A",
            )
        ]

        with pytest.raises(ValueError, match="No player stats found"):
            calculate_week_score(players, week=5, season=2023)

    @patch("fantasy.calculator.nfl.load_player_stats")
    def test_calculate_week_score_player_not_found(self, mock_load_stats):
        """Test error handling when a player is not found."""
        mock_data = pd.DataFrame(
            {
                "season": [2023],
                "week": [5],
                "player_name": ["Other Player"],
                "recent_team": ["KC"],
                "team": ["KC"],
                "position": ["QB"],
                "passing_yards": [200],
                "passing_tds": [1],
                "interceptions": [0],
                "rushing_yards": [0],
                "rushing_tds": [0],
                "receiving_yards": [0],
                "receiving_tds": [0],
                "receptions": [0],
            }
        )
        mock_load_stats.return_value = mock_data

        players = [
            Player(
                player_name="Patrick Mahomes",
                player_team="KC",
                player_position="QB",
                fantasy_team="Team A",
            )
        ]

        with pytest.raises(ValueError, match="Could not find score for player"):
            calculate_week_score(players, week=5, season=2023)


class TestFormatTeamScores:
    """Tests for format_team_scores function."""

    def test_format_single_team_score(self):
        """Test formatting a single team score."""
        player_scores = [
            PlayerScore(
                player_name="Player 1",
                player_team="KC",
                player_position="QB",
                week=5,
                season=2023,
                fantasy_points=20.0,
            ),
            PlayerScore(
                player_name="Player 2",
                player_team="GB",
                player_position="RB",
                week=5,
                season=2023,
                fantasy_points=15.5,
            ),
        ]
        team_score = TeamScore(
            fantasy_team="Team A",
            week=5,
            season=2023,
            total_points=35.5,
            player_scores=player_scores,
        )

        formatted = format_team_scores([team_score])

        assert "Team A" in formatted
        assert "2023 Week 5" in formatted
        assert "35.5" in formatted
        assert "Player 1" in formatted
        assert "Player 2" in formatted
        assert "QB" in formatted
        assert "RB" in formatted

    def test_format_empty_list(self):
        """Test formatting an empty list returns empty string."""
        formatted = format_team_scores([])
        assert formatted == ""

