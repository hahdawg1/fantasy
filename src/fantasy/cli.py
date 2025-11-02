"""Command-line interface for fantasy scoring."""

import click
from datetime import datetime
from pathlib import Path

from fantasy.csv_parser import parse_fantasy_csv
from fantasy.calculator import calculate_week_score, format_team_scores
import nflreadpy as nfl


@click.command()
@click.argument("csv_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--week",
    "-w",
    type=int,
    help="Week number to calculate scores for. If not provided, uses current week.",
)
@click.option(
    "--season",
    "-s",
    type=int,
    help="Season year (defaults to current season from nflreadpy)",
    default=None,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path for results (CSV format)",
)
def main(
    csv_file: Path,
    week: int | None,
    season: int | None,
    output: Path | None,
) -> None:
    """
    Calculate fantasy team scores from a CSV file using nflreadpy.

    The CSV file should have columns: player_name, player_team, player_position, fantasy_team
    """
    # Determine season if not provided
    if season is None:
        try:
            season = nfl.get_current_season()
            click.echo(f"Using current season: {season}")
        except Exception:
            # Fallback to current year
            season = datetime.now().year
            click.echo(
                f"Warning: Could not get current season from nflreadpy. Using {season}.",
                err=True,
            )

    # Determine week if not provided
    if week is None:
        try:
            week = nfl.get_current_week()
            click.echo(f"Using current week: {week}")
        except Exception:
            week = 1
            click.echo(
                "Warning: Week not specified and could not determine current week. Using week 1. "
                "Please specify --week for accurate results.",
                err=True,
            )

    # Parse CSV
    click.echo(f"Parsing CSV file: {csv_file}")
    try:
        players = parse_fantasy_csv(csv_file)
        click.echo(
            f"Found {len(players)} players across {len(set(p.fantasy_team for p in players))} teams"
        )
    except Exception as e:
        click.echo(f"Error parsing CSV: {e}", err=True)
        raise click.Abort()

    # Calculate scores
    click.echo(f"Calculating scores for {season} week {week}...")
    try:
        team_scores = calculate_week_score(players, week, season)
    except ValueError as e:
        click.echo(
            f"Error calculating scores: {e}\n"
            f"This might indicate that nflreadpy has no data for {season} week {week}. "
            f"Try using a different season/year or week.",
            err=True,
        )
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error calculating scores: {e}", err=True)
        raise click.Abort()

    # Display results
    click.echo("\n" + "=" * 60)
    click.echo(format_team_scores(team_scores))
    click.echo("=" * 60)

    # Save to file if requested
    if output:
        import pandas as pd

        # Flatten team scores for CSV export
        rows = []
        for ts in team_scores:
            for ps in ts.player_scores:
                rows.append(
                    {
                        "fantasy_team": ts.fantasy_team,
                        "season": ts.season,
                        "week": ts.week,
                        "player_name": ps.player_name,
                        "player_position": ps.player_position,
                        "player_team": ps.player_team,
                        "fantasy_points": ps.fantasy_points,
                        "team_total": ts.total_points,
                    }
                )

        df = pd.DataFrame(rows)
        df.to_csv(output, index=False)
        click.echo(f"\nResults saved to: {output}")


if __name__ == "__main__":
    main()

