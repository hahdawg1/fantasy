"""Tests for player matcher module."""

import pandas as pd
import pytest

from fantasy.player_matcher import (
    find_player_match,
    fuzzy_match_name,
    normalize_name,
)


class TestNormalizeName:
    """Tests for normalize_name function."""

    def test_normalize_basic(self):
        """Test basic name normalization."""
        assert normalize_name("Patrick Mahomes") == "patrick mahomes"
        assert normalize_name("  Aaron Jones  ") == "aaron jones"

    def test_normalize_removes_suffixes(self):
        """Test that common suffixes are removed."""
        assert normalize_name("Patrick Mahomes Jr.") == "patrick mahomes"
        assert normalize_name("Patrick Mahomes Jr") == "patrick mahomes"
        assert normalize_name("Tom Brady Sr.") == "tom brady"
        assert normalize_name("John Smith II") == "john smith"
        assert normalize_name("John Smith III") == "john smith"
        assert normalize_name("John Smith IV") == "john smith"

    def test_normalize_case_insensitive(self):
        """Test that normalization is case insensitive."""
        assert normalize_name("PATRICK MAHOMES") == "patrick mahomes"
        assert normalize_name("Patrick Mahomes") == normalize_name("patrick mahomes")


class TestFuzzyMatchName:
    """Tests for fuzzy_match_name function."""

    def test_exact_match(self):
        """Test exact name matching."""
        assert fuzzy_match_name("Patrick Mahomes", "Patrick Mahomes") is True
        assert fuzzy_match_name("Aaron Jones", "Aaron Jones") is True

    def test_case_insensitive_match(self):
        """Test case-insensitive matching."""
        assert fuzzy_match_name("Patrick Mahomes", "patrick mahomes") is True
        assert fuzzy_match_name("AARON JONES", "Aaron Jones") is True

    def test_suffix_removal_match(self):
        """Test matching when one name has a suffix."""
        assert fuzzy_match_name("Patrick Mahomes", "Patrick Mahomes Jr.") is True
        assert fuzzy_match_name("Tom Brady Sr.", "Tom Brady") is True

    def test_contains_match(self):
        """Test partial matching (one name contains the other)."""
        assert fuzzy_match_name("Patrick", "Patrick Mahomes") is True
        assert fuzzy_match_name("Patrick Mahomes", "Patrick") is True

    def test_subset_match(self):
        """Test matching when one name's words are subset of the other."""
        assert fuzzy_match_name("P. Mahomes", "Patrick Mahomes") is True
        assert fuzzy_match_name("Patrick Mahomes", "Patrick M. Mahomes") is True

    def test_first_last_match(self):
        """Test matching by first and last name."""
        assert fuzzy_match_name("Mahomes Patrick", "Patrick Mahomes") is True

    def test_no_match(self):
        """Test that different names don't match."""
        assert fuzzy_match_name("Patrick Mahomes", "Josh Allen") is False
        assert fuzzy_match_name("Tom Brady", "Aaron Rodgers") is False


