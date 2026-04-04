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


def build_cache_tables(export_dataset):
    """Build cache tables for an ExportDataSet's core mapping and all extensions.

    Each cache table is a flat denormalized table with one column per mapped query field.
    The core table and all extension tables include an occurrenceID column for joining.
    """
    core_mapping = export_dataset.coremapping
    collection = export_dataset.collection

    # Build core cache table
    _build_single_cache(core_mapping, collection)

    # Build extension cache tables
    for ext in export_dataset.extensions.all().order_by('sortorder').iterator(chunk_size=2000):
        _build_single_cache(ext.schemamapping, collection,
                            prefix=f'dwc_cache_ext{ext.sortorder}')


def _build_single_cache(mapping, collection, prefix='dwc_cache'):
    """Build a single cache table for one SchemaMapping."""
    from specifyweb.backend.export.models import CacheTableMeta
    from django.utils import timezone

    table_name = get_cache_table_name(mapping.id, collection.id, prefix)

    # Update build status
    meta, _ = CacheTableMeta.objects.update_or_create(
        schemamapping=mapping,
        defaults={'tablename': table_name, 'buildstatus': 'building'}
    )

    try:
        # Get the query fields with terms
        fields = mapping.query.fields.all().order_by('position').iterator(chunk_size=2000)

        # Build column definitions: each field becomes a TEXT column
        # named by its term IRI (sanitized) or field name
        columns = [('occurrence_id', 'VARCHAR(256)')]  # always include occurrenceID
        for field in fields:
            col_name = _sanitize_column_name(field.term or field.fieldname)
            columns.append((col_name, 'TEXT'))

        # Create the cache table
        create_cache_table(table_name, columns)

        # TODO: Execute the query and populate the table
        # This requires integration with stored_queries.execution which
        # needs a SQLAlchemy session. For now, create the empty table.

        meta.buildstatus = 'idle'
        meta.lastbuilt = timezone.now()
        meta.rowcount = 0
        meta.save()

    except Exception as e:
        meta.buildstatus = 'error'
        meta.save()
        raise


def _sanitize_column_name(name):
    """Sanitize a string into a valid MySQL column name."""
    # Take the last segment of a URI (the term name)
    if '/' in name:
        name = name.rsplit('/', 1)[-1]
    if '#' in name:
        name = name.rsplit('#', 1)[-1]
    # Remove non-alphanumeric chars except underscore
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    return name[:64]  # MySQL column name limit


def cleanup_orphan_caches():
    """Drop cache tables that have no corresponding SchemaMapping."""
    from specifyweb.backend.export.models import CacheTableMeta, SchemaMapping

    # Find CacheTableMeta records where the schemamapping no longer exists
    orphans = CacheTableMeta.objects.filter(schemamapping__isnull=True)
    for orphan in orphans:
        drop_cache_table(orphan.tablename)
        orphan.delete()

    # Also check for cache tables in the DB that aren't tracked
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name LIKE 'dwc\\_cache\\_%' AND table_schema = DATABASE()"
        )
        db_tables = {row[0] for row in cursor.fetchall()}

    tracked_tables = set(CacheTableMeta.objects.values_list('tablename', flat=True))
    for orphan_table in db_tables - tracked_tables:
        drop_cache_table(orphan_table)


def validate_occurrence_id_uniqueness(mapping, collection):
    """Check that occurrenceID values are unique in the core cache table.

    Returns list of duplicate occurrenceIDs, or empty list if all unique.
    """
    table_name = get_cache_table_name(mapping.id, collection.id)
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', table_name)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT occurrence_id, COUNT(*) as cnt FROM `{safe_name}` '
                f'GROUP BY occurrence_id HAVING cnt > 1 LIMIT 100'
            )
            return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []
