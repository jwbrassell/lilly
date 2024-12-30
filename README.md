# Local Development Hub

A Flask-based local development hub that helps you manage git repositories, hosts, and markdown notes. Features include:

- Git repository tracking
- Host management (servers, development machines, etc.)
- Markdown notes with:
  - TinyMCE rich text editor
  - Code syntax highlighting
  - Mermaid diagram support
  - Full-text search
- HashiCorp Vault integration for secure storage

## Requirements

- Python 3.8+
- pip (Python package manager)
- macOS (for the current setup script)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd <repo-directory>
```

2. Run the setup script:
```bash
./setup.sh
```

This will:
- Install required Python packages
- Download and install HashiCorp Vault
- Initialize Vault in development mode
- Create necessary environment variables
- Initialize the database

## Usage

1. Start the Flask application:
```bash
flask run
```

The application will be available at:
- Flask App: http://localhost:5010
- Vault UI: http://localhost:5011/ui

## Features

### Git Repositories
- Track your git repositories
- Store repository URLs and descriptions
- Quick access to repository information

### Hosts
- Manage your development machines and servers
- Store hostnames, IP addresses, and SSH usernames
- Quick reference for SSH connections

### Notes
- Create and edit notes with a rich text editor
- Support for Markdown formatting
- Code syntax highlighting for multiple languages
- Mermaid diagram support for creating:
  - Flowcharts
  - Sequence diagrams
  - Entity relationship diagrams
  - And more
- Full-text search across all notes

### Vault Integration
- Secure storage using HashiCorp Vault
- Local-only access (no external connections)
- Development mode for easy setup

## Directory Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── setup.sh           # Setup script
├── static/            # Static files (TinyMCE, etc.)
└── templates/         # HTML templates
    ├── base.html      # Base template
    ├── index.html     # Homepage
    ├── repos/         # Git repository templates
    ├── hosts/         # Host management templates
    └── notes/         # Note management templates
```

## Development

The application uses:
- Flask for the web framework
- SQLAlchemy for database management
- TinyMCE for the rich text editor
- markdown2 for Markdown rendering
- Mermaid for diagrams
- Bootstrap for styling

## Security Notes

This application is designed for local use only. It:
- Runs without HTTPS
- Uses Vault in development mode
- Stores data in a local SQLite database

Do not expose this application to the internet or use it in a production environment without proper security measures.
