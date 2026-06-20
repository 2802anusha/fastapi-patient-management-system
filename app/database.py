"""
Database configuration module.

Currently using JSON file storage. This module is a placeholder
for future migration to SQLAlchemy + SQLite.

Future setup will include:
- SQLAlchemy engine and session
- Base class for ORM models
- Dependency injection for DB sessions
"""

import json
import os

# Path to the JSON file (relative to where the app is run from)
JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patients.json')


def load_data():
    """Load patient data from the JSON file."""
    with open(JSON_FILE_PATH, 'r') as f:
        data = json.load(f)
    return data


def save_data(data):
    """Save patient data to the JSON file."""
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(data, f)
