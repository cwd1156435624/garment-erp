from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.production.models import CuttingTask

class CuttingTaskTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.task = CuttingTask.objects.create(
            task_number='TASK001',
            product_name='Test Product',
            quantity=100,
            status='pending'
        )
        
        self.task_url = reverse('cuttingtask-list')
        self.task_detail_url = reverse('cuttingtask-detail', args=[self.task.id])
        self.start_task_url = reverse('cuttingtask-start-task', args=[self.task.id])
        self.complete_task_url = reverse('cuttingtask-complete-task', args=[self.task.id])
    
    def test_create_task(self):
        data = {
            'task_number': 'TASK002',
            'product_name': 'Test Product 2',
            'quantity': 200,
            'status': 'pending'
        }
        response = self.client.post(self.task_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CuttingTask.objects.count(), 2)
    
    def test_get_tasks(self):
        response = self.client.get(self.task_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_task_detail(self):
        response = self.client.get(self.task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_number'], 'TASK001')
    
    def test_update_task(self):
        data = {'product_name': 'Updated Product'}
        response = self.client.patch(self.task_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['product_name'], 'Updated Product')
    
    def test_delete_task(self):
        response = self.client.delete(self.task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_deleted)
    
    def test_start_task(self):
        response = self.client.post(self.start_task_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'processing')
        self.assertIsNotNone(response.data['start_time'])
    
    def test_start_task_invalid_status(self):
        self.task.status = 'processing'
        self.task.save()
        response = self.client.post(self.start_task_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_complete_task(self):
        self.task.status = 'processing'
        self.task.save()
        response = self.client.post(self.complete_task_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertIsNotNone(response.data['end_time'])
    
    def test_complete_task_invalid_status(self):
        response = self.client.post(self.complete_task_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)