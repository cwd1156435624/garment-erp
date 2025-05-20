from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.warehouse.models import Warehouse, DeliveryTask, FinishedGoods
from apps.production.models import Order, Batch

class WarehouseTests(TestCase):
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
        
        self.warehouse_url = reverse('warehouse-list')
        self.warehouse_detail_url = reverse('warehouse-detail', args=[self.warehouse.id])
    
    def test_create_warehouse_success(self):
        data = {
            'name': 'New Warehouse',
            'address': 'New Address',
            'contact_person': 'Jane Doe',
            'contact_phone': '0987654321',
            'area': 2000.0
        }
        response = self.client.post(self.warehouse_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Warehouse.objects.count(), 2)
    
    def test_create_warehouse_invalid_data(self):
        data = {
            'name': '',  # name is required
            'contact_person': 'Jane Doe',
            'contact_phone': 'invalid_phone',  # invalid phone format
            'area': -1000  # invalid area value
        }
        response = self.client.post(self.warehouse_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_warehouse_missing_required_fields(self):
        data = {
            'contact_person': 'Jane Doe',
            'contact_phone': '0987654321'
            # missing name and address
        }
        response = self.client.post(self.warehouse_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('address', response.data)
    
    def test_create_warehouse_duplicate_name(self):
        data = {
            'name': 'Test Warehouse',  # duplicate name
            'address': 'New Address',
            'contact_person': 'Jane Doe',
            'contact_phone': '0987654321',
            'area': 2000.0
        }
        response = self.client.post(self.warehouse_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_get_warehouses_success(self):
        response = self.client.get(self.warehouse_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_warehouse_detail_success(self):
        response = self.client.get(self.warehouse_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Warehouse')
    
    def test_get_warehouse_detail_not_found(self):
        url = reverse('warehouse-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_warehouse_success(self):
        data = {'name': 'Updated Warehouse'}
        response = self.client.patch(self.warehouse_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Warehouse')
    
    def test_update_warehouse_invalid_data(self):
        data = {
            'area': -1000,  # invalid area value
            'contact_phone': 'invalid_phone'  # invalid phone format
        }
        response = self.client.patch(self.warehouse_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_warehouse_success(self):
        response = self.client.delete(self.warehouse_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.warehouse.refresh_from_db()
        self.assertTrue(self.warehouse.is_deleted)
    
    def test_filter_by_name(self):
        response = self.client.get(f'{self.warehouse_url}?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Warehouse')
    
    def test_filter_by_address(self):
        response = self.client.get(f'{self.warehouse_url}?address=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['address'], 'Test Address')
    
    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.warehouse_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_warehouse_permission_denied(self):
        # Create a regular user without proper permissions
        regular_user = get_user_model().objects.create_user(
            username='regular_user',
            password='regular123'
        )
        self.client.force_authenticate(user=regular_user)
        
        data = {
            'name': 'New Warehouse',
            'address': 'New Address',
            'contact_person': 'Jane Doe',
            'contact_phone': '0987654321',
            'area': 2000.0
        }
        response = self.client.post(self.warehouse_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)