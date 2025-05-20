from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.finance.models import Transaction

class TransactionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.transaction = Transaction.objects.create(
            transaction_id='TR001',
            transaction_type='income',
            amount=1000.00,
            description='Test Transaction',
            status='pending'
        )
        
        self.transaction_url = reverse('transaction-list')
        self.transaction_detail_url = reverse('transaction-detail', args=[self.transaction.id])
        self.approve_url = reverse('transaction-approve', args=[self.transaction.id])
    
    def test_create_transaction(self):
        data = {
            'transaction_id': 'TR002',
            'transaction_type': 'expense',
            'amount': 500.00,
            'description': 'New Transaction',
            'status': 'pending'
        }
        response = self.client.post(self.transaction_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)
    
    def test_get_transactions(self):
        response = self.client.get(self.transaction_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_transaction_detail(self):
        response = self.client.get(self.transaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction_id'], 'TR001')

    def test_approve_transaction(self):
        # 测试正常审批流程
        response = self.client.patch(self.approve_url, {'action': 'approve'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transaction.objects.get(id=self.transaction.id).status, 'approved')

    def test_reject_transaction(self):
        # 测试正常拒绝流程
        response = self.client.patch(self.approve_url, {'action': 'reject'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transaction.objects.get(id=self.transaction.id).status, 'rejected')

    def test_invalid_status_change(self):
        # 测试无效状态变更
        self.transaction.status = 'completed'
        self.transaction.save()
        response = self.client.patch(self.approve_url, {'action': 'approve'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('completed', response.data['detail'])
    
    def test_update_transaction(self):
        data = {'amount': 1500.00}
        response = self.client.patch(self.transaction_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['amount']), 1500.00)
    
    def test_delete_transaction(self):
        response = self.client.delete(self.transaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.transaction.refresh_from_db()
        self.assertTrue(self.transaction.is_deleted)
    
    def test_approve_transaction(self):
        response = self.client.post(self.approve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
    
    def test_filter_by_transaction_type(self):
        response = self.client.get(f'{self.transaction_url}?transaction_type=income')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['transaction_type'], 'income')
    
    def test_filter_by_status(self):
        response = self.client.get(f'{self.transaction_url}?status=pending')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')
    
    def test_filter_by_amount_range(self):
        response = self.client.get(f'{self.transaction_url}?min_amount=500&max_amount=2000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(500 <= float(response.data[0]['amount']) <= 2000)