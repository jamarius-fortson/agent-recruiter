"""CLI for agent-recruiter — Expert Edition."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.theme import Theme

from .agents import RecruitingPipeline
from .models import Shortlist
from .tools.telemetry import setup_telemetry

# Custom theme for a premium feel
THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "score_high": "bold green",
    "score_mid": "bold yellow",
    "score_low": "bold red",
})

console = Console(theme=THEME)


def _setup_logging(verbose: bool):
    """Configure structured logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )


def _print_shortlist(shortlist: Shortlist) -> None:
    """Print a beautiful, premium summary of the shortlist."""
    console.print()
    
    header = Table.grid(expand=True)
    header.add_column(style="bold cyan")
    header.add_row(f"📋 SHORTLIST: {shortlist.job_title} @ {shortlist.job_company}")
    
    stats = (
        f"Screened: [bold]{shortlist.total_screened}[/bold] resumes  │  "
        f"Selected: [bold]{shortlist.shortlisted_count}[/bold] candidates  │  "
        f"Cost: [bold]${shortlist.total_cost_usd:.3f}[/bold]"
    )
    
    console.print(Panel(stats, title="[bold white]Execution Summary[/bold white]", border_style="cyan"))

    if shortlist.candidates:
        table = Table(box=None, header_style="bold white", show_edge=False)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Candidate", width=25)
        table.add_column("Score", justify="right")
        table.add_column("Match Bar", width=22)
        table.add_column("Top Strength", style="dim")

        for i, c in enumerate(shortlist.ranked(), 1):
            score = c.overall_score
            style = "score_high" if score >= 85 else "score_mid" if score >= 70 else "score_low"
            
            table.add_row(
                str(i),
                f"[{style}]{c.candidate.name}[/{style}]",
                f"[{style}]{score:>5.1f}%[/{style}]",
                f"[{style}]{c.score_bar}[/{style}]",
                c.strengths[0] if c.strengths else "N/A"
            )
        
        console.print(table)
    else:
        console.print("  [warning]No candidates met the minimum score threshold.[/warning]")
    
    console.print()


@click.group()
@click.version_option(version="0.2.0", prog_name="agent-recruiter")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--telemetry", is_flag=True, help="Enable OpenTelemetry tracing")
def cli(verbose: bool, telemetry: bool):
    """Autonomous talent sourcing pipeline — Production Edition."""
    _setup_logging(verbose)
    if telemetry:
        setup_telemetry()


@cli.command()
@click.option("--jd", required=True, type=click.Path(exists=True), help="Path to job description file")
@click.option("--resumes", required=True, type=click.Path(exists=True), help="Path to resume directory")
@click.option("--output", "-o", default="shortlist.json", help="Output JSON file")
@click.option("--report", "-r", default="shortlist_report.html", help="Output HTML report file")
@click.option("--top", type=int, default=10, help="Top N candidates")
@click.option("--min-score", type=float, default=70, help="Minimum match score")
@click.option("--model", default="gpt-4o", help="Primary LLM model (JD parsing, Scoring)")
@click.option("--screener-model", default="gpt-4o-mini", help="Model for bulk screening")
@click.option("--tone", default="professional", type=click.Choice(["professional", "casual", "startup"]))
@click.option("--sender", default="", help="Sender name for outreach")
@click.option("--company", default="", help="Company name (overrides JD)")
@click.option("--github/--no-github", default=True, help="Perform deep GitHub signal analysis")
@click.option("--blind", is_flag=True, help="Enable Blind Recruitment Mode (masks identities)")
def source(jd, resumes, output, report, top, min_score, model, screener_model, tone, sender, company, github, blind):
    """Full production pipeline: JD Parser → Parallel Screener → Match Scorer → Outreach."""
    from .tools.dashboard_gen import generate_dashboard

    pipeline = RecruitingPipeline(
        model=model,
        screener_model=screener_model,
        min_score=min_score,
        top_k=top,
        outreach_tone=tone,
        sender_name=sender,
        company_name=company,
        analyze_github=github,
        blind_mode=blind,
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        progress.add_task(description="Running multi-agent recruitment pipeline...", total=None)
        shortlist = asyncio.run(pipeline.run(jd_path=jd, resume_dir=resumes))

    _print_shortlist(shortlist)

    # Save results
    output_path = Path(output)
    output_path.write_text(json.dumps(shortlist.to_dict(), indent=2))
    
    # Generate visual report
    report_path = generate_dashboard(shortlist, output_path=report)
    
    console.print(f"  [success]✔[/success] Results archived to [bold cyan]{output}[/bold cyan]")
    console.print(f"  [success]✔[/success] Visual report ready → [bold cyan]{report_path}[/bold cyan]\n")


@cli.command("sync")
@click.option("--file", "-f", default="shortlist.json", type=click.Path(exists=True), help="Shortlist JSON to sync")
def sync(file):
    """Sync shortlist results to Supabase for persistence."""
    from .tools.database import get_supabase_client
    
    data = json.loads(Path(file).read_text())
    shortlist = Shortlist.from_dict(data)
    
    client = get_supabase_client()
    if not client:
        console.print("  [error]Error:[/error] SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment.")
        return

    with console.status("[bold cyan]Syncing to cloud database..."):
        success = asyncio.run(client.sync_shortlist(shortlist))
    
    if success:
        console.print(f"  [success]✔[/success] Successfully synced [bold]{shortlist.shortlisted_count}[/bold] candidates to Supabase.\n")
    else:
        console.print("  [error]✘[/error] Sync failed. Check logs for details.\n")


@cli.command("screen")
@click.option("--jd", required=True, type=click.Path(exists=True), help="Job description file")
@click.option("--resume", required=True, type=click.Path(exists=True), help="Single resume file")
@click.option("--model", default="gpt-4o-mini", help="LLM model for screening")
def screen(jd, resume, model):
    """Expert screening for a single candidate."""
    from .tools import read_jd, read_resume
    from .scoring import compute_match_score

    async def _run_screening():
        pipeline = RecruitingPipeline(model=model, screener_model=model)
        jd_text = read_jd(jd)
        reqs, _ = await pipeline.jd_parser.parse(jd_text)
        
        resume_text = read_resume(resume)
        profile, _ = await pipeline.screener.screen(resume_text, Path(resume).name)
        
        return compute_match_score(profile, reqs)

    with console.status("[bold cyan]Analyzing candidate..."):
        score = asyncio.run(_run_screening())

    console.print(Panel(
        f"[bold]{score.candidate.name}[/bold]\n"
        f"Score: [bold green]{score.overall_score}%[/bold green]\n\n"
        f"Matched Skills: {', '.join(score.matched_skills[:10])}\n"
        f"Experience: {score.candidate.years_experience} years\n"
        f"Reasoning: {score.reasoning}",
        title="Candidate Match Result",
        border_style="green"
    ))


def main():
    try:
        cli()
    except Exception as e:
        console.print(f"\n[error]Fatal Error:[/error] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
