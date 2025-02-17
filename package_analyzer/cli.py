import typer
from typing import Optional
from rich.console import Console
from . import scraper
from . import utils
from . import visualizer
from .security_analyzer import SecurityAnalyzer
from .issue_tracker import IssueTracker, display_issue_analysis

console = Console()
security_analyzer = SecurityAnalyzer()
issue_tracker = IssueTracker()


def main(
    package_name: str,
    version: Optional[str] = typer.Option(
        None, "--version", "-v", help="Specific version to analyze"
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format (table/json)"
    ),
    save: bool = typer.Option(False, "--save", "-s", help="Save the results to a file"),
    graph: bool = typer.Option(
        False, "--graph", "-g", help="Generate dependency graph"
    ),
    depth: int = typer.Option(
        2, "--depth", "-d", help="Maximum depth for dependency graph"
    ),
    graph_format: str = typer.Option(
        "png", "--graph-format", help="Graph output format (pdf, png, svg)"
    ),
    security: bool = typer.Option(
        False, "--security", help="Perform security analysis"
    ),
    issues: bool = typer.Option(False, "--issues", "-i", help="Analyze GitHub issues"),
):
    """Analyze dependencies, security, and issues for a Python package."""
    try:
        console.print(f"[green]Analyzing package: {package_name}...[/green]")
        package_data = scraper.fetch_package_info(package_name, version)

        if format == "table":
            utils.display_table(package_data)
        elif format == "json":
            utils.display_json(package_data)

        if security:
            console.print(f"\n[green]Performing security analysis...[/green]")
            security_data = security_analyzer.analyze_package(package_name, version)
            utils.display_security_report(security_data)

        if issues:
            console.print(f"\n[green]Analyzing GitHub issues...[/green]")
            issue_data = issue_tracker.analyze_issues(package_name)
            display_issue_analysis(issue_data)

        if graph:
            console.print(f"\n[green]Generating dependency graph...[/green]")
            graph_file = visualizer.save_dependency_graph(
                package_name, max_depth=depth, output_format=graph_format
            )
            console.print(f"[green]Dependency graph saved as: {graph_file}[/green]")

        if save:
            utils.save_results(package_data, package_name)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    typer.run(main)
