

```bash
# Basic analysis with table output
python -m package_analyzer requests


python -m package_analyzer requests --version 2.31.0


python -m package_analyzer requests --format json
```

```bash

python -m package_analyzer requests --security

python -m package_analyzer requests --security --save
```

Dependency Visualization:
```bash
python -m package_analyzer requests --graph

python -m package_analyzer requests --graph --depth 3

python -m package_analyzer requests --graph --graph-format svg
```

```bash
# Comprehensive analysis with all features
python -m package_analyzer requests --security --graph --format table --save

# Custom analysis with specific version and depth
python -m package_analyzer django --version 4.2 --security --graph --depth 2
```
