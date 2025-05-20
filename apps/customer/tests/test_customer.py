from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.customer.models import Customer

class CustomerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.customer = Customer.objects.create(
            name='Test Customer',
            contact_person='John Doe',
            phone='1234567890',
            email='test@example.com',
            address='Test Address'
        )
        
        self.customer_url = reverse('customer-list')
        self.customer_detail_url = reverse('customer-detail', args=[self.customer.id])
    
    def test_create_customer(self):
        data = {
            'name': 'New Customer',
            'contact_person': 'Jane Doe',
            'phone': '0987654321',
            'email': 'new@example.com',
            'address': 'New Address'
        }
        response = self.client.post(self.customer_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
    
    def test_get_customers(self):
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_customer_detail(self):
        response = self.client.get(self.customer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Customer')
    
    def test_update_customer(self):
        data = {'name': 'Updated Customer'}
        response = self.client.patch(self.customer_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Customer')
    
    def test_delete_customer(self):
        response = self.client.delete(self.customer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_deleted)
    
    def test_search_customer(self):
        response = self.client.get(f'{self.customer_url}?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Customer')
    
    def test_filter_customer_by_email(self):
        response = self.client.get(f'{self.customer_url}?email=test@example.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'test@example.com')