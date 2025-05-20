from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.production.models import Order

class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.order = Order.objects.create(
            order_number='TEST001',
            customer_name='Test Customer',
            product_name='Test Product',
            quantity=100,
            status='pending',
            created_by=self.user
        )
        
        self.order_url = reverse('order-list')
        self.order_detail_url = reverse('order-detail', args=[self.order.id])
        self.change_status_url = reverse('order-change-status', args=[self.order.id])
    
    def test_create_order(self):
        data = {
            'order_number': 'TEST002',
            'customer_name': 'Test Customer 2',
            'product_name': 'Test Product 2',
            'quantity': 200,
            'status': 'pending'
        }
        response = self.client.post(self.order_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
    
    def test_get_orders(self):
        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_order_detail(self):
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_number'], 'TEST001')
    
    def test_update_order(self):
        data = {'customer_name': 'Updated Customer'}
        response = self.client.patch(self.order_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer_name'], 'Updated Customer')
    
    def test_delete_order(self):
        response = self.client.delete(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_deleted)
    
    def test_change_order_status(self):
        data = {'status': 'processing'}
        response = self.client.post(self.change_status_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'processing')
    
    def test_change_order_status_invalid(self):
        data = {'status': 'invalid_status'}
        response = self.client.post(self.change_status_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)