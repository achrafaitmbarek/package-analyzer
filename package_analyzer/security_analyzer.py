import requests
from typing import Dict, List, Any, Optional
from packaging import version
import re


class SecurityAnalyzer:
    def __init__(self):
        self.osv_api_url = "https://api.osv.dev/v1/query"
        self.security_critical_packages = {
            "cryptography",
            "django",
            "flask",
            "requests",
            "urllib3",
            "pyopenssl",
            "paramiko",
            "pyjwt",
            "python-jose",
        }
        self.critical_keywords = {
            "remote code execution",
            "rce",
            "arbitrary code",
            "sql injection",
            "authentication bypass",
            "privilege escalation",
            "buffer overflow",
            "memory corruption",
            "denial of service",
            "information disclosure",
            "path traversal",
            "xss",
        }

    def analyze_package(
        self, package_name: str, package_version: Optional[str] = None
    ) -> Dict[str, Any]:
        vulnerabilities = self._fetch_vulnerabilities(package_name, package_version)
        return self._process_vulnerabilities(
            vulnerabilities, package_name, package_version
        )

    def _fetch_vulnerabilities(
        self, package_name: str, package_version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = {"package": {"name": package_name, "ecosystem": "PyPI"}}
        if package_version:
            query["version"] = package_version

        try:
            response = requests.post(self.osv_api_url, json=query)
            response.raise_for_status()
            return response.json().get("vulns", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch security data: {str(e)}")

    def _determine_severity(
        self, vulnerability: Dict[str, Any], package_name: str
    ) -> str:
        severity_score = 0

        # Check CVSS score
        database_specific = vulnerability.get("database_specific", {})
        if isinstance(database_specific, dict):
            cvss_score = database_specific.get("cvss_score")
            if cvss_score:
                try:
                    score = float(cvss_score)
                    severity_score += score
                except (ValueError, TypeError):
                    pass

        # Analyze vulnerability description and details
        description = (
            vulnerability.get("summary", "").lower()
            + str(vulnerability.get("details", "")).lower()
        )

        # Check for critical keywords in description
        for keyword in self.critical_keywords:
            if keyword in description:
                severity_score += 2

        # Increase severity for security-critical packages
        if package_name.lower() in self.security_critical_packages:
            severity_score += 1

        # Check for specific vulnerability types
        if any(
            kw in description
            for kw in ["cryptographic", "encryption", "authentication"]
        ):
            severity_score += 1.5

        # Evaluate impact information
        affected = vulnerability.get("affected", [])
        if affected:
            for entry in affected:
                ecosystem_specific = entry.get("ecosystem_specific", {})
                if ecosystem_specific:
                    if ecosystem_specific.get("affects_security", False):
                        severity_score += 2

        # Map final score to severity levels
        if severity_score >= 9:
            return "CRITICAL"
        elif severity_score >= 7:
            return "HIGH"
        elif severity_score >= 4:
            return "MEDIUM"
        return "LOW"

    def _process_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]],
        package_name: str,
        package_version: Optional[str],
    ) -> Dict[str, Any]:
        processed_data = {
            "total_vulnerabilities": len(vulnerabilities),
            "severity_counts": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "vulnerabilities": [],
        }

        for vuln in vulnerabilities:
            severity = self._determine_severity(vuln, package_name)
            processed_data["severity_counts"][severity] += 1

            # Extract fixed versions and references
            fixed_versions = []
            for affected in vuln.get("affected", []):
                for range_info in affected.get("ranges", []):
                    if range_info.get("type") == "ECOSYSTEM":
                        for event in range_info.get("events", []):
                            if "fixed" in event:
                                fixed_versions.append(event["fixed"])

            # Process vulnerability details
            vuln_info = {
                "id": vuln.get("id", "Unknown"),
                "severity": severity,
                "summary": vuln.get("summary", "No description available"),
                "details": vuln.get("details", ""),
                "fixed_versions": fixed_versions,
                "references": vuln.get("references", []),
                "published": vuln.get("published", "Unknown"),
                "modified": vuln.get("modified", "Unknown"),
                "ecosystem_specific": vuln.get("affected", [{}])[0].get(
                    "ecosystem_specific", {}
                ),
            }

            processed_data["vulnerabilities"].append(vuln_info)

        # Sort vulnerabilities by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        processed_data["vulnerabilities"].sort(
            key=lambda x: severity_order[x["severity"]]
        )

        return processed_data