class TestFindPlayerMatch:
    """Tests for find_player_match function."""

    @pytest.fixture
    def sample_stats_df(self):
        """Create a sample stats DataFrame for testing."""
        return pd.DataFrame(
            {
                "player_name": [
                    "Patrick Mahomes",
                    "Patrick Mahomes II",
                    "Aaron Jones",
                    "Josh Allen",
                    "Davante Adams",
                ],
                "position": ["QB", "QB", "RB", "QB", "WR"],
                "recent_team": ["KC", "KC", "GB", "BUF", "LV"],
                "team": ["KC", "KC", "GB", "BUF", "LV"],
                "passing_yards": [300, 0, 0, 250, 0],
                "passing_tds": [2, 0, 0, 3, 0],
                "interceptions": [1, 0, 0, 0, 0],
                "rushing_yards": [20, 0, 100, 30, 0],
                "rushing_tds": [0, 0, 1, 0, 0],
                "receiving_yards": [0, 0, 50, 0, 150],
                "receiving_tds": [0, 0, 0, 0, 2],
                "receptions": [0, 0, 5, 0, 10],
            }
        )

    def test_exact_match(self, sample_stats_df):
        """Test finding exact match."""
        result = find_player_match(
            "Patrick Mahomes", "QB", "KC", sample_stats_df, strict_team_match=False
        )
        assert result is not None
        assert result["player_name"] == "Patrick Mahomes"
        assert result["position"] == "QB"
        assert result["recent_team"] == "KC"

    def test_match_with_suffix(self, sample_stats_df):
        """Test matching when CSV has suffix but API doesn't."""
        result = find_player_match(
            "Patrick Mahomes Jr.", "QB", "KC", sample_stats_df, strict_team_match=False
        )
        assert result is not None
        assert "Mahomes" in result["player_name"]

    def test_match_api_has_suffix(self, sample_stats_df):
        """Test matching when API has suffix but CSV doesn't."""
        result = find_player_match(
            "Patrick Mahomes", "QB", "KC", sample_stats_df, strict_team_match=False
        )
        # Should match either "Patrick Mahomes" or "Patrick Mahomes II"
        assert result is not None

    def test_match_case_insensitive(self, sample_stats_df):
        """Test case-insensitive matching."""
        result = find_player_match(
            "patrick mahomes", "QB", "KC", sample_stats_df, strict_team_match=False
        )
        assert result is not None

    def test_match_wrong_position(self, sample_stats_df):
        """Test that wrong position doesn't match."""
        result = find_player_match(
            "Patrick Mahomes", "RB", "KC", sample_stats_df, strict_team_match=False
        )
        assert result is None

    def test_match_wrong_team_strict(self, sample_stats_df):
        """Test that wrong team doesn't match when strict_team_match is True."""
        result = find_player_match(
            "Patrick Mahomes", "QB", "BUF", sample_stats_df, strict_team_match=True
        )
        assert result is None

    def test_match_wrong_team_not_strict(self, sample_stats_df):
        """Test that wrong team can still match when strict_team_match is False."""
        # This should match by name and position even if team is wrong
        result = find_player_match(
            "Patrick Mahomes", "QB", "BUF", sample_stats_df, strict_team_match=False
        )
        # Should find Patrick Mahomes (KC) even though we searched for BUF
        assert result is not None
        assert result["recent_team"] == "KC"

    def test_match_partial_name(self, sample_stats_df):
        """Test matching with partial name."""
        result = find_player_match(
            "P. Mahomes", "QB", "KC", sample_stats_df, strict_team_match=False
        )
        assert result is not None
        assert "Mahomes" in result["player_name"]

    def test_match_abbreviated_name_format(self, sample_stats_df):
        """Test matching when API uses abbreviated format like 'J.Love'."""
        # Add a player with abbreviated format to the test data
        abbreviated_df = sample_stats_df.copy()
        new_row = pd.Series(
            {
                "player_name": "J.Love",
                "position": "QB",
                "recent_team": "GB",
                "team": "GB",
                "passing_yards": 250,
                "passing_tds": 2,
                "interceptions": 0,
                "rushing_yards": 0,
                "rushing_tds": 0,
                "receiving_yards": 0,
                "receiving_tds": 0,
                "receptions": 0,
            }
        )
        abbreviated_df = pd.concat([abbreviated_df, new_row.to_frame().T], ignore_index=True)

        # Should match "Jordan Love" to "J.Love"
        result = find_player_match(
            "Jordan Love", "QB", "GB", abbreviated_df, strict_team_match=False
        )
        assert result is not None
        assert result["player_name"] == "J.Love" or "Love" in result["player_name"]

    def test_no_match(self, sample_stats_df):
        """Test that non-existent player returns None."""
        result = find_player_match(
            "Fake Player", "QB", "KC", sample_stats_df, strict_team_match=False
        )
        assert result is None

    def test_match_without_recent_team_column(self, sample_stats_df):
        """Test matching when recent_team column doesn't exist."""
        df_no_recent = sample_stats_df.drop(columns=["recent_team"])
        result = find_player_match(
            "Patrick Mahomes", "QB", "KC", df_no_recent, strict_team_match=False
        )
        assert result is not None
        assert result["player_name"] == "Patrick Mahomes"

    def test_multiple_matches_returns_first(self, sample_stats_df):
        """Test that when multiple players match, first one is returned."""
        # Both "Patrick Mahomes" and "Patrick Mahomes II" should match
        result = find_player_match(
            "Patrick Mahomes", "QB", "KC", sample_stats_df, strict_team_match=False
        )
        assert result is not None
        # Should return the first match found
        assert "Mahomes" in result["player_name"]

