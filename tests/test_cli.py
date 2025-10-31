"""Tests for CLI module."""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from fantasy.cli import main


class TestCLI:
    """Tests for CLI interface."""

    def test_cli_with_valid_csv(self, csv_file_with_teams):
        """Test CLI with a valid CSV file."""
        runner = CliRunner()
        result = runner.invoke(main, [str(csv_file_with_teams), "--week", "5"])

        assert result.exit_code == 0
        assert "Team Alpha" in result.output or "Team Beta" in result.output
        assert "Week 5" in result.output

    def test_cli_with_missing_week_warns(self, csv_file_with_teams):
        """Test CLI without week parameter shows warning."""
        runner = CliRunner()
        result = runner.invoke(main, [str(csv_file_with_teams)])

        # Should still work but with warning
        assert "Warning" in result.output or result.exit_code == 0

    def test_cli_with_output_file(self, csv_file_with_teams):
        """Test CLI with output file option."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_path = Path(f.name)

        try:
            runner = CliRunner()
            result = runner.invoke(
                main,
                [str(csv_file_with_teams), "--week", "5", "--output", str(output_path)],
            )

            assert result.exit_code == 0
            assert output_path.exists()
            assert "saved to" in result.output.lower() or str(output_path) in result.output

            # Verify output file has content
            content = output_path.read_text()
            assert "fantasy_team" in content or "Team" in content
        finally:
            output_path.unlink(missing_ok=True)

    def test_cli_with_season_year(self, csv_file_with_teams):
        """Test CLI with season year parameter."""
        runner = CliRunner()
        result = runner.invoke(
            main, [str(csv_file_with_teams), "--week", "5", "--season-year", "2024"]
        )

        assert result.exit_code == 0

    def test_cli_with_nonexistent_file(self):
        """Test CLI with nonexistent file shows error."""
        runner = CliRunner()
        result = runner.invoke(main, ["nonexistent.csv", "--week", "5"])

        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_cli_invalid_csv_format(self):
        """Test CLI with invalid CSV format shows error."""
        # Create CSV with missing columns
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("fantasy_team,player_name\nTeam A,Player 1")
            temp_path = Path(f.name)

        try:
            runner = CliRunner()
            result = runner.invoke(main, [str(temp_path), "--week", "5"])

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
        assert "--week" in result.output or "--week" in result.output

    def test_cli_fetcher_option(self, csv_file_with_teams):
        """Test CLI fetcher option."""
        runner = CliRunner()
        result = runner.invoke(
            main, [str(csv_file_with_teams), "--week", "5", "--fetcher", "mock"]
        )

        # Should work with mock fetcher
        assert result.exit_code == 0

    def test_cli_shows_mock_warning(self, csv_file_with_teams):
        """Test CLI shows warning when using mock fetcher."""
        runner = CliRunner()
        result = runner.invoke(main, [str(csv_file_with_teams), "--week", "5"])

        # Mock fetcher is default, should show warning
        assert "mock" in result.output.lower() or "warning" in result.output.lower()

