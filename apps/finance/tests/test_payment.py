from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.finance.models import PaymentTransaction
from concurrent.futures import ThreadPoolExecutor

class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='pay_test_user',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.payment_data = {
            'order_number': 'ORDER_123',
            'amount': '1000.00',
            'payment_method': 'alipay',
            'status': 'pending'
        }
        
        self.payment_url = reverse('payment-transaction-list')

    def test_create_payment_success(self):
        response = self.client.post(self.payment_url, self.payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentTransaction.objects.count(), 1)

    def test_payment_status_flow(self):
        # 测试状态从pending到success的合法转换
        payment = PaymentTransaction.objects.create(**self.payment_data)
        
        # 正常状态变更
        update_url = reverse('payment-transaction-detail', args=[payment.id])
        response = self.client.patch(update_url, {'status': 'success'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 非法状态变更（从success到pending）
        response = self.client.patch(update_url, {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_concurrent_payment_updates(self):
        payment = PaymentTransaction.objects.create(**self.payment_data)
        update_url = reverse('payment-transaction-detail', args=[payment.id])
        
        def update_status(status):
            client = APIClient()
            client.force_authenticate(user=self.user)
            return client.patch(update_url, {'status': status})

        # 并发提交5个更新请求
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_status, 'success') for _ in range(5)]
            results = [f.result().status_code for f in futures]

        # 验证只有一个请求成功（200），其他都冲突（409）
        self.assertEqual(results.count(status.HTTP_200_OK), 1)
        self.assertEqual(results.count(status.HTTP_409_CONFLICT), 4)

    def test_refund_process(self):
        # 创建已支付的交易记录
        payment = PaymentTransaction.objects.create(**{
            **self.payment_data,
            'status': 'success',
            'amount': '1500.00'
        })
        
        # 发起退款请求
        refund_url = reverse('payment-transaction-refund', args=[payment.id])
        response = self.client.post(refund_url, {
            'refund_amount': '1500.00',
            'reason': '客户取消订单'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'refunded')
        self.assertEqual(payment.refund_amount, 1500.00)

        # 测试超额退款
        response = self.client.post(refund_url, {'refund_amount': '2000.00'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('超过可退金额', str(response.data))

    def test_invalid_payment_data(self):
        invalid_cases = [
            {'amount': '-100', 'expected_error': '金额必须大于零'},
            {'payment_method': 'invalid', 'expected_error': '无效的支付方式'},
            {'order_number': '', 'expected_error': '该字段不能为空'}
        ]
        
        for case in invalid_cases:
            with self.subTest(data=case):
                data = {**self.payment_data, **case}
                response = self.client.post(self.payment_url, data)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(case['expected_error'], str(response.data))