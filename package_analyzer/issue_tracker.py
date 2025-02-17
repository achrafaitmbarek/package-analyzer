import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
import re
from datetime import datetime


class IssueTracker:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.console = Console()

    def analyze_issues(self, package_name: str) -> Dict[str, Any]:
        """Analyze GitHub issues for a given package."""
        repo_info = self._get_repo_from_pypi(package_name)
        if not repo_info:
            repo_info = self._search_github_repo(package_name)

        if not repo_info:
            return {"error": f"Could not find GitHub repository for {package_name}"}

        self.console.print(f"[green]Found repository: {repo_info['url']}[/green]")

        main_stats = self._get_repo_stats(repo_info["url"])

        return {
            "repository": repo_info,
            "summary": main_stats,
            "recent_issues": self._get_recent_issues(repo_info["url"]),
            "top_issues": self._get_top_issues(repo_info["url"]),
        }

    def _get_repo_from_pypi(self, package_name: str) -> Dict[str, str]:
        """Get repository information from PyPI."""
        try:
            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            project_urls = data["info"].get("project_urls", {})
            for url_type, url in project_urls.items():
                if url and "github.com" in url.lower():
                    return {
                        "name": package_name,
                        "url": url.strip("/"),
                        "source": "PyPI project_urls",
                    }
            return {}

        except Exception as e:
            self.console.print(f"[yellow]Error fetching from PyPI: {str(e)}[/yellow]")
            return {}

    def _get_repo_stats(self, repo_url: str) -> Dict[str, int]:
        """Get repository statistics including issues and pull requests."""
        try:
            response = requests.get(repo_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            stats = {"open_issues": 0, "pull_requests": 0}

            issues_counter = soup.find("span", id="issues-repo-tab-count")
            if issues_counter and "title" in issues_counter.attrs:
                stats["open_issues"] = int(issues_counter["title"])

            pr_counter = soup.find("span", id="pull-requests-repo-tab-count")
            if pr_counter and "title" in pr_counter.attrs:
                stats["pull_requests"] = int(pr_counter["title"])

            self.console.print(
                f"[green]Found {stats['open_issues']} open issues and {stats['pull_requests']} pull requests[/green]"
            )
            return stats

        except Exception as e:
            self.console.print(
                f"[yellow]Error getting repository stats: {str(e)}[/yellow]"
            )
            return {"open_issues": 0, "pull_requests": 0}

    def _get_recent_issues(self, repo_url: str) -> List[Dict[str, Any]]:
        """Get recent issues from repository."""
        try:
            issues_url = f"{repo_url}/issues"
            response = requests.get(issues_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            issues = []
            issue_rows = soup.find_all("div", {"class": re.compile(r"IssueRow-.*")})

            for row in issue_rows[:5]:
                title_elem = row.find("h3", {"class": re.compile(r"markdown-title.*")})
                if not title_elem:
                    continue

                title_link = title_elem.find("a")
                if not title_link:
                    continue

                issues.append(
                    {
                        "title": title_link.text.strip(),
                        "url": f"https://github.com{title_link['href']}",
                        "comments": "0",
                    }
                )

            return issues

        except Exception as e:
            self.console.print(
                f"[yellow]Error getting recent issues: {str(e)}[/yellow]"
            )
            return []

    def _get_top_issues(self, repo_url: str) -> List[Dict[str, Any]]:
        """Get most discussed issues."""
        try:
            issues_url = f"{repo_url}/issues?q=is:issue&sort=comments"
            response = requests.get(issues_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            top_issues = []
            issue_rows = soup.find_all("div", {"class": re.compile(r"IssueRow-.*")})

            for row in issue_rows[:5]:
                title_elem = row.find("h3", {"class": re.compile(r"markdown-title.*")})
                if not title_elem:
                    continue

                title_link = title_elem.find("a")
                if not title_link:
                    continue

                top_issues.append(
                    {
                        "title": title_link.text.strip(),
                        "url": f"https://github.com{title_link['href']}",
                        "comments": "0",
                    }
                )

            return top_issues

        except Exception as e:
            self.console.print(f"[yellow]Error getting top issues: {str(e)}[/yellow]")
            return []


def display_issue_analysis(data: Dict[str, Any]) -> None:
    """Display the issue analysis results."""
    console = Console()

    if "error" in data:
        console.print(f"\n[red]Error: {data['error']}[/red]")
        return

    repo = data["repository"]
    console.print(f"\n[bold cyan]Repository Information[/bold cyan]")
    console.print(f"URL: {repo['url']}")
    console.print(f"Found via: {repo['source']}")

    summary = data["summary"]
    console.print(f"\n[bold cyan]Repository Statistics[/bold cyan]")
    console.print(f"Open Issues: {summary['open_issues']}")
    console.print(f"Pull Requests: {summary['pull_requests']}")

    if data["recent_issues"]:
        console.print("\n[bold cyan]Recent Issues[/bold cyan]")
        recent_table = Table(show_header=True)
        recent_table.add_column("Title", style="yellow", width=70)

        for issue in data["recent_issues"]:
            recent_table.add_row(issue["title"])
        console.print(recent_table)

    if data["top_issues"]:
        console.print("\n[bold cyan]Most Discussed Issues[/bold cyan]")
        top_table = Table(show_header=True)
        top_table.add_column("Title", style="yellow", width=70)

        for issue in data["top_issues"]:
            top_table.add_row(issue["title"])
        console.print(top_table)
