from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.production.models import Batch

class BatchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.batch = Batch.objects.create(
            batch_number='BATCH001',
            product_name='Test Product',
            quantity=500,
            status='pending'
        )
        
        self.batch_url = reverse('batch-list')
        self.batch_detail_url = reverse('batch-detail', args=[self.batch.id])
        self.update_status_url = reverse('batch-update-status', args=[self.batch.id])
        self.quality_check_url = reverse('batch-record-quality-check', args=[self.batch.id])
    
    def test_create_batch(self):
        data = {
            'batch_number': 'BATCH002',
            'product_name': 'Test Product 2',
            'quantity': 1000,
            'status': 'pending'
        }
        response = self.client.post(self.batch_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Batch.objects.count(), 2)
    
    def test_get_batches(self):
        response = self.client.get(self.batch_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_batch_detail(self):
        response = self.client.get(self.batch_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['batch_number'], 'BATCH001')
    
    def test_update_batch(self):
        data = {'product_name': 'Updated Product'}
        response = self.client.patch(self.batch_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['product_name'], 'Updated Product')
    
    def test_delete_batch(self):
        response = self.client.delete(self.batch_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.batch.refresh_from_db()
        self.assertTrue(self.batch.is_deleted)
    
    def test_update_status(self):
        data = {'status': 'processing'}
        response = self.client.post(self.update_status_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'processing')
    
    def test_update_status_invalid(self):
        data = {'status': 'invalid_status'}
        response = self.client.post(self.update_status_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_record_quality_check(self):
        data = {'quality_check_result': 'passed'}
        response = self.client.post(self.quality_check_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quality_check_result'], 'passed')
        self.assertEqual(response.data['status'], 'quality_check')
    
    def test_record_quality_check_without_result(self):
        data = {}
        response = self.client.post(self.quality_check_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)