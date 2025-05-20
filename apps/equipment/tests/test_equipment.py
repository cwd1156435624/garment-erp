from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.equipment.models import Equipment, MaintenanceRecord, FaultRecord

class EquipmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.equipment = Equipment.objects.create(
            equipment_id='EQ001',
            name='Test Equipment',
            equipment_type='machine',
            status='normal',
            location='Test Location'
        )
        
        self.equipment_url = reverse('equipment-list')
        self.equipment_detail_url = reverse('equipment-detail', args=[self.equipment.id])
    
    def test_create_equipment_success(self):
        data = {
            'equipment_id': 'EQ002',
            'name': 'New Equipment',
            'equipment_type': 'machine',
            'status': 'normal',
            'location': 'New Location'
        }
        response = self.client.post(self.equipment_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Equipment.objects.count(), 2)
    
    def test_create_equipment_invalid_data(self):
        invalid_cases = [
            {
                'data': {
                    'equipment_id': 'EQ002',
                    'name': '',
                    'equipment_type': 'invalid_type',
                    'status': 'normal'
                },
                'expected_error': 'This field may not be blank.'
            },
            {
                'data': {
                    'equipment_id': 'EQ003',
                    'name': 'Missing Location',
                    'equipment_type': 'machine',
                    'status': 'normal'
                },
                'expected_error': 'This field is required.'
            }
        ]

        for case in invalid_cases:
            with self.subTest(case=case['data']):
                response = self.client.post(self.equipment_url, case['data'])
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(case['expected_error'], str(response.data))


    
    def test_get_equipment_list_success(self):
        response = self.client.get(self.equipment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_equipment_detail_success(self):
        response = self.client.get(self.equipment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['equipment_id'], 'EQ001')
    
    def test_get_equipment_detail_not_found(self):
        url = reverse('equipment-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_equipment_success(self):
        data = {'name': 'Updated Equipment'}
        response = self.client.patch(self.equipment_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Equipment')
    
    def test_update_equipment_invalid_data(self):
        data = {'status': 'invalid_status'}
        response = self.client.patch(self.equipment_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    
    def test_delete_equipment_success(self):
        response = self.client.delete(self.equipment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.equipment.refresh_from_db()
        self.assertTrue(self.equipment.is_deleted)
    
    def test_filter_by_equipment_type(self):
        response = self.client.get(f'{self.equipment_url}?equipment_type=machine')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['equipment_type'], 'machine')
    
    def test_filter_by_status(self):
        response = self.client.get(f'{self.equipment_url}?status=normal')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'normal')
    
    def test_filter_by_location(self):
        response = self.client.get(f'{self.equipment_url}?location=Test Location')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location'], 'Test Location')
    
    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.equipment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class MaintenanceRecordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.equipment = Equipment.objects.create(
            equipment_id='EQ001',
            name='Test Equipment',
            equipment_type='machine',
            status='normal'
        )
        
        self.maintenance = MaintenanceRecord.objects.create(
            equipment=self.equipment,
            maintenance_type='routine',
            description='Test Maintenance',
            start_time='2023-01-01T10:00:00Z',
            end_time='2023-01-01T11:00:00Z',
            status='completed'
        )
        
        self.maintenance_url = reverse('maintenancerecord-list')
        self.maintenance_detail_url = reverse('maintenancerecord-detail', args=[self.maintenance.id])
    
    def test_create_maintenance_success(self):
        data = {
            'equipment': self.equipment.id,
            'maintenance_type': 'repair',
            'description': 'New Maintenance',
            'start_time': '2023-01-02T10:00:00Z',
            'end_time': '2023-01-02T11:00:00Z',
            'status': 'completed'
        }
        response = self.client.post(self.maintenance_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MaintenanceRecord.objects.count(), 2)
    
    def test_create_maintenance_invalid_data(self):
        data = {
            'equipment': self.equipment.id,
            'maintenance_type': 'invalid_type',
            'description': '',
            'start_time': 'invalid_time'
        }
        response = self.client.post(self.maintenance_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    
    def test_get_maintenance_list_success(self):
        response = self.client.get(self.maintenance_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_maintenance_detail_success(self):
        response = self.client.get(self.maintenance_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['maintenance_type'], 'routine')
    
    def test_get_maintenance_detail_not_found(self):
        url = reverse('maintenancerecord-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_maintenance_success(self):
        data = {'description': 'Updated Maintenance'}
        response = self.client.patch(self.maintenance_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated Maintenance')
    
    def test_update_maintenance_invalid_data(self):
        data = {'maintenance_type': 'invalid_type'}
        response = self.client.patch(self.maintenance_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    
    def test_delete_maintenance_success(self):
        response = self.client.delete(self.maintenance_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.maintenance.refresh_from_db()
        self.assertTrue(self.maintenance.is_deleted)
    
    def test_filter_by_equipment(self):
        response = self.client.get(f'{self.maintenance_url}?equipment_id={self.equipment.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_filter_by_maintenance_type(self):
        response = self.client.get(f'{self.maintenance_url}?maintenance_type=routine')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['maintenance_type'], 'routine')
    
    def test_filter_by_date_range(self):
        response = self.client.get(
            f'{self.maintenance_url}?start_time=2023-01-01T00:00:00Z&end_time=2023-01-01T23:59:59Z'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.maintenance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class FaultRecordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.equipment = Equipment.objects.create(
            equipment_id='EQ001',
            name='Test Equipment',
            equipment_type='machine',
            status='normal'
        )
        
        self.fault = FaultRecord.objects.create(
            equipment=self.equipment,
            fault_type='mechanical',
            description='Test Fault',
            status='pending',
            reported_by=self.user
        )
        
        self.fault_url = reverse('faultrecord-list')
        self.fault_detail_url = reverse('faultrecord-detail', args=[self.fault.id])
    
    def test_create_fault_success(self):
        data = {
            'equipment': self.equipment.id,
            'fault_type': 'electrical',
            'description': 'New Fault',
            'status': 'pending'
        }
        response = self.client.post(self.fault_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FaultRecord.objects.count(), 2)
    
    def test_create_fault_invalid_data(self):
        data = {
            'equipment': self.equipment.id,
            'fault_type': 'invalid_type',
            'description': '',
            'status': 'invalid_status'
        }
        response = self.client.post(self.fault_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    
    def test_get_fault_list_success(self):
        response = self.client.get(self.fault_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_fault_detail_success(self):
        response = self.client.get(self.fault_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fault_type'], 'mechanical')
    
    def test_get_fault_detail_not_found(self):
        url = reverse('faultrecord-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_fault_success(self):
        data = {'status': 'resolved'}
        response = self.client.patch(self.fault_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'resolved')
    
    def test_update_fault_invalid_data(self):
        data = {'fault_type': 'invalid_type'}
        response = self.client.patch(self.fault_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    
    def test_delete_fault_success(self):
        response = self.client.delete(self.fault_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.fault.refresh_from_db()
        self.assertTrue(self.fault.is_deleted)
    
    def test_filter_by_equipment(self):
        response = self.client.get(f'{self.fault_url}?equipment_id={self.equipment.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_filter_by_fault_type(self):
        response = self.client.get(f'{self.fault_url}?fault_type=mechanical')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['fault_type'], 'mechanical')
    
    def test_filter_by_status(self):
        response = self.client.get(f'{self.fault_url}?status=pending')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')
    
    def