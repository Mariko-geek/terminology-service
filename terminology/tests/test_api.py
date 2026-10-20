from datetime import date

from django.urls import reverse
from rest_framework.test import APITestCase

from terminology.models import RefBook, RefBookElement, RefBookVersion


class TerminologyApiTests(APITestCase):
    def setUp(self):
        self.refbook = RefBook.objects.create(code='MS1', name='Специальности')
        self.v1 = RefBookVersion.objects.create(
            refbook=self.refbook,
            version='1.0',
            start_date=date(2022, 1, 1),
        )
        self.v2 = RefBookVersion.objects.create(
            refbook=self.refbook,
            version='2.0',
            start_date=date(2024, 1, 1),
        )
        RefBookElement.objects.create(version=self.v1, code='1', value='Терапевт')
        RefBookElement.objects.create(version=self.v2, code='1', value='Врач-терапевт')
        RefBookElement.objects.create(version=self.v2, code='2', value='Хирург')

        self.future_refbook = RefBook.objects.create(
            code='FUTURE',
            name='Будущий справочник',
        )
        RefBookVersion.objects.create(
            refbook=self.future_refbook,
            version='1.0',
            start_date=date(2030, 1, 1),
        )

    def test_refbook_list(self):
        response = self.client.get(reverse('refbook-list'))
        self.assertEqual(response.status_code, 200)
        codes = {item['code'] for item in response.data['refbooks']}
        self.assertIn('MS1', codes)

    def test_refbook_list_on_date_excludes_not_yet_started_refbook(self):
        response = self.client.get(
            reverse('refbook-list'),
            {'date': '2026-01-01'},
        )
        self.assertEqual(response.status_code, 200)
        codes = {item['code'] for item in response.data['refbooks']}
        self.assertIn('MS1', codes)
        self.assertNotIn('FUTURE', codes)

    def test_refbook_list_on_early_date_excludes_refbook_without_started_version(self):
        response = self.client.get(
            reverse('refbook-list'),
            {'date': '2021-12-31'},
        )
        self.assertEqual(response.status_code, 200)
        codes = {item['code'] for item in response.data['refbooks']}
        self.assertNotIn('MS1', codes)

    def test_invalid_date_returns_400(self):
        response = self.client.get(
            reverse('refbook-list'),
            {'date': '01.01.2026'},
        )
        self.assertEqual(response.status_code, 400)

    def test_elements_for_explicit_version(self):
        response = self.client.get(
            reverse('refbook-elements', args=[self.refbook.id]),
            {'version': '1.0'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['elements'],
            [{'code': '1', 'value': 'Терапевт'}],
        )

    def test_elements_without_version_use_current_version(self):
        response = self.client.get(
            reverse('refbook-elements', args=[self.refbook.id]),
        )
        self.assertEqual(response.status_code, 200)
        values = {item['value'] for item in response.data['elements']}
        self.assertEqual(values, {'Врач-терапевт', 'Хирург'})

    def test_check_element_true(self):
        response = self.client.get(
            reverse('refbook-check-element', args=[self.refbook.id]),
            {'code': '1', 'value': 'Терапевт', 'version': '1.0'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'valid': True})

    def test_check_element_false(self):
        response = self.client.get(
            reverse('refbook-check-element', args=[self.refbook.id]),
            {'code': '1', 'value': 'Хирург', 'version': '1.0'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'valid': False})

    def test_check_element_requires_code_and_value(self):
        response = self.client.get(
            reverse('refbook-check-element', args=[self.refbook.id]),
            {'code': '1'},
        )
        self.assertEqual(response.status_code, 400)


    def test_openapi_schema_is_available(self):
        response = self.client.get(reverse('schema'))
        self.assertEqual(response.status_code, 200)

