# HubQueue

A command-line interface for GitHub tools.

## Installation

Clone the repository and install the package:

```bash
git clone https://github.com/yourusername/hubqueue.git
cd hubqueue
pip install -e .
```

## Configuration

You can configure HubQueue in two ways:

1. Set the `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_github_token
```

2. Create a configuration file:

```bash
mkdir -p ~/.hubqueue
echo '{"github_token": "your_github_token"}' > ~/.hubqueue/config.json
```

## Usage

### List Issues

```bash
hubqueue list-issues --repo owner/repo
```

### List Pull Requests

```bash
hubqueue list-prs --repo owner/repo
```

## Development

### Setup Development Environment

```bash
# Create and activate virtual environment
python -m venv venv_hubqueue
source venv_hubqueue/bin/activate  # On Windows: venv_hubqueue\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

[MIT](LICENSE)
