"""Tests for `cli_finance` package."""

import pytest

from cli_finance import utils


@pytest.fixture(autouse=True)
def mock_db_path(tmp_path, monkeypatch):
    """Fixture to override the database path for tests to avoid touching real user data."""
    db_file = tmp_path / "test_records.db"
    # Patch the DB path inside utils
    monkeypatch.setattr(utils, "DB", str(db_file))

    # Initialize the database schema for the temporary test database
    utils.init_()
    return db_file

def test_add_and_get_records():
    """Verify that adding records correctly sums up income and expenses."""
    # Ensure fresh DB returns None
    inc, exp, _ = utils.get_records()
    assert inc is None
    assert exp is None

    # Add records
    utils.add_record('Income', 'Salary', 1000.0)
    utils.add_record('Expense', 'Rent', 500.0)
    utils.add_record('Expense', 'Grocery', 50.0)

    # Retrieve and check sums
    inc, exp, _ = utils.get_records()
    assert inc == 1000.0
    assert exp == 550.0

def test_delete_all(monkeypatch):
    """Verify that deleting all data functions properly."""
    # Mock the Prompt.ask call inside delete_all to automatically return 'Confirm'
    monkeypatch.setattr(utils.Prompt, "ask", lambda *args, **kwargs: "Confirm")

    utils.add_record('Income', 'Salary', 500.0)

    inc, exp, _ = utils.get_records()
    assert inc == 500.0

    # Trigger delete all
    utils.delete_all()

    inc, exp, _ = utils.get_records()
    assert inc is None
