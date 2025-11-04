"""Tests for calculator module."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from fantasy.calculator import (
    calculate_player_fantasy_points,
    calculate_week_score,
    format_team_scores,
    select_optimal_lineup,
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

    @patch("fantasy.calculator.nfl.load_player_stats")
    def test_calculate_week_score_lineup_selection(self, mock_load_stats):
        """Test that optimal lineup is selected (1 QB, 1 RB, 2 WRs, 1 TE)."""
        # Mock nflreadpy response with multiple players at each position
        mock_data = pd.DataFrame(
            {
                "season": [2023] * 8,
                "week": [5] * 8,
                "player_name": [
                    "QB1 High",  # 25 points
                    "QB2 Low",   # 15 points (should not be selected)
                    "RB1 High",  # 20 points
                    "WR1 High",  # 30 points
                    "WR2 Med",   # 25 points
                    "WR3 Low",   # 10 points (should not be selected)
                    "TE1 High",  # 18 points
                    "RB2 Low",   # 12 points (should not be selected)
                ],
                "recent_team": ["KC", "BUF", "GB", "LV", "LV", "LV", "KC", "GB"],
                "team": ["KC", "BUF", "GB", "LV", "LV", "LV", "KC", "GB"],
                "position": ["QB", "QB", "RB", "WR", "WR", "WR", "TE", "RB"],
                "passing_yards": [500, 200, 0, 0, 0, 0, 0, 0],
                "passing_tds": [4, 2, 0, 0, 0, 0, 0, 0],
                "interceptions": [0, 0, 0, 0, 0, 0, 0, 0],
                "rushing_yards": [50, 30, 100, 0, 0, 0, 0, 60],
                "rushing_tds": [1, 0, 1, 0, 0, 0, 0, 1],
                "receiving_yards": [0, 0, 50, 200, 150, 50, 80, 0],
                "receiving_tds": [0, 0, 0, 3, 2, 1, 1, 0],
                "receptions": [0, 0, 5, 15, 10, 5, 8, 0],
            }
        )
        mock_load_stats.return_value = mock_data

        players = [
            Player(player_name="QB1 High", player_team="KC", player_position="QB", fantasy_team="Team A"),
            Player(player_name="QB2 Low", player_team="BUF", player_position="QB", fantasy_team="Team A"),
            Player(player_name="RB1 High", player_team="GB", player_position="RB", fantasy_team="Team A"),
            Player(player_name="RB2 Low", player_team="GB", player_position="RB", fantasy_team="Team A"),
            Player(player_name="WR1 High", player_team="LV", player_position="WR", fantasy_team="Team A"),
            Player(player_name="WR2 Med", player_team="LV", player_position="WR", fantasy_team="Team A"),
            Player(player_name="WR3 Low", player_team="LV", player_position="WR", fantasy_team="Team A"),
            Player(player_name="TE1 High", player_team="KC", player_position="TE", fantasy_team="Team A"),
        ]

        team_scores = calculate_week_score(players, week=5, season=2023)

        assert len(team_scores) == 1
        team_score = team_scores[0]
        assert team_score.fantasy_team == "Team A"

        # Verify lineup has exactly 5 players: 1 QB, 1 RB, 2 WRs, 1 TE
        assert len(team_score.player_scores) == 5

        # Count positions in lineup
        positions = [ps.player_position for ps in team_score.player_scores]
        assert positions.count("QB") == 1
        assert positions.count("RB") == 1
        assert positions.count("WR") == 2
        assert positions.count("TE") == 1

        # Verify highest scoring players were selected
        player_names = {ps.player_name for ps in team_score.player_scores}
        assert "QB1 High" in player_names  # Higher scoring QB
        assert "QB2 Low" not in player_names  # Lower scoring QB
        assert "RB1 High" in player_names  # Higher scoring RB
        assert "RB2 Low" not in player_names  # Lower scoring RB
        assert "WR1 High" in player_names  # Highest scoring WR
        assert "WR2 Med" in player_names  # Second highest scoring WR
        assert "WR3 Low" not in player_names  # Lowest scoring WR
        assert "TE1 High" in player_names  # Only TE

        # Verify total points matches sum of selected players
        # QB1: 500/25 + 4*4 + 50/10 + 1*6 = 20 + 16 + 5 + 6 = 47
        # RB1: 100/10 + 1*6 + 50/10 + 5*0.5 = 10 + 6 + 5 + 2.5 = 23.5
        # WR1: 200/10 + 3*6 + 15*0.5 = 20 + 18 + 7.5 = 45.5
        # WR2: 150/10 + 2*6 + 10*0.5 = 15 + 12 + 5 = 32
        # TE1: 80/10 + 1*6 + 8*0.5 = 8 + 6 + 4 = 18
        # Total: 47 + 23.5 + 45.5 + 32 + 18 = 166
        expected_total = 47.0 + 23.5 + 45.5 + 32.0 + 18.0
        assert abs(team_score.total_points - expected_total) < 0.1


class TestSelectOptimalLineup:
    """Tests for select_optimal_lineup function."""

    def test_select_qb_only(self):
        """Test selecting QB from multiple QBs."""
        player_scores = [
            PlayerScore("QB1", "KC", "QB", 5, 2023, 25.0),
            PlayerScore("QB2", "BUF", "QB", 5, 2023, 15.0),
            PlayerScore("QB3", "GB", "QB", 5, 2023, 20.0),
        ]

        lineup = select_optimal_lineup(player_scores)

        assert len(lineup) == 1
        assert lineup[0].player_name == "QB1"
        assert lineup[0].fantasy_points == 25.0

    def test_select_wrs_only(self):
        """Test selecting 2 highest WRs from multiple WRs."""
        player_scores = [
            PlayerScore("WR1", "LV", "WR", 5, 2023, 30.0),
            PlayerScore("WR2", "LV", "WR", 5, 2023, 25.0),
            PlayerScore("WR3", "LV", "WR", 5, 2023, 10.0),
            PlayerScore("WR4", "LV", "WR", 5, 2023, 20.0),
        ]

        lineup = select_optimal_lineup(player_scores)

        assert len(lineup) == 2
        player_names = {ps.player_name for ps in lineup}
        assert "WR1" in player_names
        assert "WR2" in player_names
        assert "WR3" not in player_names
        assert "WR4" not in player_names

    def test_select_full_lineup(self):
        """Test selecting full optimal lineup (1 QB, 1 RB, 2 WRs, 1 TE)."""
        player_scores = [
            PlayerScore("QB1", "KC", "QB", 5, 2023, 25.0),
            PlayerScore("QB2", "BUF", "QB", 5, 2023, 15.0),
            PlayerScore("RB1", "GB", "RB", 5, 2023, 20.0),
            PlayerScore("RB2", "GB", "RB", 5, 2023, 12.0),
            PlayerScore("WR1", "LV", "WR", 5, 2023, 30.0),
            PlayerScore("WR2", "LV", "WR", 5, 2023, 25.0),
            PlayerScore("WR3", "LV", "WR", 5, 2023, 10.0),
            PlayerScore("TE1", "KC", "TE", 5, 2023, 18.0),
            PlayerScore("TE2", "KC", "TE", 5, 2023, 12.0),
        ]

        lineup = select_optimal_lineup(player_scores)

        assert len(lineup) == 5

        # Check positions
        positions = [ps.player_position for ps in lineup]
        assert positions == ["QB", "RB", "WR", "WR", "TE"]

        # Verify highest scoring players selected
        player_names = {ps.player_name for ps in lineup}
        assert "QB1" in player_names
        assert "QB2" not in player_names
        assert "RB1" in player_names
        assert "RB2" not in player_names
        assert "WR1" in player_names
        assert "WR2" in player_names
        assert "WR3" not in player_names
        assert "TE1" in player_names
        assert "TE2" not in player_names

    def test_select_partial_lineup(self):
        """Test selecting lineup when some positions are missing."""
        player_scores = [
            PlayerScore("QB1", "KC", "QB", 5, 2023, 25.0),
            PlayerScore("WR1", "LV", "WR", 5, 2023, 30.0),
            PlayerScore("WR2", "LV", "WR", 5, 2023, 25.0),
        ]

        lineup = select_optimal_lineup(player_scores)

        assert len(lineup) == 3
        positions = {ps.player_position for ps in lineup}
        assert "QB" in positions
        assert "WR" in positions
        assert "RB" not in positions
        assert "TE" not in positions


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

