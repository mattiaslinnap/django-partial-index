"""
Tests for basic fields and functions in the PartialIndex class.

Tests interacting with a real PostgreSQL database are elsewhere.
"""

from django.test import SimpleTestCase

from partial_index import PartialIndex, PQ
from testapp.models import AB


class PartialIndexTextBasedWhereRulesTest(SimpleTestCase):
    """Test the rules for providing text-based where arguments."""

    def test_where_not_provided(self):
        with self.assertRaisesRegexp(ValueError, 'must be provided'):
            PartialIndex(fields=['a', 'b'], unique=True)

    def test_single_and_pg_where_same(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_postgresql='a IS NULL')

    def test_single_and_pg_where_different(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_postgresql='a IS NOT NULL')

    def test_single_and_sqlite_where_same(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_sqlite='a IS NULL')

    def test_single_and_sqlite_where_different(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_sqlite='a IS NOT NULL')

    def test_all_where_same(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_postgresql='a IS NULL', where_sqlite='a IS NULL')

    def test_all_where_different(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL', where_postgresql='a IS NOT NULL', where_sqlite='a = 3')

    def test_pg_and_sqlite_where_same(self):
        with self.assertRaisesRegexp(ValueError, 'must be different'):
            PartialIndex(fields=['a', 'b'], unique=True, where_postgresql='a IS NULL', where_sqlite='a IS NULL')


class PartialIndexPQBasedWhereRulesTest(SimpleTestCase):
    """Test the rules for providing PQ-based where arguments."""

    def test_where_not_provided(self):
        # Same as text based test - keep a copy here for the future when text-based are removed entirely.
        with self.assertRaisesRegexp(ValueError, 'must be provided'):
            PartialIndex(fields=['a', 'b'], unique=True)

    def test_single_q_and_pg(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where=PQ(a__isnull=True), where_postgresql='a IS NULL')

    def test_single_q_and_sqlite(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where=PQ(a__isnull=True), where_sqlite='a IS NULL')

    def test_single_q_and_pg_and_sqlite(self):
        with self.assertRaisesRegexp(ValueError, 'must not provide'):
            PartialIndex(fields=['a', 'b'], unique=True, where=PQ(a__isnull=True), where_postgresql='a IS NULL', where_sqlite='a IS NULL')


class PartialIndexSingleTextWhereTest(SimpleTestCase):
    """Test simple fields and methods on the PartialIndex class with a single text-based where predicate."""

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
        self.assertNotIn('where_postgresql', kwargs)
        self.assertNotIn('where_sqlite', kwargs)
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


class PartialIndexMultiTextWhereTest(SimpleTestCase):
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
        self.assertNotIn('where', kwargs)
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


class PartialIndexSinglePQWhereTest(SimpleTestCase):
    """Test simple fields and methods on the PartialIndex class with a Q-based where predicate."""

    def setUp(self):
        self.idx = PartialIndex(fields=['a', 'b'], unique=True, where=PQ(a__isnull=True))

    def test_no_unique(self):
        with self.assertRaisesMessage(ValueError, 'Unique must be True or False'):
            PartialIndex(fields=['a', 'b'], where=PQ(a__isnull=True))

    def test_fields(self):
        self.assertEqual(self.idx.unique, True)
        self.assertEqual(self.idx.where, PQ(a__isnull=True))
        self.assertEqual(self.idx.where_postgresql, '')
        self.assertEqual(self.idx.where_sqlite, '')

    def test_repr(self):
        self.assertEqual(repr(self.idx), "<PartialIndex: fields='a, b', unique=True, where=<PQ: (AND: ('a__isnull', True))>>")

    def test_deconstruct_pq(self):
        path, args, kwargs = self.idx.deconstruct()
        self.assertEqual(path, 'partial_index.PartialIndex')
        self.assertEqual((), args)
        self.assertEqual(kwargs['fields'], ['a', 'b'])
        self.assertEqual(kwargs['unique'], True)
        self.assertEqual(kwargs['where'], PQ(a__isnull=True))
        self.assertNotIn('where_postgresql', kwargs)
        self.assertNotIn('where_sqlite', kwargs)
        self.assertIn('name', kwargs)  # Exact value of name is not tested.

    def test_suffix(self):
        self.assertEqual(self.idx.suffix, 'partial')

    def test_generated_name_ends_with_partial(self):
        idx = PartialIndex(fields=['a', 'b'], unique=False, where=PQ(a__isnull=True))
        idx.set_name_with_model(AB)
        self.assertEqual(idx.name[-8:], '_partial')

    def test_same_args_same_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where=PQ(a__isnull=True))
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', 'b'], unique=False, where=PQ(a__isnull=True))
        idx2.set_name_with_model(AB)
        self.assertEqual(idx1.name, idx2.name)

    def test_field_sort_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where=PQ(a__isnull=True))
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', '-b'], unique=False, where=PQ(a__isnull=True))
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)

    def test_field_order_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where=PQ(a__isnull=True))
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['b', 'a'], unique=False, where=PQ(a__isnull=True))
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)

    def test_unique_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where=PQ(a__isnull=True))
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', 'b'], unique=True, where=PQ(a__isnull=True))
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)

    def test_where_changes_generated_name(self):
        idx1 = PartialIndex(fields=['a', 'b'], unique=False, where=PQ(a__isnull=True))
        idx1.set_name_with_model(AB)
        idx2 = PartialIndex(fields=['a', 'b'], unique=False, where=PQ(a__isnull=False))
        idx2.set_name_with_model(AB)
        self.assertNotEqual(idx1.name, idx2.name)
