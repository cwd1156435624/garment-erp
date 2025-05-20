from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.settlement.models import Settlement

class SettlementTests(APITestCase):
    def test_create_settlement_success(self):
        url = reverse('settlement-list')
        data = {'contract_number': 'CT2023001', 'amount': 150000.00, 'party_a': 'ABC公司'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Settlement.objects.count(), 1)
        self.assertEqual(Settlement.objects.get().contract_number, 'CT2023001')

    def test_create_settlement_invalid_data(self):
        url = reverse('settlement-list')
        data = {'amount': -500}  # 金额为负数
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_settlement_detail_success(self):
        settlement = Settlement.objects.create(contract_number='CT2023002', amount=200000)
        url = reverse('settlement-detail', args=[settlement.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contract_number'], 'CT2023002')

    def test_get_nonexistent_settlement(self):
        url = reverse('settlement-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reconciliation_process(self):
        payment = PaymentTransaction.objects.create(
            order_number='ORDER_RECON_001',
            amount='8000.00',
            payment_method='alipay',
            status='success'
        )
        
        # 正常对账流程
        recon_url = reverse('reconciliation-list')
        response = self.client.post(recon_url, {
            'payment_id': payment.id,
            'reconciliation_date': '2024-03-20',
            'amount': '8000.00'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 状态更新验证
        detail_url = reverse('reconciliation-detail', args=[response.data['id']])
        update_res = self.client.patch(detail_url, {'status': 'completed'})
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)

    def test_data_mismatch_handling(self):
        payment = PaymentTransaction.objects.create(
            order_number='ORDER_RECON_002',
            amount='6000.00',
            status='success'
        )
        
        response = self.client.post(reverse('reconciliation-list'), {
            'payment_id': payment.id,
            'amount': '5800.00',
            'reconciliation_date': '2024-03-20'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('金额不一致', str(response.data))

    def test_duplicate_reconciliation(self):
        payment = PaymentTransaction.objects.create(
            order_number='ORDER_RECON_003',
            amount='7000.00',
            status='success'
        )
        
        # 首次提交
        self.client.post(reverse('reconciliation-list'), {
            'payment_id': payment.id,
            'amount': '7000.00',
            'reconciliation_date': '2024-03-20'
        })
        
        # 重复提交
        duplicate_res = self.client.post(reverse('reconciliation-list'), {
            'payment_id': payment.id,
            'amount': '7000.00',
            'reconciliation_date': '2024-03-20'
        })
        self.assertEqual(duplicate_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('重复对账', str(duplicate_res.data))