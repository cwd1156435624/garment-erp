from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.production.models import ProductionException

class ProductionExceptionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.exception = ProductionException.objects.create(
            title='Test Exception',
            description='Test Description',
            severity='high',
            status='pending',
            reported_by=self.user
        )
        
        self.exception_url = reverse('productionexception-list')
        self.exception_detail_url = reverse('productionexception-detail', args=[self.exception.id])
        self.resolve_exception_url = reverse('productionexception-resolve-exception', args=[self.exception.id])
    
    def test_create_exception(self):
        data = {
            'title': 'New Exception',
            'description': 'New Description',
            'severity': 'medium',
            'status': 'pending'
        }
        response = self.client.post(self.exception_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductionException.objects.count(), 2)
    
    def test_get_exceptions(self):
        response = self.client.get(self.exception_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_exception_detail(self):
        response = self.client.get(self.exception_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Exception')
    
    def test_update_exception(self):
        data = {'description': 'Updated Description'}
        response = self.client.patch(self.exception_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated Description')
    
    def test_delete_exception(self):
        response = self.client.delete(self.exception_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.exception.refresh_from_db()
        self.assertTrue(self.exception.is_deleted)
    
    def test_resolve_exception(self):
        data = {'solution': 'Test Solution'}
        response = self.client.post(self.resolve_exception_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['solution'], 'Test Solution')
        self.assertIsNotNone(response.data['resolved_at'])
    
    def test_resolve_exception_without_solution(self):
        data = {}
        response = self.client.post(self.resolve_exception_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)