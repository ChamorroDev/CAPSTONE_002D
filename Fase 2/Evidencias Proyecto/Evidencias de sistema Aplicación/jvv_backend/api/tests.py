import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, JuntaVecinos

class APITests(APITestCase):
    def setUp(self):
        self.junta = JuntaVecinos.objects.create(
            nombre="Junta de Prueba",
            direccion="Calle Test 123",
            comuna="Testcomuna",
            region="Testregion"
        )
        
        self.admin_user = CustomUser.objects.create_user(
            email="admin@test.cl",
            password="testpassword",
            nombre="Admin",
            apellido="Test",
            rut="22222222-2",
            telefono="+56987654321",
            direccion="Dirección test",
            fecha_nacimiento="1990-01-01",
            junta_vecinos=self.junta,
            rol="administrador",
            es_activo=True
        )
    
    def test_login(self):
        url = reverse('token_obtain_pair')
        data = {
            'email': 'admin@test.cl',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)