from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.employee.models import Employee

class EmployeeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.employee = Employee.objects.create(
            name='Test Employee',
            employee_id='EMP001',
            department='Engineering',
            position='Software Engineer',
            phone='1234567890',
            email='test@example.com',
            hire_date='2023-01-01'
        )
        
        self.employee_url = reverse('employee-list')
        self.employee_detail_url = reverse('employee-detail', args=[self.employee.id])
    
    def test_create_employee(self):
        data = {
            'name': 'New Employee',
            'employee_id': 'EMP002',
            'department': 'Marketing',
            'position': 'Marketing Manager',
            'phone': '0987654321',
            'email': 'new@example.com',
            'hire_date': '2023-02-01'
        }
        response = self.client.post(self.employee_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)
    
    def test_get_employees(self):
        response = self.client.get(self.employee_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_employee_detail(self):
        response = self.client.get(self.employee_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], 'EMP001')
    
    def test_update_employee(self):
        data = {'position': 'Senior Software Engineer'}
        response = self.client.patch(self.employee_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['position'], 'Senior Software Engineer')
    
    def test_delete_employee(self):
        response = self.client.delete(self.employee_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.is_deleted)
    
    def test_search_employee(self):
        response = self.client.get(f'{self.employee_url}?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Employee')
    
    def test_filter_employee_by_department(self):
        response = self.client.get(f'{self.employee_url}?department=Engineering')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['department'], 'Engineering')
    
    def test_filter_employee_by_position(self):
        response = self.client.get(f'{self.employee_url}?position=Software Engineer')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['position'], 'Software Engineer')