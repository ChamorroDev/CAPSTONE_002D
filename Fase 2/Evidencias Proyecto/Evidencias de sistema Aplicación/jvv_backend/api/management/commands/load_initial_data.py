from api.models import *
from django.contrib.auth.hashers import make_password
from datetime import datetime, time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Carga datos iniciales de roles, usuarios, espacios, eventos y certificados'

    def handle(self, *args, **kwargs):
        # ---- Roles ----
        rol_vecino, _ = Rol.objects.get_or_create(nombre="Vecino", descripcion="Vecino registrado")
        rol_admin, _ = Rol.objects.get_or_create(nombre="Administrador", defaults={"descripcion": "Rol con permisos completos"})

        # ---- Usuarios ----
        Usuario.objects.get_or_create(
            nombre="Admin Principal",
            email="admin@juntavecinos.cl",
            password=make_password("admin123"),
            activo=True,
            rol=rol_admin
        )
        Usuario.objects.get_or_create(
            nombre="Juan Pérez",
            email="juan@vecino.cl",
            password=make_password("juan123"),
            activo=True,
            rol=rol_vecino
        )

        # ---- Espacios ----
        Espacio.objects.get_or_create(nombre="Cancha de Futbol", descripcion="Cancha de futbol de la junta", capacidad=20)
        Espacio.objects.get_or_create(nombre="Sala Multiuso", descripcion="Sala para actividades comunitarias", capacidad=30)

        # ---- Estados de Reserva ----
        EstadoReservaEspacio.objects.get_or_create(nombre="Pendiente")
        EstadoReservaEspacio.objects.get_or_create(nombre="Aprobada")
        EstadoReservaEspacio.objects.get_or_create(nombre="Rechazada")

        # ---- Estados de Evento ----
        EstadoEvento.objects.get_or_create(nombre="Pendiente")
        EstadoEvento.objects.get_or_create(nombre="Aprobado")
        EstadoEvento.objects.get_or_create(nombre="Rechazado")


        # ---- Actividades ----
        Actividad.objects.get_or_create(
            nombre="Clase de Yoga",
            descripcion="Clase de yoga semanal para vecinos",
            fecha=datetime(2025, 8, 20).date(),
            hora_inicio=time(10,0),
            hora_fin=time(11,0),
            cupo_maximo=15
        )

        Actividad.objects.get_or_create(
            nombre="Taller de Jardinería",
            descripcion="Aprender a cuidar plantas en comunidad",
            fecha=datetime(2025, 8, 21).date(),
            hora_inicio=time(15,0),
            hora_fin=time(17,0),
            cupo_maximo=20
        )

        # ---- Estados de Certificados ----
        EstadoCertificado.objects.get_or_create(nombre="Pendiente")
        EstadoCertificado.objects.get_or_create(nombre="Aprobado")
        EstadoCertificado.objects.get_or_create(nombre="Rechazado")

        self.stdout.write(self.style.SUCCESS('Datos iniciales cargados correctamente ✅'))
