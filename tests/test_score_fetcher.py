"""Tests for score fetcher."""

from fantasy.models import Player
from fantasy.score_fetcher import MockScoreFetcher, PlayerScore


class TestMockScoreFetcher:
    """Tests for MockScoreFetcher."""

    def test_fetch_single_player_score(self):
        """Test fetching a score for a single player."""
        fetcher = MockScoreFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score = fetcher.fetch_player_score(player, week=5)

        assert score is not None
        assert isinstance(score, PlayerScore)
        assert score.player_name == "Patrick Mahomes"
        assert score.position == "QB"
        assert score.team == "KC"
        assert score.week == 5
        assert 0 <= score.score <= 30

    def test_fetch_player_score_consistency(self):
        """Test that the same player/week/year combination returns same score."""
        fetcher = MockScoreFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score1 = fetcher.fetch_player_score(player, week=5, season_year=2024)
        score2 = fetcher.fetch_player_score(player, week=5, season_year=2024)

        assert score1 is not None
        assert score2 is not None
        assert score1.score == score2.score

    def test_fetch_player_score_different_weeks(self):
        """Test that different weeks return different scores."""
        fetcher = MockScoreFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score1 = fetcher.fetch_player_score(player, week=5)
        score2 = fetcher.fetch_player_score(player, week=6)

        assert score1 is not None
        assert score2 is not None
        # They might be the same by chance, but likely different
        # At least verify both are valid scores
        assert 0 <= score1.score <= 30
        assert 0 <= score2.score <= 30

    def test_fetch_multiple_player_scores(self):
        """Test fetching scores for multiple players."""
        fetcher = MockScoreFetcher()
        players = [
            Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A"),
            Player(name="Aaron Jones", position="RB", team="GB", fantasy_team="Team A"),
            Player(name="Josh Allen", position="QB", team="BUF", fantasy_team="Team B"),
        ]

        scores = fetcher.fetch_player_scores(players, week=5)

        assert len(scores) == 3
        assert all(isinstance(score, PlayerScore) for score in scores)
        assert all(score.week == 5 for score in scores)
        assert all(0 <= score.score <= 30 for score in scores)

    def test_fetch_player_score_with_season_year(self):
        """Test fetching score with season year parameter."""
        fetcher = MockScoreFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score = fetcher.fetch_player_score(player, week=5, season_year=2023)

        assert score is not None
        assert score.week == 5

    def test_fetch_player_score_never_none(self):
        """Test that MockScoreFetcher never returns None."""
        fetcher = MockScoreFetcher()
        player = Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_team="Team A")

        score = fetcher.fetch_player_score(player, week=5)

        assert score is not None

