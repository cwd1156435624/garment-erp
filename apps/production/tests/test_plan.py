from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.production.models import ProductionPlan

class ProductionPlanTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.plan = ProductionPlan.objects.create(
            plan_number='PLAN001',
            product_name='Test Product',
            quantity=1000,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            status='pending',
            progress=0
        )
        
        self.plan_url = reverse('productionplan-list')
        self.plan_detail_url = reverse('productionplan-detail', args=[self.plan.id])
        self.update_progress_url = reverse('productionplan-update-progress', args=[self.plan.id])
    
    def test_create_plan(self):
        data = {
            'plan_number': 'PLAN002',
            'product_name': 'Test Product 2',
            'quantity': 2000,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date(),
            'status': 'pending',
            'progress': 0
        }
        response = self.client.post(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductionPlan.objects.count(), 2)
    
    def test_get_plans(self):
        response = self.client.get(self.plan_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_plan_detail(self):
        response = self.client.get(self.plan_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan_number'], 'PLAN001')
    
    def test_update_plan(self):
        data = {'product_name': 'Updated Product'}
        response = self.client.patch(self.plan_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['product_name'], 'Updated Product')
    
    def test_delete_plan(self):
        response = self.client.delete(self.plan_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.plan.refresh_from_db()
        self.assertTrue(self.plan.is_deleted)
    
    def test_update_progress(self):
        data = {'progress': 50}
        response = self.client.post(self.update_progress_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 50)
        self.assertEqual(response.data['status'], 'pending')
    
    def test_update_progress_complete(self):
        data = {'progress': 100}
        response = self.client.post(self.update_progress_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 100)
        self.assertEqual(response.data['status'], 'completed')
    
    def test_update_progress_invalid(self):
        data = {'progress': 150}
        response = self.client.post(self.update_progress_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)