"""
Tests for basic fields and functions in the PartialIndex class.

Tests interacting with a real PostgreSQL database are elsewhere.
"""
from django.test import SimpleTestCase
from partial_index import PartialIndex
from testapp.models import AB


class PartialIndexTest(SimpleTestCase):
    """Test simple fields and methods on the PartialIndex class."""

    def setUp(self):
        self.idx = PartialIndex(fields=['a', 'b'], unique=True, where='a IS NULL')

    def test_no_unique(self):
        with self.assertRaisesMessage(ValueError, 'unique must be True or False'):
            PartialIndex(fields=['a', 'b'], where='a is null')

    def test_no_where(self):
        with self.assertRaisesMessage(ValueError, 'where predicate must be provided'):
            PartialIndex(fields=['a', 'b'], unique=True)

    def test_fields(self):
        self.assertEqual(self.idx.unique, True)
        self.assertEqual(self.idx.where, 'a IS NULL')

    def test_repr(self):
        self.assertEqual(repr(self.idx), "<PartialIndex: fields='a, b', unique=True, where='a IS NULL'>")

    def test_deconstruct(self):
        path, args, kwargs = self.idx.deconstruct()
        self.assertEqual(path, 'partial_index.PartialIndex')
        self.assertEqual((), args)
        self.assertEqual(kwargs['fields'], ['a', 'b'])
        self.assertEqual(kwargs['unique'], True)
        self.assertEqual(kwargs['where'], 'a IS NULL')
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
