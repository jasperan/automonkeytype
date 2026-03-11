"""CLI interface for AutoMonkeyType."""

import click

from . import __version__
from .engine import TypingEngine


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version")
@click.option(
    "--wpm",
    default=100,
    type=float,
    show_default=True,
    help="Target words per minute.",
)
@click.option(
    "--errors",
    default=0.0,
    type=float,
    show_default=True,
    help="Typo probability per keystroke (0.0 = perfect, 0.05 = ~5%% errors).",
)
@click.option(
    "--mode",
    default="words",
    type=click.Choice(["words", "time", "quote", "zen", "custom"]),
    show_default=True,
    help="MonkeyType test mode.",
)
@click.option(
    "--count",
    default="50",
    show_default=True,
    help="Word count (words mode) or seconds (time mode).",
)
@click.option(
    "--headless",
    is_flag=True,
    default=False,
    help="Run browser without visible window.",
)
def main(wpm, errors, mode, count, headless):
    """AutoMonkeyType - Human-like typing automation for monkeytype.com

    Launches a browser, navigates to MonkeyType, and types with realistic
    human-like timing dynamics including bigram-aware delays, finger travel
    distance modeling, fatigue simulation, and PID-controlled WPM targeting.
    """
    click.echo(
        f"\n"
        f"  AutoMonkeyType v{__version__}\n"
        f"  Target: {wpm} WPM | Errors: {errors:.1%} | "
        f"Mode: {mode} {count}\n"
    )

    engine = TypingEngine(
        target_wpm=wpm,
        error_rate=errors,
        headless=headless,
        mode=mode,
        word_count=count,
    )
    engine.run()


if __name__ == "__main__":
    main()
