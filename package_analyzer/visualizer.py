from graphviz import Digraph
import requests
from typing import Dict, Set, Any
import json


def create_dependency_graph(package_name: str, max_depth: int = 2) -> Digraph:
    """
    Create a dependency graph for the specified package.

    Args:
        package_name: Name of the package to analyze
        max_depth: Maximum depth of dependencies to analyze

    Returns:
        Graphviz Digraph object
    """
    dot = Digraph(comment=f"Dependency Graph for {package_name}")
    dot.attr(rankdir="LR")

    # Set node styles
    dot.attr("node", shape="box", style="rounded,filled", fillcolor="lightblue")

    # Track visited packages to avoid cycles
    visited = set()

    def fetch_package_info(pkg_name: str) -> Dict[str, Any]:
        response = requests.get(f"https://pypi.org/pypi/{pkg_name}/json")
        response.raise_for_status()
        return response.json()

    def add_dependencies(pkg_name: str, current_depth: int = 0):
        if current_depth >= max_depth or pkg_name in visited:
            return

        visited.add(pkg_name)

        try:
            data = fetch_package_info(pkg_name)
            requires_dist = data["info"].get("requires_dist", [])

            # Add the current package node
            dot.node(pkg_name, f"{pkg_name}\n{data['info'].get('version', 'unknown')}")

            if requires_dist:
                for dep in requires_dist:
                    if dep:
                        # Extract base package name without version specifiers
                        dep_name = dep.split(" ")[0].split(";")[0].strip()
                        if dep_name:
                            # Add dependency node and edge
                            dot.edge(pkg_name, dep_name)
                            if dep_name not in visited:
                                add_dependencies(dep_name, current_depth + 1)

        except requests.exceptions.RequestException:
            # If we can't fetch package info, just add the node without dependencies
            dot.node(pkg_name, pkg_name, fillcolor="lightgray")

    # Start building the graph from the root package
    add_dependencies(package_name)
    return dot


def save_dependency_graph(
    package_name: str, max_depth: int = 2, output_format: str = "png"
) -> str:
    """
    Generate and save the dependency graph.

    Args:
        package_name: Name of the package to analyze
        max_depth: Maximum depth of dependencies to analyze
        output_format: Output file format (pdf, png, svg)

    Returns:
        Path to the generated graph file
    """
    graph = create_dependency_graph(package_name, max_depth)
    filename = f"{package_name}_dependencies"
    graph.render(filename, format=output_format, cleanup=True)
    return f"{filename}.{output_format}"
