"""Cache table operations for DwC export pipeline."""
import logging
import re
from django.db import connection

logger = logging.getLogger(__name__)


def get_cache_table_name(mapping_id, collection_id, prefix='dwc_cache'):
    """Generate a safe cache table name."""
    return f'{prefix}_{mapping_id}_{collection_id}'


def create_cache_table(table_name, columns):
    """Create a cache table with the given columns.

    columns: list of (column_name, column_type) tuples
    """
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', table_name)
    col_defs = ', '.join(
        f'`{re.sub(r"[^a-zA-Z0-9_]", "", name)}` {col_type}'
        for name, col_type in columns
    )
    with connection.cursor() as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS `{safe_name}`')
        cursor.execute(f'CREATE TABLE `{safe_name}` ({col_defs})')
    logger.info('Created cache table %s', safe_name)


def drop_cache_table(table_name):
    """Drop a cache table if it exists."""
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', table_name)
    with connection.cursor() as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS `{safe_name}`')
    logger.info('Dropped cache table %s', safe_name)


def insert_into_cache(table_name, select_sql, params=None):
    """Populate a cache table from a SELECT query."""
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', table_name)
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO `{safe_name}` {select_sql}', params or [])
        return cursor.rowcount
