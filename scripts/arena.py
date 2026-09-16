"""Head-to-head tournament arena for Kaggriculture agents."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Any, Callable, Dict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.kaggriculture.agents.baseline_naive import StarterBaselineAgent
from src.kaggriculture.agents.greedy_scheduler import FarmBrainAgent
from src.kaggriculture.sim.kaggle_wrapper import run_episode

console = Console()

AGENTS_REGISTRY: Dict[str, Callable[[], Any]] = {
    "starter": lambda: StarterBaselineAgent(),
    "greedy": lambda: FarmBrainAgent(),
}


def run_arena(agent1_name: str, agent2_name: str, games: int = 10, verbose: bool = False) -> None:
    console.print(f"[bold cyan]Starting Arena Tournament:[/] {agent1_name} vs {agent2_name} ({games} games)\n")

    a1_factory = AGENTS_REGISTRY.get(agent1_name)
    a2_factory = AGENTS_REGISTRY.get(agent2_name)

    if not a1_factory or not a2_factory:
        console.print(f"[red]Error: Agent name not recognized. Choose from: {list(AGENTS_REGISTRY.keys())}[/]")
        sys.exit(1)

    a1_wins = 0
    a2_wins = 0
    ties = 0
    a1_scores = []
    a2_scores = []

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Running games...", total=games)

        for g in range(games):
            # Alternate player sides to guarantee fairness
            swap = (g % 2 == 1)
            inst1 = a1_factory()
            inst2 = a2_factory()

            p0_agent = inst2 if swap else inst1
            p1_agent = inst1 if swap else inst2

            result = run_episode(p0_agent, p1_agent, seed=1000 + g)
            score0 = result["reward_player0"]
            score1 = result["reward_player1"]

            score_a1 = score1 if swap else score0
            score_a2 = score0 if swap else score1

            a1_scores.append(score_a1)
            a2_scores.append(score_a2)

            if score_a1 > score_a2:
                a1_wins += 1
            elif score_a2 > score_a1:
                a2_wins += 1
            else:
                ties += 1

            if verbose:
                console.print(
                    f"Game {g+1:2d} (Seed {1000+g}): {agent1_name}={score_a1:.1f} vs {agent2_name}={score_a2:.1f} "
                    f"-> {'A1 Win' if score_a1 > score_a2 else 'A2 Win' if score_a2 > score_a1 else 'Tie'}"
                )

            progress.advance(task)

    mean_a1 = sum(a1_scores) / len(a1_scores) if a1_scores else 0
    mean_a2 = sum(a2_scores) / len(a2_scores) if a2_scores else 0
    win_rate_a1 = (a1_wins / games) * 100 if games > 0 else 0

    table = Table(title=f"Tournament Summary ({games} Games)")
    table.add_column("Agent", style="cyan bold")
    table.add_column("Wins", justify="right")
    table.add_column("Win Rate (%)", justify="right")
    table.add_column("Mean Final Money", justify="right")
    table.add_column("Max Final Money", justify="right")

    table.add_row(
        agent1_name,
        str(a1_wins),
        f"{win_rate_a1:.1f}%",
        f"${mean_a1:,.2f}",
        f"${max(a1_scores):,.2f}",
    )
    table.add_row(
        agent2_name,
        str(a2_wins),
        f"{(a2_wins/games)*100:.1f}%",
        f"${mean_a2:,.2f}",
        f"${max(a2_scores):,.2f}",
    )

    console.print(table)
    margin = mean_a1 - mean_a2
    console.print(f"\n[bold green]Net Margin:[/] {agent1_name} vs {agent2_name} = [bold]{margin:+,.2f}[/]\n")


def main():
    parser = argparse.ArgumentParser(description="Kaggriculture Arena Tournament")
    parser.add_argument("--agent1", type=str, default="greedy", help="Name of agent 1")
    parser.add_argument("--agent2", type=str, default="starter", help="Name of agent 2")
    parser.add_argument("--games", type=int, default=10, help="Number of games to simulate")
    parser.add_argument("--verbose", action="store_true", help="Print per-game results")
    args = parser.parse_args()

    run_arena(args.agent1, args.agent2, games=args.games, verbose=args.verbose)


if __name__ == "__main__":
    main()
