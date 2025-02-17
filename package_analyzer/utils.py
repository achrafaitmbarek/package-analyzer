import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import Dict, Any

console = Console()


def display_table(data: Dict[str, Any]):
    """Display package information in a formatted table."""
    console.print(f"\nPackage: {data['name']}\n")

    # Basic Information Table
    info_table = Table(title="Package Information", show_header=True)
    info_table.add_column("Field", style="cyan")
    info_table.add_column("Value", style="green")

    info_table.add_row("Version", data["version"])
    info_table.add_row("Description", data["description"])
    info_table.add_row("Author", data["author"])
    info_table.add_row("License", data["license"])
    info_table.add_row("Homepage", data["homepage"])
    info_table.add_row("Documentation", data["documentation"])
    info_table.add_row("Requires Python", data["requires_python"])

    console.print(info_table)

    # Dependencies Table
    if data["dependencies"]:
        dep_table = Table(title="\nDependencies", show_header=True)
        dep_table.add_column("Package", style="cyan")

        for dep in data["dependencies"]:
            dep_table.add_row(dep)

        console.print(dep_table)
    else:
        console.print("\n[yellow]No dependencies found[/yellow]")


def display_security_report(security_data: Dict[str, Any]):
    """Display security analysis results."""
    summary = Text()
    summary.append(
        f"Total Vulnerabilities: {security_data['total_vulnerabilities']}\n\n"
    )
    summary.append("Severity Breakdown:\n")
    for severity, count in security_data["severity_counts"].items():
        color = {
            "CRITICAL": "red",
            "HIGH": "yellow",
            "MEDIUM": "magenta",
            "LOW": "blue",
        }.get(severity, "white")
        summary.append(f"{severity}: ", style=color)
        summary.append(f"{count}\n")

    console.print(Panel(summary, title="Security Summary"))

    if security_data["vulnerabilities"]:
        vuln_table = Table(title="\nVulnerability Details", show_header=True)
        vuln_table.add_column("ID", style="cyan")
        vuln_table.add_column("Severity", style="red")
        vuln_table.add_column("Summary")
        vuln_table.add_column("Fixed Versions", style="green")

        for vuln in security_data["vulnerabilities"]:
            severity_style = {
                "CRITICAL": "red",
                "HIGH": "yellow",
                "MEDIUM": "magenta",
                "LOW": "blue",
            }.get(vuln["severity"], "white")

            fixed_versions = (
                ", ".join(vuln["fixed_versions"])
                if vuln["fixed_versions"]
                else "No fix available"
            )

            vuln_table.add_row(
                vuln["id"],
                Text(vuln["severity"], style=severity_style),
                Text(vuln["summary"], style="white"),
                fixed_versions,
            )

        console.print(vuln_table)
    else:
        console.print("\n[green]No vulnerabilities found[/green]")


def display_json(data: Dict[str, Any]):
    """Display package information as JSON."""
    console.print_json(json.dumps(data, indent=2))


def save_results(data: Dict[str, Any], package_name: str):
    """Save the analysis results to a file."""
    filename = f"{package_name}_analysis.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    console.print(f"\n[green]Results saved to {filename}[/green]")
