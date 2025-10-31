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

Calculate scores for a specific week:

```bash
fantasy teams.csv --week 5
```

Calculate scores for the current week (defaults to week 1 if not specified):

```bash
fantasy teams.csv
```

Save results to a file:

```bash
fantasy teams.csv --week 5 --output results.csv
```

Specify season year:

```bash
fantasy teams.csv --week 5 --season-year 2024
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

Currently, the app includes a `mock` score fetcher that generates random scores for testing.

To implement a real score fetcher (e.g., ESPN API, NFL.com API, etc.), create a class that implements the `ScoreFetcher` protocol from `fantasy.score_fetcher`.

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

