import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import re
from datetime import datetime


class StatsAnalyzer:
    def __init__(self):
        self.base_url = "https://pypi.org/project"

    def fetch_package_stats(self, package_name: str) -> Dict[str, Any]:
        """
        Fetch and analyze package statistics from PyPI.
        """
        url = f"{self.base_url}/{package_name}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            stats = {
                "releases": self._extract_release_history(soup),
                "maintainers": self._extract_maintainers(soup),
                "project_status": self._extract_project_status(soup),
                "python_versions": self._extract_python_versions(soup),
            }

            return stats

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch package statistics: {str(e)}")

    def _extract_release_history(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract release history information."""
        releases = []
        release_timeline = soup.find("div", class_="release-timeline")

        if release_timeline:
            for release in release_timeline.find_all("div", class_="release"):
                version = release.find("p", class_="release__version")
                date = release.find("time")

                if version and date:
                    release_info = {
                        "version": version.text.strip(),
                        "date": date.get("datetime"),
                        "is_prerelease": bool(
                            release.find("span", class_="badge--warning")
                        ),
                        "is_yanked": bool(release.find("span", class_="badge--danger")),
                    }
                    releases.append(release_info)

        return {
            "total_releases": len(releases),
            "latest_release": releases[0] if releases else None,
            "release_history": releases[:5],  # Latest 5 releases
        }

    def _extract_maintainers(self, soup: BeautifulSoup) -> list:
        """Extract maintainer information."""
        maintainers = []
        maintainers_section = soup.find(
            "div", class_="sidebar-section", h6=lambda x: x and "Maintainers" in x.text
        )

        if maintainers_section:
            for maintainer in maintainers_section.find_all(
                "span", class_="sidebar-section__maintainer"
            ):
                maintainer_link = maintainer.find("a")
                if maintainer_link:
                    maintainers.append(
                        {
                            "username": maintainer_link.text.strip(),
                            "profile_url": f"https://pypi.org{maintainer_link['href']}",
                        }
                    )

        return maintainers

    def _extract_project_status(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract project status information."""
        status = {}

        # Extract development status
        classifiers = soup.find("ul", class_="sidebar-section__classifiers")
        if classifiers:
            dev_status = classifiers.find("strong", string="Development Status")
            if dev_status:
                status_li = dev_status.find_next("li")
                if status_li:
                    status["development_status"] = status_li.text.strip()

        # Extract license type
        license_section = soup.find("strong", string="License")
        if license_section:
            license_text = license_section.find_parent("li")
            if license_text:
                status["license_type"] = license_text.text.replace(
                    "License:", ""
                ).strip()

        return status

    def _extract_python_versions(self, soup: BeautifulSoup) -> list:
        """Extract supported Python versions."""
        versions = []
        classifiers = soup.find("ul", class_="sidebar-section__classifiers")

        if classifiers:
            python_section = classifiers.find("strong", string="Programming Language")
            if python_section:
                version_list = python_section.find_next("ul")
                if version_list:
                    for version in version_list.find_all("li"):
                        version_text = version.text.strip()
                        if "Python" in version_text and not any(
                            x in version_text for x in ["Implementation", ":: 3 ::"]
                        ):
                            versions.append(
                                version_text.replace("Python ::", "").strip()
                            )

        return versions
