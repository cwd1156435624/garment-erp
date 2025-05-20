from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.warehouse.models import Warehouse, DeliveryTask
from apps.production.models import Order
from datetime import date

class DeliveryTaskTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            address='Test Address',
            contact_person='John Doe',
            contact_phone='1234567890',
            area=1000.0
        )
        
        self.order = Order.objects.create(
            order_number='ORD001',
            total_amount=1000.00,
            status='confirmed',
            created_by=self.user
        )
        
        self.delivery_task = DeliveryTask.objects.create(
            task_number='DT001',
            order=self.order,
            from_warehouse=self.warehouse,
            to_address='Delivery Address',
            contact_person='Jane Doe',
            contact_phone='0987654321',
            delivery_date=date.today(),
            status='pending',
            created_by=self.user
        )
        
        self.delivery_task_url = reverse('deliverytask-list')
        self.delivery_task_detail_url = reverse('deliverytask-detail', args=[self.delivery_task.id])
    
    def test_create_delivery_task_success(self):
        data = {
            'task_number': 'DT002',
            'order': self.order.id,
            'from_warehouse': self.warehouse.id,
            'to_address': 'New Delivery Address',
            'contact_person': 'John Smith',
            'contact_phone': '1234567890',
            'delivery_date': date.today().isoformat(),
            'status': 'pending'
        }
        response = self.client.post(self.delivery_task_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeliveryTask.objects.count(), 2)
    
    def test_create_delivery_task_invalid_data(self):
        data = {
            'task_number': '',  # task_number is required
            'order': 999,  # invalid order id
            'from_warehouse': self.warehouse.id,
            'contact_phone': 'invalid_phone'  # invalid phone format
        }
        response = self.client.post(self.delivery_task_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_delivery_task_duplicate_number(self):
        data = {
            'task_number': 'DT001',  # duplicate task number
            'order': self.order.id,
            'from_warehouse': self.warehouse.id,
            'to_address': 'New Delivery Address',
            'contact_person': 'John Smith',
            'contact_phone': '1234567890',
            'delivery_date': date.today().isoformat(),
            'status': 'pending'
        }
        response = self.client.post(self.delivery_task_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('task_number', response.data)
    
    def test_get_delivery_tasks_success(self):
        response = self.client.get(self.delivery_task_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_delivery_task_detail_success(self):
        response = self.client.get(self.delivery_task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_number'], 'DT001')
    
    def test_get_delivery_task_detail_not_found(self):
        url = reverse('deliverytask-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_delivery_task_success(self):
        data = {
            'status': 'in_transit',
            'driver': 'John Driver',
            'vehicle_number': 'ABC123'
        }
        response = self.client.patch(self.delivery_task_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_transit')
    
    def test_update_delivery_task_invalid_status(self):
        data = {'status': 'invalid_status'}
        response = self.client.patch(self.delivery_task_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
    
    def test_update_delivered_task(self):
        self.delivery_task.status = 'delivered'
        self.delivery_task.save()
        data = {'status': 'in_transit'}
        response = self.client.patch(self.delivery_task_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_delivery_task_success(self):
        response = self.client.delete(self.delivery_task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.delivery_task.refresh_from_db()
        self.assertTrue(self.delivery_task.is_deleted)
    
    def test_filter_by_status(self):
        response = self.client.get(f'{self.delivery_task_url}?status=pending')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')
    
    def test_filter_by_warehouse(self):
        response = self.client.get(f'{self.delivery_task_url}?warehouse={self.warehouse.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['from_warehouse'], self.warehouse.id)
    
    def test_filter_by_date_range(self):
        today = date.today().isoformat()
        response = self.client.get(f'{self.delivery_task_url}?start_date={today}&end_date={today}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.delivery_task_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_delivery_task_permission_denied(self):
        regular_user = get_user_model().objects.create_user(
            username='regular_user',
            password='regular123'
        )
        self.client.force_authenticate(user=regular_user)
        
        data = {
            'task_number': 'DT002',
            'order': self.order.id,
            'from_warehouse': self.warehouse.id,
            'to_address': 'New Delivery Address',
            'contact_person': 'John Smith',
            'contact_phone': '1234567890',
            'delivery_date': date.today().isoformat(),
            'status': 'pending'
        }
        response = self.client.post(self.delivery_task_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)