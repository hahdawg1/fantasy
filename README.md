# Fantasy

A Python application for calculating fantasy football team scores from CSV data using [nflreadpy](https://github.com/nflverse/nflreadpy).

## Features

- Parse fantasy team rosters from CSV files
- Calculate team scores for any week and season using nflreadpy
- Support for multiple fantasy teams
- Standard fantasy scoring rules (half-PPR)
- CLI interface for easy usage

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
- `player_name`: Name of the player
- `player_team`: NFL team abbreviation (see list below for valid abbreviations)
- `player_position`: Position of the player (QB, RB, WR, TE, etc.)
- `fantasy_team`: Name of the fantasy team

#### NFL Team Abbreviations

When filling in the `player_team` column, use the following abbreviations that match nflreadpy's data format:

**Current Teams:**

*American Football Conference (AFC):*
- `BUF` - Buffalo Bills
- `MIA` - Miami Dolphins
- `NE` - New England Patriots
- `NYJ` - New York Jets
- `BAL` - Baltimore Ravens
- `CIN` - Cincinnati Bengals
- `CLE` - Cleveland Browns
- `PIT` - Pittsburgh Steelers
- `HOU` - Houston Texans
- `IND` - Indianapolis Colts
- `JAX` - Jacksonville Jaguars
- `TEN` - Tennessee Titans
- `DEN` - Denver Broncos
- `KC` - Kansas City Chiefs
- `LV` - Las Vegas Raiders
- `LAC` - Los Angeles Chargers

*National Football Conference (NFC):*
- `DAL` - Dallas Cowboys
- `NYG` - New York Giants
- `PHI` - Philadelphia Eagles
- `WAS` - Washington Commanders
- `CHI` - Chicago Bears
- `DET` - Detroit Lions
- `GB` - Green Bay Packers
- `MIN` - Minnesota Vikings
- `ATL` - Atlanta Falcons
- `CAR` - Carolina Panthers
- `NO` - New Orleans Saints
- `TB` - Tampa Bay Buccaneers
- `ARI` - Arizona Cardinals
- `LAR` - Los Angeles Rams
- `SF` - San Francisco 49ers
- `SEA` - Seattle Seahawks

**Historical Team Abbreviations** (for older seasons):
- `OAK` - Oakland Raiders (renamed to LV in 2020)
- `SD` - San Diego Chargers (renamed to LAC in 2017)
- `STL` - St. Louis Rams (renamed to LAR in 2016)
- `LA` - Los Angeles Rams (also used as LAR)

Example CSV:

```csv
player_name,player_team,player_position,fantasy_team
Patrick Mahomes,KC,QB,Team Alpha
Aaron Jones,GB,RB,Team Alpha
Josh Allen,BUF,QB,Team Beta
Davante Adams,LV,WR,Team Beta
```

### Command Line

Calculate scores for a specific week and season:

```bash
fantasy teams.csv --week 5 --season 2023
```

Calculate scores for the current week (auto-detected):

```bash
fantasy teams.csv
```

Save results to a file:

```bash
fantasy teams.csv --week 5 --season 2023 --output results.csv
```

### Scoring Rules

The application uses standard fantasy football scoring:

**Quarterbacks (QB):**
- 1 point per 25 passing yards
- 4 points per passing touchdown
- -2 points per interception
- 1 point per 10 rushing yards
- 6 points per rushing touchdown

**Running Backs, Wide Receivers, Tight Ends (RB/WR/TE):**
- 1 point per 10 rushing yards
- 6 points per rushing touchdown
- 1 point per 10 receiving yards
- 6 points per receiving touchdown
- 0.5 points per reception (half-PPR)

### Example Output

```
============================================================

Team Beta - 2023 Week 5
  Total Points: 85.23
  Player Scores:
    Josh Allen (QB, BUF): 28.5
    Davante Adams (WR, LV): 27.63

Team Alpha - 2023 Week 5
  Total Points: 77.64
  Player Scores:
    Patrick Mahomes (QB, KC): 25.92
    Aaron Jones (RB, GB): 21.64
============================================================
```

## Data Source

This application uses [nflreadpy](https://github.com/nflverse/nflreadpy), a Python package for downloading NFL data from nflverse repositories. nflreadpy provides comprehensive NFL statistics dating back to 1999.

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

## License

MIT License
