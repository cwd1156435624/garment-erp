from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.production.models import ProductionOrder
import json

class OrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'order_number': 'PO-2023-001',
            'product_code': 'P-1001',
            'quantity': 100,
            'due_date': '2023-12-31'
        }

    def test_create_order_with_missing_fields(self):
        url = '/api/production/orders/'
        invalid_data = self.valid_payload.copy()
        del invalid_data['product_code']
        
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('product_code' in response.data['errors'])

    def test_update_order_with_invalid_status(self):
        order = ProductionOrder.objects.create(**self.valid_payload)
        url = f'/api/production/orders/{order.id}/'
        
        response = self.client.patch(url, {'status': 'INVALID_STATUS'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('invalid_choice', response.data['status'][0].code)

    def test_delete_completed_order(self):
        order = ProductionOrder.objects.create(**self.valid_payload, status='COMPLETED')
        url = f'/api/production/orders/{order.id}/'
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('completed', response.data['detail'])