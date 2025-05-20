from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.warehouse.models import Warehouse, FinishedGoods
from apps.production.models import Order, Batch
from datetime import datetime

class FinishedGoodsTests(TestCase):
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
        
        self.batch = Batch.objects.create(
            batch_number='B001',
            order=self.order,
            quantity=100,
            status='completed',
            created_by=self.user
        )
        
        self.finished_goods = FinishedGoods.objects.create(
            batch=self.batch,
            warehouse=self.warehouse,
            operation_type='in',
            quantity=50,
            operator=self.user
        )
        
        self.finished_goods_url = reverse('finishedgoods-list')
        self.finished_goods_detail_url = reverse('finishedgoods-detail', args=[self.finished_goods.id])
    
    def test_create_finished_goods_success(self):
        data = {
            'batch': self.batch.id,
            'warehouse': self.warehouse.id,
            'operation_type': 'in',
            'quantity': 30
        }
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FinishedGoods.objects.count(), 2)
    
    def test_create_finished_goods_invalid_data(self):
        data = {
            'batch': 999,  # invalid batch id
            'warehouse': self.warehouse.id,
            'operation_type': 'invalid',  # invalid operation type
            'quantity': -10  # invalid quantity
        }
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_finished_goods_missing_required_fields(self):
        data = {
            'warehouse': self.warehouse.id,
            'quantity': 30
            # missing batch and operation_type
        }
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('batch', response.data)
        self.assertIn('operation_type', response.data)
    
    def test_get_finished_goods_success(self):
        response = self.client.get(self.finished_goods_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_finished_goods_detail_success(self):
        response = self.client.get(self.finished_goods_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 50)
    
    def test_get_finished_goods_detail_not_found(self):
        url = reverse('finishedgoods-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_finished_goods_success(self):
        data = {'quantity': 60}
        response = self.client.patch(self.finished_goods_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 60)
    
    def test_update_finished_goods_invalid_data(self):
        data = {
            'quantity': -10,  # invalid quantity
            'operation_type': 'invalid'  # invalid operation type
        }
        response = self.client.patch(self.finished_goods_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_finished_goods_success(self):
        response = self.client.delete(self.finished_goods_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.finished_goods.refresh_from_db()
        self.assertTrue(self.finished_goods.is_deleted)
    
    def test_filter_by_warehouse(self):
        response = self.client.get(f'{self.finished_goods_url}?warehouse={self.warehouse.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['warehouse'], self.warehouse.id)
    
    def test_filter_by_batch(self):
        response = self.client.get(f'{self.finished_goods_url}?batch={self.batch.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['batch'], self.batch.id)
    
    def test_filter_by_operation_type(self):
        response = self.client.get(f'{self.finished_goods_url}?operation_type=in')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['operation_type'], 'in')
    
    def test_filter_by_date_range(self):
        today = datetime.now().date().isoformat()
        response = self.client.get(f'{self.finished_goods_url}?start_date={today}&end_date={today}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.finished_goods_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_finished_goods_permission_denied(self):
        regular_user = get_user_model().objects.create_user(
            username='regular_user',
            password='regular123'
        )
        self.client.force_authenticate(user=regular_user)
        
        data = {
            'batch': self.batch.id,
            'warehouse': self.warehouse.id,
            'operation_type': 'in',
            'quantity': 30
        }
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_validate_stock_quantity(self):
        # Test that stock quantity cannot be negative after operation
        data = {
            'batch': self.batch.id,
            'warehouse': self.warehouse.id,
            'operation_type': 'out',
            'quantity': 100  # trying to take out more than available
        }
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)

    def test_concurrent_stock_operations(self):
        # Test concurrent stock operations from multiple users
        from django.test import TransactionTestCase
        from django.db import transaction
        import threading
        import time

        class ConcurrentTest(TransactionTestCase):
            def setUp(self):
                super().setUp()
                self.user2 = get_user_model().objects.create_user(
                    username='testuser2',
                    password='testpass123'
                )
                self.client2 = APIClient()
                self.client2.force_authenticate(user=self.user2)

            def test_concurrent_stock_update(self):
                def update_stock(client, quantity):
                    data = {
                        'batch': self.batch.id,
                        'warehouse': self.warehouse.id,
                        'operation_type': 'out',
                        'quantity': quantity
                    }
                    return client.post(self.finished_goods_url, data)

                thread1 = threading.Thread(target=update_stock, args=(self.client, 30))
                thread2 = threading.Thread(target=update_stock, args=(self.client2, 30))

                thread1.start()
                thread2.start()
                thread1.join()
                thread2.join()

                # Verify final stock quantity
                final_stock = FinishedGoods.objects.filter(batch=self.batch).aggregate(total=models.Sum('quantity'))['total']
                self.assertIsNotNone(final_stock)
                self.assertEqual(final_stock, -10)  # Initial 50 - (30 + 30)

    def test_transaction_rollback(self):
        # Test transaction rollback when operation fails
        from django.db import transaction
        
        initial_stock = FinishedGoods.objects.filter(batch=self.batch).aggregate(total=models.Sum('quantity'))['total']
        
        try:
            with transaction.atomic():
                # Create a valid stock operation
                data1 = {
                    'batch': self.batch.id,
                    'warehouse': self.warehouse.id,
                    'operation_type': 'out',
                    'quantity': 20
                }
                response1 = self.client.post(self.finished_goods_url, data1)
                self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
                
                # Create an invalid stock operation
                data2 = {
                    'batch': self.batch.id,
                    'warehouse': self.warehouse.id,
                    'operation_type': 'out',
                    'quantity': 1000  # This should fail
                }
                response2 = self.client.post(self.finished_goods_url, data2)
                self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
                raise Exception('Forcing rollback')
        except:
            pass
        
        # Verify stock quantity remains unchanged
        final_stock = FinishedGoods.objects.filter(batch=self.batch).aggregate(total=models.Sum('quantity'))['total']
        self.assertEqual(final_stock, initial_stock)

    def test_high_volume_operations(self):
        # Test system performance with high volume of operations
        import time
        
        start_time = time.time()
        operation_count = 50
        
        for i in range(operation_count):
            data = {
                'batch': self.batch.id,
                'warehouse': self.warehouse.id,
                'operation_type': 'in',
                'quantity': 1
            }
            response = self.client.post(self.finished_goods_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert that the operations were completed within acceptable time
        self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds
        
        # Verify final stock quantity
        final_stock = FinishedGoods.objects.filter(batch=self.batch).aggregate(total=models.Sum('quantity'))['total']
        self.assertEqual(final_stock, 50 + operation_count)

    def test_boundary_conditions(self):
        # Test boundary conditions and edge cases
        
        # Test maximum integer value
        data = {
            'batch': self.batch.id,
            'warehouse': self.warehouse.id,
            'operation_type': 'in',
            'quantity': 2147483647  # Max int32 value
        }
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test zero quantity
        data['quantity'] = 0
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test negative quantity for 'in' operation
        data['quantity'] = -10
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with non-existent batch
        data.update({
            'batch': 99999,
            'quantity': 10
        })
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with non-existent warehouse
        data.update({
            'batch': self.batch.id,
            'warehouse': 99999
        })
        response = self.client.post(self.finished_goods_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)