"""Tests for calculator module."""

from fantasy.calculator import calculate_team_scores, format_team_scores
from fantasy.models import Player, TeamScore
from fantasy.score_fetcher import MockScoreFetcher


class TestCalculateTeamScores:
    """Tests for calculate_team_scores function."""

    def test_calculate_scores_single_team(self, sample_players):
        """Test calculating scores for a single team."""
        # Filter to just Team A players
        team_a_players = [p for p in sample_players if p.fantasy_team == "Team A"]
        fetcher = MockScoreFetcher()

        team_scores = calculate_team_scores(team_a_players, week=5, score_fetcher=fetcher)

        assert len(team_scores) == 1
        assert team_scores[0].fantasy_team == "Team A"
        assert team_scores[0].week == 5
        assert len(team_scores[0].player_scores) == 2
        assert team_scores[0].total_score > 0

    def test_calculate_scores_multiple_teams(self, sample_players):
        """Test calculating scores for multiple teams."""
        fetcher = MockScoreFetcher()

        team_scores = calculate_team_scores(sample_players, week=5, score_fetcher=fetcher)

        assert len(team_scores) == 2
        team_names = {ts.fantasy_team for ts in team_scores}
        assert "Team A" in team_names
        assert "Team B" in team_names

        # Each team should have 2 players
        for team_score in team_scores:
            assert len(team_score.player_scores) == 2

    def test_calculate_scores_sorted_by_total(self, sample_players):
        """Test that team scores are sorted by total score (descending)."""
        fetcher = MockScoreFetcher()

        team_scores = calculate_team_scores(sample_players, week=5, score_fetcher=fetcher)

        # Verify they're sorted descending
        for i in range(len(team_scores) - 1):
            assert team_scores[i].total_score >= team_scores[i + 1].total_score

    def test_calculate_scores_total_matches_sum(self, sample_players):
        """Test that total score matches sum of player scores."""
        fetcher = MockScoreFetcher()

        team_scores = calculate_team_scores(sample_players, week=5, score_fetcher=fetcher)

        for team_score in team_scores:
            calculated_sum = sum(ps.score for ps in team_score.player_scores)
            assert abs(team_score.total_score - calculated_sum) < 0.01

    def test_calculate_scores_with_season_year(self, sample_players):
        """Test calculating scores with season year parameter."""
        fetcher = MockScoreFetcher()

        team_scores = calculate_team_scores(
            sample_players, week=5, score_fetcher=fetcher, season_year=2024
        )

        assert len(team_scores) > 0
        assert all(ts.week == 5 for ts in team_scores)

    def test_calculate_scores_missing_player_raises_error(self):
        """Test that missing player scores raise ValueError."""
        # Create a custom fetcher that returns None for some players
        class SelectiveFetcher(MockScoreFetcher):
            def fetch_player_score(self, player, week, season_year=None):
                # Only return scores for Team A players
                if player.fantasy_team == "Team A":
                    return super().fetch_player_score(player, week, season_year)
                return None

        players = [
            Player(name="Player 1", position="QB", team="KC", fantasy_team="Team A"),
            Player(name="Player 2", position="RB", team="GB", fantasy_team="Team B"),
        ]
        fetcher = SelectiveFetcher()

        # Should raise ValueError when Player 2's score can't be found
        with pytest.raises(ValueError, match="Could not find score for player"):
            calculate_team_scores(players, week=5, score_fetcher=fetcher)


class TestFormatTeamScores:
    """Tests for format_team_scores function."""

    def test_format_single_team_score(self):
        """Test formatting a single team score."""
        from fantasy.models import PlayerScore

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

        formatted = format_team_scores([team_score])

        assert "Team A" in formatted
        assert "Week 5" in formatted
        assert "35.5" in formatted
        assert "Player 1" in formatted
        assert "Player 2" in formatted
        assert "QB" in formatted
        assert "RB" in formatted

    def test_format_multiple_team_scores(self):
        """Test formatting multiple team scores."""
        from fantasy.models import PlayerScore

        team_scores = [
            TeamScore(
                fantasy_team="Team A",
                week=5,
                total_score=20.0,
                player_scores=[
                    PlayerScore(
                        player_name="Player 1", position="QB", team="KC", week=5, score=20.0
                    ),
                ],
            ),
            TeamScore(
                fantasy_team="Team B",
                week=5,
                total_score=25.0,
                player_scores=[
                    PlayerScore(
                        player_name="Player 2", position="RB", team="GB", week=5, score=25.0
                    ),
                ],
            ),
        ]

        formatted = format_team_scores(team_scores)

        assert "Team A" in formatted
        assert "Team B" in formatted
        assert "20.0" in formatted
        assert "25.0" in formatted

    def test_format_empty_list(self):
        """Test formatting an empty list returns empty string."""
        formatted = format_team_scores([])
        assert formatted == ""

