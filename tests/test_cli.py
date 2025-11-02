"""Tests for CLI module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from fantasy.cli import main


class TestCLI:
    """Tests for CLI interface."""

    @patch("fantasy.cli.nfl.get_current_season")
    @patch("fantasy.cli.nfl.get_current_week")
    @patch("fantasy.cli.calculate_week_score")
    def test_cli_with_valid_csv(self, mock_calc, mock_get_week, mock_get_season, csv_file_with_teams):
        """Test CLI with a valid CSV file."""
        from fantasy.models import TeamScore, PlayerScore

        mock_get_season.return_value = 2023
        mock_get_week.return_value = 5

        # Mock team scores (total_points must match sum of player scores)
        mock_team_scores = [
            TeamScore(
                fantasy_team="Team Alpha",
                week=5,
                season=2023,
                total_points=25.0,  # Must match sum of player_scores
                player_scores=[
                    PlayerScore(
                        player_name="Patrick Mahomes",
                        player_team="KC",
                        player_position="QB",
                        week=5,
                        season=2023,
                        fantasy_points=25.0,
                    )
                ],
            )
        ]
        mock_calc.return_value = mock_team_scores

        runner = CliRunner()
        result = runner.invoke(main, [str(csv_file_with_teams)])

        assert result.exit_code == 0
        assert "Team Alpha" in result.output or "2023 Week 5" in result.output

    @patch("fantasy.cli.nfl.get_current_season")
    @patch("fantasy.cli.nfl.get_current_week")
    @patch("fantasy.cli.calculate_week_score")
    def test_cli_with_explicit_week_season(
        self, mock_calc, mock_get_week, mock_get_season, csv_file_with_teams
    ):
        """Test CLI with explicit week and season."""
        from fantasy.models import TeamScore, PlayerScore

        mock_get_season.return_value = 2023
        mock_get_week.return_value = 5

        mock_team_scores = [
            TeamScore(
                fantasy_team="Team Alpha",
                week=10,
                season=2022,
                total_points=0.0,  # Must match sum of player_scores (empty list = 0.0)
                player_scores=[],
            )
        ]
        mock_calc.return_value = mock_team_scores

        runner = CliRunner()
        result = runner.invoke(
            main, [str(csv_file_with_teams), "--week", "10", "--season", "2022"]
        )

        assert result.exit_code == 0
        mock_calc.assert_called_once()
        # Check that week 10 and season 2022 were used
        call_args = mock_calc.call_args
        assert call_args[0][1] == 10  # week
        assert call_args[0][2] == 2022  # season

    def test_cli_with_nonexistent_file(self):
        """Test CLI with nonexistent file shows error."""
        runner = CliRunner()
        result = runner.invoke(main, ["nonexistent.csv"])

        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_cli_invalid_csv_format(self):
        """Test CLI with invalid CSV format shows error."""
        content = "player_name,player_team\nPatrick Mahomes,KC"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            runner = CliRunner()
            result = runner.invoke(main, [str(temp_path)])

            assert result.exit_code != 0
            assert "error" in result.output.lower() or "missing" in result.output.lower()
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_help(self):
        """Test CLI help message."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "CSV_FILE" in result.output
        assert "--week" in result.output

