"""Tests for fantasy models."""

import pytest

from fantasy.models import Player, PlayerScore, TeamScore


class TestPlayer:
    """Tests for Player model."""

    def test_player_creation(self):
        """Test creating a player with all fields."""
        player = Player(
            name="Patrick Mahomes",
            position="QB",
            team="KC",
            fantasy_team="Team A",
        )
        assert player.name == "Patrick Mahomes"
        assert player.position == "QB"
        assert player.team == "KC"
        assert player.fantasy_team == "Team A"

    def test_player_equality(self):
        """Test player equality comparison."""
        player1 = Player(name="Tom Brady", position="QB", team="TB", fantasy_team="Team A")
        player2 = Player(name="Tom Brady", position="QB", team="TB", fantasy_team="Team A")
        player3 = Player(name="Tom Brady", position="QB", team="TB", fantasy_team="Team B")

        assert player1 == player2
        assert player1 != player3

    def test_player_hash(self):
        """Test that players can be used in sets and dicts."""
        player1 = Player(name="Tom Brady", position="QB", team="TB", fantasy_team="Team A")
        player2 = Player(name="Tom Brady", position="QB", team="TB", fantasy_team="Team A")
        player3 = Player(name="Tom Brady", position="QB", team="TB", fantasy_team="Team B")

        player_set = {player1, player2, player3}
        assert len(player_set) == 2  # player1 and player2 are duplicates

        player_dict = {player1: "value1", player3: "value3"}
        assert player_dict[player2] == "value1"  # player2 should match player1's key


class TestPlayerScore:
    """Tests for PlayerScore model."""

    def test_player_score_creation(self):
        """Test creating a player score."""
        score = PlayerScore(
            player_name="Patrick Mahomes",
            position="QB",
            team="KC",
            week=5,
            score=25.5,
        )
        assert score.player_name == "Patrick Mahomes"
        assert score.position == "QB"
        assert score.team == "KC"
        assert score.week == 5
        assert score.score == 25.5

    def test_player_score_zero_allowed(self):
        """Test that zero score is allowed."""
        score = PlayerScore(
            player_name="Patrick Mahomes",
            position="QB",
            team="KC",
            week=5,
            score=0.0,
        )
        assert score.score == 0.0

    def test_player_score_negative_not_allowed(self):
        """Test that negative scores raise ValueError."""
        with pytest.raises(ValueError, match="Score cannot be negative"):
            PlayerScore(
                player_name="Patrick Mahomes",
                position="QB",
                team="KC",
                week=5,
                score=-5.0,
            )


class TestTeamScore:
    """Tests for TeamScore model."""

    def test_team_score_creation(self):
        """Test creating a team score."""
        player_scores = [
            PlayerScore(player_name="Player 1", position="QB", team="KC", week=5, score=20.0),
            PlayerScore(player_name="Player 2", position="RB", team="GB", week=5, score=15.5),
        ]

        team_score = TeamScore(
            fantasy_team="Team A",
            week=5,
            total_score=35.5,
            player_scores=player_scores,
        )

        assert team_score.fantasy_team == "Team A"
        assert team_score.week == 5
        assert team_score.total_score == 35.5
        assert len(team_score.player_scores) == 2

    def test_team_score_validation_pass(self):
        """Test that team score validation passes when total matches sum."""
        player_scores = [
            PlayerScore(player_name="Player 1", position="QB", team="KC", week=5, score=20.0),
            PlayerScore(player_name="Player 2", position="RB", team="GB", week=5, score=15.5),
        ]

        team_score = TeamScore(
            fantasy_team="Team A",
            week=5,
            total_score=35.5,
            player_scores=player_scores,
        )
        assert team_score.total_score == 35.5

    def test_team_score_validation_fails_when_mismatch(self):
        """Test that team score validation fails when total doesn't match sum."""
        player_scores = [
            PlayerScore(player_name="Player 1", position="QB", team="KC", week=5, score=20.0),
            PlayerScore(player_name="Player 2", position="RB", team="GB", week=5, score=15.5),
        ]

        with pytest.raises(ValueError, match="Total score.*does not match sum"):
            TeamScore(
                fantasy_team="Team A",
                week=5,
                total_score=50.0,  # Doesn't match 20.0 + 15.5
                player_scores=player_scores,
            )

    def test_team_score_allows_small_floating_point_differences(self):
        """Test that small floating point differences are allowed."""
        player_scores = [
            PlayerScore(player_name="Player 1", position="QB", team="KC", week=5, score=20.0),
            PlayerScore(player_name="Player 2", position="RB", team="GB", week=5, score=15.5),
        ]

        # 35.5 + 0.005 should be close enough
        team_score = TeamScore(
            fantasy_team="Team A",
            week=5,
            total_score=35.505,
            player_scores=player_scores,
        )
        assert team_score.total_score == 35.505

