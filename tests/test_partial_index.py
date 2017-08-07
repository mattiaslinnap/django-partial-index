"""
Tests for basic fields and functions in the PartialIndex class.

Tests interacting with a real PostgreSQL database are elsewhere.
"""
from django.test import SimpleTestCase
from partial_index import PartialIndex
from testapp.models import AB


class PartialIndexWhereRulesTest(SimpleTestCase):
    """Test the rules for providing where arguments."""

    def test_no_where(self):
        with self.assertRaisesMessage(ValueError, 'At least one where predicate must be provided'):
            PartialIndex(fields=['a', 'b'], unique=True)

    def test_single_and_pg_where_same(self):
        with self.assertRaisesRegexp(ValueError, '^If providing a single'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_postgresql='a IS NULL')

    def test_single_and_pg_where_different(self):
        with self.assertRaisesRegexp(ValueError, '^If providing a single'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_postgresql='a IS NOT NULL')

    def test_single_and_sqlite_where_same(self):
        with self.assertRaisesRegexp(ValueError, '^If providing a single'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_sqlite='a IS NULL')

    def test_single_and_sqlite_where_different(self):
        with self.assertRaisesRegexp(ValueError, '^If providing a single'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_sqlite='a IS NOT NULL')

    def test_all_where_same(self):
        with self.assertRaisesRegexp(ValueError, '^If providing a single'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_postgresql='a IS NULL', where_sqlite='a IS NULL')

    def test_all_where_different(self):
        with self.assertRaisesRegexp(ValueError, '^If providing a single'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_postgresql='a IS NOT NULL', where_sqlite='a = 3')

    def test_pg_and_sqlite_where_same(self):
        with self.assertRaisesRegexp(ValueError, '^If providing a separate'):
            PartialIndex(fields=['a', 'b'], unique=True, where_postgresql='a IS NULL', where_sqlite='a IS NULL')


class PartialIndexSingleWhereTest(SimpleTestCase):
    """Test simple fields and methods on the PartialIndex class."""

    def setUp(self):
        self.idx = PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL')

    def test_no_unique(self):
        with self.assertRaisesMessage(ValueError, 'Unique must be True or False'):
            PartialIndex(fields=['a', 'b'], where='a is null')

    def test_fields(self):
        self.assertEqual(self.idx.unique, True)
        self.assertEqual(self.idx.where, 'a IS NULL')
        self.assertEqual(self.idx.where_postgresql, '')
        self.assertEqual(self.idx.where_sqlite, '')

    def test_repr(self):
        self.assertEqual(repr(self.idx), "<PartialIndex: fields='a, b', unique=True, where='a IS NULL'>")

    def test_deconstruct(self):
        path, args, kwargs = self.idx.deconstruct()
        self.assertEqual(path, 'partial_index.PartialIndex')
        self.assertEqual((), args)
        self.assertEqual(kwargs['fields'], ['a', 'b'])
        self.assertEqual(kwargs['unique'], True)
        self.assertEqual(kwargs['where'], 'a IS NULL')
        self.assertEqual(kwargs['where_postgresql'], '')
        self.assertEqual(kwargs['where_sqlite'], '')
        self.assertIn('name', kwargs)  # Exact value of name is not tested.

    def test_suffix(self):
        self.assertEqual(self.idx.suffix, 'partial')

    def test_generated_name_ends_with_partial(self):
        idx = PartialIndex(fields=['a', 'b'], unique=False, where='a IS NULL')
        idx.set_name_with_model(AB)
        self.assertEqual(idx.name[-8:], '_partial')

    def test_field_sort_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where='a IS NULL')
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', '-b'], unique=False, where='a IS NULL')
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)

    def test_field_order_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where='a IS NULL')
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['b', 'a'], unique=False, where='a IS NULL')
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)

    def test_unique_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where='a IS NULL')
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL')
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)

    def test_where_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where='a IS NULL')
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', 'b'], unique=False, where='a IS NOT NULL')
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)


class PartialIndexMultiWhereTest(SimpleTestCase):
    """Test simple fields and methods on the PartialIndex class with separate where_vendor='' arguments."""

    def setUp(self):
        self.idx = PartialIndex(fields=['a', 'b'], unique=True, where_postgresql='a = false', where_sqlite='a = 0')

    def test_no_unique(self):
        with self.assertRaisesMessage(ValueError, 'Unique must be True or False'):
            PartialIndex(fields=['a', 'b'], where_postgresql='a = false', where_sqlite='a = 0')

    def test_fields(self):
        self.assertEqual(self.idx.unique, True)
        self.assertEqual(self.idx.where, '')
        self.assertEqual(self.idx.where_postgresql, 'a = false')
        self.assertEqual(self.idx.where_sqlite, 'a = 0')

    def test_repr(self):
        self.assertEqual(repr(self.idx), "<PartialIndex: fields='a, b', unique=True, where_postgresql='a = false', where_sqlite='a = 0'>")

    def test_deconstruct(self):
        path, args, kwargs = self.idx.deconstruct()
        self.assertEqual(path, 'partial_index.PartialIndex')
        self.assertEqual((), args)
        self.assertEqual(kwargs['fields'], ['a', 'b'])
        self.assertEqual(kwargs['unique'], True)
        self.assertEqual(kwargs['where'], '')
        self.assertEqual(kwargs['where_postgresql'], 'a = false')
        self.assertEqual(kwargs['where_sqlite'], 'a = 0')
        self.assertIn('name', kwargs)  # Exact value of name is not tested.

    def test_suffix(self):
        self.assertEqual(self.idx.suffix, 'partial')

    def test_generated_name_ends_with_partial(self):
        idx = PartialIndex(fields=['a', 'b'], unique=False, where_postgresql='a = false', where_sqlite='a = 0')
        idx.set_name_with_model(AB)
        self.assertEqual(idx.name[-8:], '_partial')

    def test_where_postgresql_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where_postgresql='a = false', where_sqlite='a = 0')
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', 'b'], unique=False, where_postgresql='a = true', where_sqlite='a = 0')
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)

    def test_where_sqlite_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where_postgresql='a = false', where_sqlite='a = 0')
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', 'b'], unique=False, where_postgresql='a = false', where_sqlite='a = 1')
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)
