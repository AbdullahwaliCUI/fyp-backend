import pytest
from django.db import connection


@pytest.mark.django_db
class TestDatabaseConnection:
    def test_database_connection(self):
        # Check if database connection is usable
        assert connection.is_usable() is True

    def test_simple_raw_query(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            assert row[0] == 1

    def test_database_can_execute_basic_query(self):
        # Execute a simple query to test DB
        with connection.cursor() as cursor:
            cursor.execute("SELECT CURRENT_DATE")
            result = cursor.fetchone()
            assert result is not None
