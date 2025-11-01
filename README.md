# Fantasy

A Python application for calculating fantasy team scores from CSV data.

## Features

- Parse fantasy team rosters from CSV files
- Calculate team scores for any week (current or previous)
- Support for multiple fantasy teams
- Extensible score fetching system (currently includes mock fetcher for testing)

## Installation

Install in development mode:

```bash
pip install -e .
```

Install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

### CSV Format

Your CSV file should have the following columns:
- `fantasy_team`: Name of the fantasy team
- `player name` (or `player_name`): Name of the player
- `player position` (or `player_position`): Position (e.g., QB, RB, WR, TE)
- `player team` (or `player_team`): Real team the player belongs to

#### NFL Team Abbreviations

When filling in the `player team` column, use the following NFL team abbreviations:

**American Football Conference (AFC)**

*AFC East:*
- `BUF` - Buffalo Bills
- `MIA` - Miami Dolphins
- `NE` - New England Patriots
- `NYJ` - New York Jets

*AFC North:*
- `BAL` - Baltimore Ravens
- `CIN` - Cincinnati Bengals
- `CLE` - Cleveland Browns
- `PIT` - Pittsburgh Steelers

*AFC South:*
- `HOU` - Houston Texans
- `IND` - Indianapolis Colts
- `JAX` - Jacksonville Jaguars
- `TEN` - Tennessee Titans

*AFC West:*
- `DEN` - Denver Broncos
- `KC` - Kansas City Chiefs
- `LV` - Las Vegas Raiders
- `LAC` - Los Angeles Chargers

**National Football Conference (NFC)**

*NFC East:*
- `DAL` - Dallas Cowboys
- `NYG` - New York Giants
- `PHI` - Philadelphia Eagles
- `WAS` - Washington Commanders

*NFC North:*
- `CHI` - Chicago Bears
- `DET` - Detroit Lions
- `GB` - Green Bay Packers
- `MIN` - Minnesota Vikings

*NFC South:*
- `ATL` - Atlanta Falcons
- `CAR` - Carolina Panthers
- `NO` - New Orleans Saints
- `TB` - Tampa Bay Buccaneers

*NFC West:*
- `ARI` - Arizona Cardinals
- `LAR` - Los Angeles Rams
- `SF` - San Francisco 49ers
- `SEA` - Seattle Seahawks

### Command Line

Calculate scores for a specific week using mock data:

```bash
fantasy teams.csv --week 5
```

Calculate scores using the Fantasy Football Data Pros API:

```bash
fantasy teams.csv --week 5 --season-year 2024 --fetcher ffdp
```

Save results to a file:

```bash
fantasy teams.csv --week 5 --output results.csv --fetcher ffdp
```

Specify season year (required for FFDP fetcher):

```bash
fantasy teams.csv --week 5 --season-year 2024 --fetcher ffdp
```

### Example CSV

```csv
fantasy_team,player name,player position,player team
Team A,Patrick Mahomes,QB,KC
Team A,Aaron Jones,RB,GB
Team B,Josh Allen,QB,BUF
Team B,Davante Adams,WR,LV
```

### Example Output

```
============================================================

Team A - Week 5
  Total Score: 45.2
  Player Scores:
    Patrick Mahomes (QB, KC): 25.1
    Aaron Jones (RB, GB): 20.1

Team B - Week 5
  Total Score: 38.5
  Player Scores:
    Josh Allen (QB, BUF): 22.3
    Davante Adams (WR, LV): 16.2
============================================================
```

## Score Fetchers

The app supports multiple score fetchers:

### Mock Fetcher (default)

The `mock` fetcher generates random scores for testing. Use this when you want to test the application without making API calls.

```bash
fantasy teams.csv --week 5 --fetcher mock
```

### Fantasy Football Data Pros (FFDP) API

The `ffdp` fetcher uses the [Fantasy Football Data Pros API](https://www.fantasyfootballdatapros.com/our_api) to fetch real fantasy scores. This API provides historical data going back to 1999.

```bash
fantasy teams.csv --week 5 --season-year 2024 --fetcher ffdp
```

**Note:** The FFDP API requires an internet connection. If a player's score cannot be found, the application will raise an error.

**Rate Limiting:** The FFDP fetcher includes built-in rate limiting (0.5 seconds between requests) to avoid overwhelming the API. Responses are cached per week to minimize API calls.

### Implementing Custom Fetchers

To implement a custom score fetcher (e.g., ESPN API, NFL.com API, etc.), create a class that implements the `ScoreFetcher` protocol from `fantasy.score_fetcher` or extends `BaseScoreFetcher`.

## Development

Run tests:

```bash
pytest
```

Format code:

```bash
black src/
```

Lint code:

```bash
ruff check src/
```

Type checking:

```bash
mypy src/
```

