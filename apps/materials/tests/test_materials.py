from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.materials.models import Material

class MaterialTests(APITestCase):
    def test_create_material_success(self):
        url = reverse('material-list')
        data = {'name': 'Steel', 'spec': 'ASTM A36', 'unit': 'kg'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(Material.objects.get().name, 'Steel')

    def test_create_material_invalid_data(self):
        url = reverse('material-list')
        data = {'name': '', 'spec': 'ASTM A36'}  # 缺少必填字段
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_material_detail_success(self):
        material = Material.objects.create(name='Aluminum', spec='6061')
        url = reverse('material-detail', args=[material.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Aluminum')

    def test_get_nonexistent_material(self):
        url = reverse('material-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)