from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.supplier.models import Supplier, PurchaseOrder

class SupplierTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            email='test@example.com',
            address='Test Address'
        )
        
        self.supplier_url = reverse('supplier-list')
        self.supplier_detail_url = reverse('supplier-detail', args=[self.supplier.id])
    
    def test_create_supplier_success(self):
        data = {
            'name': 'New Supplier',
            'contact_person': 'Jane Doe',
            'phone': '0987654321',
            'email': 'new@example.com',
            'address': 'New Address'
        }
        response = self.client.post(self.supplier_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 2)
    
    def test_create_supplier_invalid_data(self):
        data = {
            'name': '',
            'contact_person': 'Test',
            'phone': '123',
            'email': 'invalid'
        }
        response = self.client.post(self.supplier_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)
        self.assertIn('email', response.data)

    def test_update_nonexistent_supplier(self):
        invalid_url = reverse('supplier-detail', args=[999])
        data = {'name': 'Updated Name'}
        response = self.client.patch(invalid_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_supplier_invalid_format(self):
        data = {
            'name': '',
            'contact_person': 'Jane Doe',
            'phone': 'invalid_phone',
            'email': 'invalid_email'
        }
        response = self.client.post(self.supplier_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_supplier_missing_required_fields(self):
        data = {
            'contact_person': 'Jane Doe',
            'phone': '0987654321'
            # missing name and address
        }
        response = self.client.post(self.supplier_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('address', response.data)
    
    def test_create_supplier_duplicate_name(self):
        data = {
            'name': 'Test Supplier',  # duplicate name
            'contact_person': 'Jane Doe',
            'phone': '0987654321',
            'email': 'new@example.com',
            'address': 'New Address'
        }
        response = self.client.post(self.supplier_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_update_supplier_invalid_status(self):
        data = {'status': 'invalid_status'}
        response = self.client.patch(self.supplier_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
    
    def test_change_status_invalid_transition(self):
        self.supplier.status = 'terminated'
        self.supplier.save()
        response = self.client.post(reverse('supplier-change-status', args=[self.supplier.id]), 
                                  {'status': 'active'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_status_success(self):
        response = self.client.post(reverse('supplier-change-status', args=[self.supplier.id]), 
                                  {'status': 'suspended'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'suspended')
    
    def test_get_suppliers_success(self):
        response = self.client.get(self.supplier_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_supplier_detail_success(self):
        response = self.client.get(self.supplier_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Supplier')
    
    def test_get_supplier_detail_not_found(self):
        url = reverse('supplier-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_supplier_success(self):
        data = {'name': 'Updated Supplier'}
        response = self.client.patch(self.supplier_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Supplier')
    
    def test_update_supplier_invalid_data(self):
        data = {
            'email': 'invalid_email',  # invalid email format
            'phone': 'invalid_phone'  # invalid phone format
        }
        response = self.client.patch(self.supplier_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_supplier_success(self):
        response = self.client.delete(self.supplier_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.supplier.refresh_from_db()
        self.assertTrue(self.supplier.is_deleted)
    
    def test_search_supplier(self):
        response = self.client.get(f'{self.supplier_url}?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Supplier')
    
    def test_filter_supplier_by_email(self):
        response = self.client.get(f'{self.supplier_url}?email=test@example.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'test@example.com')
    
    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PurchaseOrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            email='test@example.com'
        )
        
        self.purchase_order = PurchaseOrder.objects.create(
            order_number='PO001',
            supplier=self.supplier,
            total_amount=1000.00,
            status='pending',
            created_by=self.user
        )
        
        self.purchase_order_url = reverse('purchaseorder-list')
        self.purchase_order_detail_url = reverse('purchaseorder-detail', args=[self.purchase_order.id])
        self.approve_url = reverse('purchaseorder-approve', args=[self.purchase_order.id])
    
    def test_create_purchase_order_success(self):
        data = {
            'order_number': 'PO002',
            'supplier': self.supplier.id,
            'total_amount': 2000.00,
            'status': 'pending'
        }
        response = self.client.post(self.purchase_order_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseOrder.objects.count(), 2)
    
    def test_create_purchase_order_invalid_data(self):
        data = {
            'order_number': '',  # order_number is required
            'supplier': 999,  # invalid supplier id
            'total_amount': -1000  # invalid amount
        }
        response = self.client.post(self.purchase_order_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_purchase_orders_success(self):
        response = self.client.get(self.purchase_order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_purchase_order_detail_success(self):
        response = self.client.get(self.purchase_order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_number'], 'PO001')
    
    def test_get_purchase_order_detail_not_found(self):
        url = reverse('purchaseorder-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_purchase_order_success(self):
        data = {'total_amount': 1500.00}
        response = self.client.patch(self.purchase_order_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['total_amount']), 1500.00)
    
    def test_update_purchase_order_invalid_data(self):
        data = {
            'total_amount': -1000,  # invalid amount
            'status': 'invalid_status'  # invalid status
        }
        response = self.client.patch(self.purchase_order_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_purchase_order_success(self):
        response = self.client.delete(self.purchase_order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.purchase_order.refresh_from_db()
        self.assertTrue(self.purchase_order.is_deleted)
    
    def test_approve_purchase_order_success(self):
        response = self.client.post(self.approve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
    
    def test_approve_purchase_order_already_approved(self):
        self.purchase_order.status = 'approved'
        self.purchase_order.save()
        response = self.client.post(self.approve_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filter_by_supplier(self):
        response = self.client.get(f'{self.purchase_order_url}?supplier_id={self.supplier.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['supplier'], self.supplier.id)
    
    def test_filter_by_status(self):
        response = self.client.get(f'{self.purchase_order_url}?status=pending')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')
    
    def test_filter_by_amount_range(self):
        response = self.client.get(f'{self.purchase_order_url}?min_amount=500&max_amount=1500')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(500 <= float(response.data[0]['total_amount']) <= 1500)
    
    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.purchase_order_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_supplier_permission_denied(self):
        # Create a regular user without proper permissions
        regular_user = get_user_model().objects.create_user(
            username='regular_user',
            password='regular123'
        )
        self.client.force_authenticate(user=regular_user)
        
        data = {
            'name': 'New Supplier',
            'contact_person': 'Jane Doe',
            'phone': '0987654321',
            'email': 'new@example.com',
            'address': 'New Address'
        }
        response = self.client.post(self.supplier_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_supplier_with_invalid_credit_limit(self):
        data = {'credit_limit': -1000}  # negative credit limit
        response = self.client.patch(self.supplier_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('credit_limit', response.data)
    
    def test_update_supplier_with_invalid_tax_number(self):
        data = {'tax_number': '12'}  # too short tax number
        response = self.client.patch(self.supplier_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tax_number', response.data)
    
    def test_change_status_without_reason(self):
        response = self.client.post(reverse('supplier-change-status', args=[self.supplier.id]), 
                                  {'status': 'suspended'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reason', response.data)