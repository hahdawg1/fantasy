"""Command-line interface for fantasy scoring."""

import click
from datetime import datetime
from pathlib import Path

from fantasy.csv_parser import parse_fantasy_csv
from fantasy.calculator import calculate_team_scores, format_team_scores
from fantasy.score_fetcher import MockScoreFetcher, ScoreFetcher
from fantasy.ffdp_fetcher import FFDPFetcher


@click.command()
@click.argument("csv_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--week",
    "-w",
    type=int,
    help="Week number to calculate scores for. If not provided, uses current week.",
)
@click.option(
    "--season-year",
    "-y",
    type=int,
    help="Season year (defaults to current year)",
    default=None,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path for results (CSV format)",
)
@click.option(
    "--fetcher",
    type=click.Choice(["mock", "ffdp"], case_sensitive=False),
    default="mock",
    help="Score fetcher to use: 'mock' for testing, 'ffdp' for Fantasy Football Data Pros API (default: mock)",
    show_default=True,
)
def main(
    csv_file: Path,
    week: int | None,
    season_year: int | None,
    output: Path | None,
    fetcher: str,
) -> None:
    """
    Calculate fantasy team scores from a CSV file.

    The CSV file should have columns: fantasy_team, player name, player position, player team
    """
    # Determine week if not provided (default to current week)
    if week is None:
        # For now, default to week 1. In a real implementation, you'd determine
        # the current week based on the current date and season start
        current_date = datetime.now()
        # Simple heuristic: assume season starts around September 1st
        if current_date.month >= 9:
            # Rough estimate: week = (day of year - 244) // 7 + 1
            # This is approximate and should be replaced with actual season data
            week = 1  # Default fallback
            click.echo(
                "Warning: Week not specified. Using week 1. "
                "Please specify --week for accurate results.",
                err=True,
            )
        else:
            week = 1
            click.echo(
                "Warning: Week not specified. Using week 1. "
                "Please specify --week for accurate results.",
                err=True,
            )

    if season_year is None:
        season_year = datetime.now().year

    # Parse CSV
    click.echo(f"Parsing CSV file: {csv_file}")
    try:
        players = parse_fantasy_csv(csv_file)
        click.echo(f"Found {len(players)} players across {len(set(p.fantasy_team for p in players))} teams")
    except Exception as e:
        click.echo(f"Error parsing CSV: {e}", err=True)
        raise click.Abort()

    # Initialize score fetcher
    score_fetcher: ScoreFetcher
    if fetcher == "mock":
        score_fetcher = MockScoreFetcher()
        click.echo(
            "Warning: Using mock score fetcher. Scores are randomly generated for testing.",
            err=True,
        )
    elif fetcher == "ffdp":
        score_fetcher = FFDPFetcher()
        click.echo(f"Using Fantasy Football Data Pros API for {season_year} week {week}...")
    else:
        click.echo(f"Unknown fetcher: {fetcher}", err=True)
        raise click.Abort()

    # Calculate scores
    click.echo(f"Calculating scores for week {week}...")
    try:
        team_scores = calculate_team_scores(players, week, score_fetcher, season_year)
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
                        "week": ts.week,
                        "player_name": ps.player_name,
                        "position": ps.position,
                        "team": ps.team,
                        "score": ps.score,
                        "team_total": ts.total_score,
                    }
                )

        df = pd.DataFrame(rows)
        df.to_csv(output, index=False)
        click.echo(f"\nResults saved to: {output}")


if __name__ == "__main__":
    main()

