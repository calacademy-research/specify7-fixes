from django.db import connection
from django.test import TestCase

from specifyweb.backend.export.cache import (
    create_cache_table, drop_cache_table, get_cache_table_name,
)


class CacheTableNameTests(TestCase):

    def test_cache_table_name_generation(self):
        name = get_cache_table_name(5, 4)
        self.assertEqual(name, 'dwc_cache_5_4')

    def test_cache_table_name_sanitization(self):
        # Special chars in prefix are not stripped by get_cache_table_name,
        # but create_cache_table sanitizes the full name.
        name = get_cache_table_name(1, 2, prefix='bad;prefix')
        # create_cache_table will strip the semicolon
        self.assertIn('bad', name)


class CacheTableOperationsTests(TestCase):

    def _table_exists(self, name):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_name = %s", [name]
            )
            return cursor.fetchone()[0] > 0

    def test_create_and_drop_cache_table(self):
        table_name = 'dwc_cache_test_99'
        columns = [('id', 'INT'), ('val', 'VARCHAR(128)')]
        create_cache_table(table_name, columns)
        self.assertTrue(self._table_exists(table_name))

        drop_cache_table(table_name)
        self.assertFalse(self._table_exists(table_name))

    def test_cache_table_name_sanitization_in_create(self):
        # Semicolons and other special chars are stripped
        dirty_name = 'test;drop--table'
        columns = [('id', 'INT')]
        create_cache_table(dirty_name, columns)
        safe_name = 'testdroptable'
        self.assertTrue(self._table_exists(safe_name))
        drop_cache_table(safe_name)
