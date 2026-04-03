from django.db import IntegrityError
from django.test import TestCase

from specifyweb.specify.tests.test_api import MainSetupTearDown
from specifyweb.specify.models import Spquery, Spqueryfield
from specifyweb.backend.export.models import SchemaMapping


class SchemaMappingTests(MainSetupTearDown, TestCase):

    def _make_query(self, name='test query'):
        return Spquery.objects.create(
            name=name,
            contextname='CollectionObject',
            contexttableid=1,
            createdbyagent=self.agent,
            specifyuser=self.specifyuser,
        )

    def test_create_schema_mapping(self):
        query = self._make_query()
        mapping = SchemaMapping.objects.create(
            query=query,
            mappingtype='Core',
            name='DwC Core Mapping',
            createdbyagent=self.agent,
        )
        mapping.refresh_from_db()
        self.assertEqual(mapping.query_id, query.pk)
        self.assertEqual(mapping.mappingtype, 'Core')
        self.assertEqual(mapping.name, 'DwC Core Mapping')
        self.assertFalse(mapping.isdefault)

    def test_schema_mapping_query_onetoone(self):
        query = self._make_query()
        SchemaMapping.objects.create(
            query=query,
            mappingtype='Core',
            name='First',
        )
        with self.assertRaises(IntegrityError):
            SchemaMapping.objects.create(
                query=query,
                mappingtype='Extension',
                name='Second',
            )

    def test_schema_mapping_cascade_delete(self):
        query = self._make_query()
        SchemaMapping.objects.create(
            query=query,
            mappingtype='Core',
            name='Cascade Test',
        )
        self.assertEqual(SchemaMapping.objects.count(), 1)
        query.delete()
        self.assertEqual(SchemaMapping.objects.count(), 0)

    def test_spqueryfield_term_nullable(self):
        query = self._make_query()

        # Field without DwC term — backward compatible
        field_no_term = Spqueryfield.objects.create(
            query=query,
            fieldname='catalogNumber',
            operstart=0,
            sorttype=0,
            position=0,
            startvalue='',
            stringid='1.collectionobject.catalogNumber',
            tablelist='1',
        )
        field_no_term.refresh_from_db()
        self.assertIsNone(field_no_term.term)
        self.assertFalse(field_no_term.isstatic)
        self.assertIsNone(field_no_term.staticvalue)

        # Field with DwC term
        field_with_term = Spqueryfield.objects.create(
            query=query,
            fieldname='catalogNumber',
            operstart=0,
            sorttype=0,
            position=1,
            startvalue='',
            stringid='1.collectionobject.catalogNumber',
            tablelist='1',
            term='http://rs.tdwg.org/dwc/terms/catalogNumber',
            isstatic=False,
        )
        field_with_term.refresh_from_db()
        self.assertEqual(
            field_with_term.term,
            'http://rs.tdwg.org/dwc/terms/catalogNumber',
        )

        # Static field
        field_static = Spqueryfield.objects.create(
            query=query,
            fieldname='catalogNumber',
            operstart=0,
            sorttype=0,
            position=2,
            startvalue='',
            stringid='1.collectionobject.catalogNumber',
            tablelist='1',
            term='http://rs.tdwg.org/dwc/terms/basisOfRecord',
            isstatic=True,
            staticvalue='PreservedSpecimen',
        )
        field_static.refresh_from_db()
        self.assertTrue(field_static.isstatic)
        self.assertEqual(field_static.staticvalue, 'PreservedSpecimen')
