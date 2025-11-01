"""Tests for FFDP fetcher."""

from unittest.mock import Mock, patch
import pytest
import requests

from fantasy.models import Player
from fantasy.ffdp_fetcher import FFDPFetcher, PlayerScore


class TestFFDPFetcher:
    """Tests for FFDPFetcher."""

    def test_init(self):
        """Test FFDPFetcher initialization."""
        fetcher = FFDPFetcher()
        assert fetcher.rate_limit_delay == 0.5
        assert fetcher._cache == {}

        fetcher_custom = FFDPFetcher(rate_limit_delay=1.0)
        assert fetcher_custom.rate_limit_delay == 1.0

    @patch("fantasy.ffdp_fetcher.requests.get")
    def test_fetch_player_score_success(self, mock_get):
        """Test successfully fetching a player score."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "player_name": "Patrick Mahomes",
                "position": "QB",
                "team": "KC",
                "fantasy_points": 25.5,
            },
            {
                "player_name": "Aaron Jones",
                "position": "RB",
                "team": "GB",
                "fantasy_points": 18.3,
            },
        ]
        mock_get.return_value = mock_response

        fetcher = FFDPFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score = fetcher.fetch_player_score(player, week=5, season_year=2024)

        assert score is not None
        assert isinstance(score, PlayerScore)
        assert score.player_name == "Patrick Mahomes"
        assert score.position == "QB"
        assert score.team == "KC"
        assert score.week == 5
        assert score.score == 25.5

    @patch("fantasy.ffdp_fetcher.requests.get")
    def test_fetch_player_score_not_found(self, mock_get):
        """Test when player is not found in API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "player_name": "Other Player",
                "position": "QB",
                "team": "KC",
                "fantasy_points": 20.0,
            },
        ]
        mock_get.return_value = mock_response

        fetcher = FFDPFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score = fetcher.fetch_player_score(player, week=5, season_year=2024)

        assert score is None

    @patch("fantasy.ffdp_fetcher.requests.get")
    def test_fetch_player_score_api_error(self, mock_get):
        """Test when API request fails."""
        mock_get.side_effect = requests.RequestException("API Error")

        fetcher = FFDPFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score = fetcher.fetch_player_score(player, week=5, season_year=2024)

        assert score is None

    @patch("fantasy.ffdp_fetcher.requests.get")
    def test_fetch_player_score_different_score_fields(self, mock_get):
        """Test handling different score field names."""
        test_cases = [
            ("pts", 22.5),
            ("points", 23.0),
            ("fantasy_pts", 24.5),
            ("score", 25.0),
        ]

        for field_name, expected_score in test_cases:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {
                    "player_name": "Test Player",
                    "position": "QB",
                    "team": "KC",
                    field_name: expected_score,
                },
            ]
            mock_get.return_value = mock_response

            fetcher = FFDPFetcher()
            player = Player(
                name="Test Player", position="QB", team="KC", fantasy_team="Team A"
            )

            score = fetcher.fetch_player_score(player, week=5, season_year=2024)

            assert score is not None
            assert score.score == expected_score

    @patch("fantasy.ffdp_fetcher.requests.get")
    def test_fetch_player_score_name_matching(self, mock_get):
        """Test player name matching with variations."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "player_name": "Patrick Mahomes II",
                "position": "QB",
                "team": "KC",
                "fantasy_points": 25.5,
            },
        ]
        mock_get.return_value = mock_response

        fetcher = FFDPFetcher()
        # Try with just "Patrick Mahomes"
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score = fetcher.fetch_player_score(player, week=5, season_year=2024)

        assert score is not None
        assert "Patrick Mahomes" in score.player_name

    @patch("fantasy.ffdp_fetcher.requests.get")
    def test_fetch_player_score_caching(self, mock_get):
        """Test that API responses are cached."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "player_name": "Patrick Mahomes",
                "position": "QB",
                "team": "KC",
                "fantasy_points": 25.5,
            },
        ]
        mock_get.return_value = mock_response

        fetcher = FFDPFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        # First fetch
        score1 = fetcher.fetch_player_score(player, week=5, season_year=2024)
        # Second fetch - should use cache
        score2 = fetcher.fetch_player_score(player, week=5, season_year=2024)

        assert score1 is not None
        assert score2 is not None
        # Should only call API once
        assert mock_get.call_count == 1

    @patch("fantasy.ffdp_fetcher.requests.get")
    def test_fetch_player_scores_multiple_players(self, mock_get):
        """Test fetching scores for multiple players."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "player_name": "Patrick Mahomes",
                "position": "QB",
                "team": "KC",
                "fantasy_points": 25.5,
            },
            {
                "player_name": "Aaron Jones",
                "position": "RB",
                "team": "GB",
                "fantasy_points": 18.3,
            },
        ]
        mock_get.return_value = mock_response

        fetcher = FFDPFetcher()
        players = [
            Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A"),
            Player(name="Aaron Jones", position="RB", team="GB", fantasy_team="Team A"),
        ]

        scores = fetcher.fetch_player_scores(players, week=5, season_year=2024)

        assert len(scores) == 2
        assert all(isinstance(score, PlayerScore) for score in scores)
        assert scores[0].player_name == "Patrick Mahomes"
        assert scores[1].player_name == "Aaron Jones"

    @patch("fantasy.ffdp_fetcher.requests.get")
    def test_fetch_player_score_default_season_year(self, mock_get):
        """Test that default season year is used when not provided."""
        from datetime import datetime

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        fetcher = FFDPFetcher()
        player = Player(name="Test Player", position="QB", team="KC", fantasy_team="Team A")

        fetcher.fetch_player_score(player, week=5)

        # Check that API was called with current year
        expected_year = datetime.now().year
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert str(expected_year) in call_url

