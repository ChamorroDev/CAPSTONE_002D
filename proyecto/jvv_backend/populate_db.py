import os
import django
from faker import Faker
from datetime import date
import random
from datetime import timedelta, time

# Configura el entorno de Django para poder usar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jvv_backend.settings')  # Ajusta al nombre real de tu proyecto
django.setup()

from api.models import (
    JuntaVecinos, CustomUser, Noticia, ProyectoVecinal, Actividad,
    InscripcionActividad, Espacio, SolicitudEspacio, SolicitudCertificado
)

# Crea una instancia de Faker en español
fake = Faker('es_ES')


def populate_database(num_users=20, num_noticias=10, num_proyectos=5, num_actividades=5, num_espacios=3):
    """
    Poblar la base de datos con datos ficticios para pruebas.
    """
    print("Iniciando el poblado de la base de datos...")

    # Crear Junta de Vecinos
    try:
        junta_vecinos = JuntaVecinos.objects.create(
            nombre=fake.street_name() + ' Vecinos',
            direccion=fake.address(),
            comuna=fake.city(),
            region=fake.state(),
            activa=True
        )
        print(f"Junta de vecinos creada: {junta_vecinos.nombre}")
    except Exception as e:
        print(f"Error al crear JuntaVecinos: {e}")
        return

    usuarios = []

    # Crear administrador
    administrador = CustomUser.objects.create_user(
        email='admin@junta.cl',
        password='password123',
        nombre=fake.first_name(),
        apellido=fake.last_name(),
        rut=fake.unique.ssn()[:12],
        telefono=fake.phone_number(),
        direccion=fake.address(),
        fecha_nacimiento=date(1980, 1, 1),
        rol='administrador',
        is_active=True,
        junta_vecinos=junta_vecinos
    )
    administrador.es_vecino = True
    administrador.save()
    usuarios.append(administrador)
    print("Administrador creado.")

    # Crear directivo
    directivo = CustomUser.objects.create_user(
        email='directivo@junta.cl',
        password='password123',
        nombre=fake.first_name(),
        apellido=fake.last_name(),
        rut=fake.unique.ssn()[:12],
        telefono=fake.phone_number(),
        direccion=fake.address(),
        fecha_nacimiento=date(1985, 5, 20),
        rol='directivo',
        is_active=True,
        junta_vecinos=junta_vecinos
    )
    directivo.es_vecino = True
    directivo.save()
    usuarios.append(directivo)
    print("Directivo creado.")

    # Crear vecinos y registrados
    vecinos = []
    for _ in range(num_users):
        rol = random.choice(['vecino', 'registrado'])
        user = CustomUser.objects.create_user(
            email=fake.unique.email(),
            password='password123',
            nombre=fake.first_name(),
            apellido=fake.last_name(),
            rut=fake.unique.ssn()[:12],
            telefono=fake.phone_number(),
            direccion=fake.address(),
            fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=90),
            rol=rol,
            is_active=True,
            junta_vecinos=junta_vecinos
        )
        user.es_vecino = (rol == 'vecino')
        user.save()
        usuarios.append(user)
        if rol == 'vecino':
            vecinos.append(user)
    print(f"{num_users} usuarios creados ({len(vecinos)} vecinos, {num_users - len(vecinos)} registrados).")

    # Crear noticias
    for _ in range(num_noticias):
        Noticia.objects.create(
            titulo=fake.sentence(nb_words=6),
            contenido=fake.paragraph(nb_sentences=5),
            junta_vecinos=junta_vecinos,
            autor=directivo,
            es_publica=random.choice([True, False])
        )
    print(f"{num_noticias} noticias creadas.")

    # Crear proyectos vecinales
    for _ in range(num_proyectos):
        proponente = random.choice(vecinos)
        ProyectoVecinal.objects.create(
            titulo=fake.sentence(nb_words=5),
            descripcion=fake.paragraph(),
            proponente=proponente,
            junta_vecinos=junta_vecinos,
            estado=random.choice(['pendiente', 'aprobado', 'rechazado'])
        )
    print(f"{num_proyectos} proyectos vecinales creados.")

    # Crear actividades + inscripciones
    actividades = []
    for _ in range(num_actividades):
        actividad = Actividad.objects.create(
            titulo=fake.sentence(nb_words=4),
            descripcion=fake.paragraph(),
            fecha=fake.date_time_between(start_date="now", end_date="+30d"),
            cupo_maximo=random.randint(0, 50),
            junta_vecinos=junta_vecinos,
            creada_por=directivo
        )
        actividades.append(actividad)

        # Inscripciones
        num_inscritos = random.randint(0, len(vecinos))
        inscritos = random.sample(vecinos, num_inscritos)
        for vecino_inscrito in inscritos:
            InscripcionActividad.objects.create(actividad=actividad, vecino=vecino_inscrito)
    print(f"{num_actividades} actividades creadas con inscripciones.")

    # Crear espacios
    espacios = []
    for _ in range(num_espacios):
        espacio = Espacio.objects.create(
            nombre=fake.word().capitalize(),
            tipo=random.choice(['cancha', 'sala', 'otro']),
            descripcion=fake.sentence(),
            junta_vecinos=junta_vecinos
        )
        espacios.append(espacio)

    # Crear solicitudes de espacio
    for _ in range(num_espacios * 2):
        espacio_solicitado = random.choice(espacios)
        solicitante = random.choice(vecinos)
        fecha_evento = fake.date_this_year()
        hora_inicio = time(hour=random.randint(8, 20), minute=0)
        hora_fin = time(hour=(hora_inicio.hour + random.randint(1, 3)) % 24, minute=0)

        try:
            SolicitudEspacio.objects.create(
                espacio=espacio_solicitado,
                solicitante=solicitante,
                fecha_evento=fecha_evento,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                motivo=fake.sentence(),
                estado=random.choice(['pendiente', 'aprobado', 'rechazado']),
                aprobado_por=directivo
            )
        except Exception:
            continue
    print("Espacios y solicitudes creadas.")

    # Crear solicitudes de certificados
    for _ in range(num_users // 2):
        vecino = random.choice(vecinos)
        SolicitudCertificado.objects.create(
            vecino=vecino,
            tipo=random.choice(['Residencia', 'Vigencia', 'Directiva']),
            motivo=fake.sentence(),
            estado=random.choice(['pendiente', 'aprobado', 'rechazado']),
            resuelto_por=directivo
        )
    print("Solicitudes de certificado creadas.")

    print("Poblado de la base de datos finalizado con éxito.")


if __name__ == '__main__':
    populate_database()
