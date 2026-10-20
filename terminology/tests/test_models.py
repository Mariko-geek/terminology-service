from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from terminology.models import RefBook, RefBookElement, RefBookVersion


class RefBookModelTests(TestCase):
    def setUp(self):
        self.refbook = RefBook.objects.create(code='TEST', name='Тестовый справочник')
        self.v1 = RefBookVersion.objects.create(
            refbook=self.refbook,
            version='1.0',
            start_date=date(2024, 1, 1),
        )
        self.v2 = RefBookVersion.objects.create(
            refbook=self.refbook,
            version='2.0',
            start_date=date(2025, 1, 1),
        )
        self.future = RefBookVersion.objects.create(
            refbook=self.refbook,
            version='3.0',
            start_date=date(2030, 1, 1),
        )

    def test_version_for_date_selects_latest_started_version(self):
        self.assertEqual(
            self.refbook.version_for_date(date(2024, 6, 1)),
            self.v1,
        )
        self.assertEqual(
            self.refbook.version_for_date(date(2026, 1, 1)),
            self.v2,
        )

    def test_future_version_is_not_effective_earlier(self):
        self.assertNotEqual(
            self.refbook.version_for_date(date(2026, 1, 1)),
            self.future,
        )

    def test_refbook_code_is_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RefBook.objects.create(code='TEST', name='Дубликат')

    def test_version_name_is_unique_inside_refbook(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RefBookVersion.objects.create(
                refbook=self.refbook,
                version='1.0',
                start_date=date(2027, 1, 1),
            )

    def test_start_date_is_unique_inside_refbook(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RefBookVersion.objects.create(
                refbook=self.refbook,
                version='1.1',
                start_date=date(2024, 1, 1),
            )

    def test_element_code_is_unique_inside_version(self):
        RefBookElement.objects.create(version=self.v1, code='A', value='Значение')
        with self.assertRaises(IntegrityError), transaction.atomic():
            RefBookElement.objects.create(version=self.v1, code='A', value='Другое значение')
