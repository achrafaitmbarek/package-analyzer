import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional


def fetch_package_info(
    package_name: str, version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch comprehensive package information combining API data and web scraping.

    Args:
        package_name: Name of the package to analyze
        version: Specific version to analyze (optional)

    Returns:
        Dict containing package information
    """
    # Fetch data from PyPI API
    api_data = _fetch_api_data(package_name, version)

    # Enhance with web-scraped data
    web_data = _scrape_pypi_page(package_name, version)

    # Combine the data
    return {**api_data, **web_data}


def _fetch_api_data(package_name: str, version: Optional[str] = None) -> Dict[str, Any]:
    """Fetch basic package information from PyPI JSON API."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    info = data["info"]
    return {
        "name": package_name,
        "version": version or info["version"],
        "author": info.get("author", "Unknown"),
        "license": info.get("license", "Not specified"),
        "description": info.get("summary", "No description available"),
        "homepage": info.get("home_page", "Not available"),
        "documentation": info.get("docs_url", "Not available"),
        "requires_python": info.get("requires_python", "Not specified"),
        "dependencies": _extract_dependencies(data, version),
    }


def _scrape_pypi_page(
    package_name: str, version: Optional[str] = None
) -> Dict[str, Any]:
    """Scrape additional information from PyPI project page."""
    url = f"https://pypi.org/project/{package_name}"
    if version:
        url += f"/{version}"

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    return {
        "installation_guide": _extract_installation_guide(soup),
        "latest_releases": _extract_latest_releases(soup),
        "project_stats": _extract_project_stats(soup),
        "community_info": _extract_community_info(soup),
    }


def _extract_installation_guide(soup: BeautifulSoup) -> str:
    """Extract installation instructions."""
    install_div = soup.find("span", {"class": "package-header__pip-instructions"})
    return install_div.text.strip() if install_div else "pip install {package_name}"


def _extract_latest_releases(soup: BeautifulSoup) -> list:
    """Extract recent release information."""
    releases = []
    release_divs = soup.find_all("a", {"class": "release__card"})
    for release in release_divs[:5]:  # Get last 5 releases
        version = release.find("p", {"class": "release__version"})
        if version:
            releases.append(version.text.strip())
    return releases


def _extract_project_stats(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract project statistics."""
    stats = {}
    stats_div = soup.find("div", {"class": "package-header__stats"})
    if stats_div:
        for stat in stats_div.find_all("p"):
            name = stat.find("span", {"class": "package-header__stat-name"})
            value = stat.find("span", {"class": "package-header__stat-value"})
            if name and value:
                stats[name.text.strip()] = value.text.strip()
    return stats


def _extract_community_info(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract community-related information."""
    info = {}

    # Extract maintainers
    maintainers = []
    maintainers_div = soup.find("div", {"class": "maintainers"})
    if maintainers_div:
        maintainers = [
            m.text.strip()
            for m in maintainers_div.find_all("span", {"class": "maintainer"})
        ]
    info["maintainers"] = maintainers

    return info


def _extract_dependencies(data: Dict[str, Any], version: Optional[str] = None) -> list:
    """Extract package dependencies."""
    if version and version in data.get("releases", {}):
        release_data = data["releases"][version]
    else:
        version = data["info"]["version"]
        release_data = data["releases"].get(version, [])

    requires_dist = data["info"].get("requires_dist", [])
    if requires_dist:
        return [dep.split(";")[0].strip() for dep in requires_dist if dep]
    return []
