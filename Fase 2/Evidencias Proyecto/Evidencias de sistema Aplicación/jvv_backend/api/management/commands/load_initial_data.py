from api.models import *
from django.contrib.auth.hashers import make_password
from datetime import datetime, time,timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Carga datos iniciales para la aplicación'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar recreación de datos incluso si ya existen',
        )
        parser.add_argument(
            '--clean-only',
            action='store_true',
            help='Solo limpiar datos sin crear nuevos',
        )
    
    def clean_database(self):
        """Limpia todos los datos de la base de datos"""
        self.stdout.write("🧹 Limpiando base de datos...")
        
        # IMPORTANTE: Borrar en el orden correcto para evitar errores de FK
        SolicitudEspacio.objects.all().delete()
        SolicitudCertificado.objects.all().delete()
        ProyectoVecinal.objects.all().delete()
        InscripcionActividad.objects.all().delete()
        NoticiaImagen.objects.all().delete()
        Actividad.objects.all().delete()
        Espacio.objects.all().delete()
        Noticia.objects.all().delete()
        
        # Borrar usuarios excepto superusuarios
        CustomUser.objects.exclude(is_superuser=True).delete()
        JuntaVecinos.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS("✅ Base de datos limpiada exitosamente"))
    
    def handle(self, *args, **options):
        force = options['force']
        clean_only = options['clean_only']
        
        if clean_only:
            self.clean_database()
            return
        
        if not force and JuntaVecinos.objects.exists():
            self.stdout.write(self.style.WARNING('⚠️ Ya existen datos. Usa --force para recrearlos'))
            return
        
        if force:
            self.clean_database()
        
        self.stdout.write("🚀 Iniciando carga de datos iniciales...")
        
        try:
            # 1. Crear Junta de Vecinos
            self.stdout.write("🏠 Creando Junta de Vecinos...")
            junta = JuntaVecinos.objects.create(
                nombre="Junta de Vecinos Villa Los Olivos",
                direccion="Av. Principal #123, Villa Los Olivos",
                comuna="Santiago",
                region="Metropolitana",
                activa=True
            )
            
            # 2. Crear usuarios de prueba
            self.stdout.write("👥 Creando usuarios...")
            
            # Administrador
            admin = CustomUser.objects.create_superuser(
                email="admin@juntavecinos.cl",
                password="admin123",
                nombre="Administrador",
                apellido="Sistema",
                rut="12.345.678-9",
                telefono="+56912345678",
                direccion="Av. Principal #123",
                fecha_nacimiento="1980-01-01",
                junta_vecinos=junta,
                rol="administrador",
                puede_gestionar_vecinos=True,
                puede_gestionar_certificados=True,
                puede_gestionar_proyectos=True,
                puede_gestionar_noticias=True,
                puede_gestionar_calendario=True,
                puede_gestionar_actividades=True
            )
            
            # Directivo
            directivo = CustomUser.objects.create_user(
                email="directivo@juntavecinos.cl",
                password="directivo123",
                nombre="María",
                apellido="González",
                rut="11.222.333-4",
                telefono="+56987654321",
                direccion="Calle Los Pinos #456",
                fecha_nacimiento="1985-05-15",
                junta_vecinos=junta,
                rol="directivo",
                puede_gestionar_vecinos=True,
                puede_gestionar_certificados=True,
                puede_gestionar_proyectos=True,
                puede_gestionar_noticias=True,
                puede_gestionar_calendario=True,
                puede_gestionar_actividades=True
            )
            
            # Vecino 1
            vecino1 = CustomUser.objects.create_user(
                email="juan.perez@email.com",
                password="vecino123",
                nombre="Juan",
                apellido="Pérez",
                rut="13.444.555-6",
                telefono="+56955556666",
                direccion="Pasaje Las Flores #789",
                fecha_nacimiento="1990-08-20",
                junta_vecinos=junta,
                rol="vecino"
            )
            
            # Vecino 2
            vecino2 = CustomUser.objects.create_user(
                email="ana.garcia@email.com",
                password="vecino123",
                nombre="Ana",
                apellido="García",
                rut="14.777.888-9",
                telefono="+56944443333",
                direccion="Av. Los Álamos #321",
                fecha_nacimiento="1988-12-10",
                junta_vecinos=junta,
                rol="vecino"
            )
            
            # 3. Crear noticias de ejemplo
            self.stdout.write("📰 Creando noticias...")
            
            noticia1 = Noticia.objects.create(
                titulo="Bienvenidos a la Junta de Vecinos Villa Los Olivos",
                contenido="""
            ¡Estimados vecinos y vecinas!

            Les damos la más cordial bienvenida a nuestra plataforma digital de la Junta de Vecinos Villa Los Olivos.

            Este espacio está diseñado para facilitar la comunicación, organización y participación de todos los residentes de nuestra comunidad.

            En esta plataforma podrán:
            - Enterarse de las últimas noticias y anuncios
            - Participar en actividades comunitarias
            - Solicitar certificados de residencia
            - Proponer proyectos vecinales
            - Reservar espacios comunes

            ¡Esperamos que esta herramienta sea de gran utilidad para todos!

            Atentamente,
            La Directiva
            """,
                junta_vecinos=junta,
                autor=directivo,
                es_publica=True
            )
                        
            noticia2 = Noticia.objects.create(
                titulo="Próxima Reunión Mensual de Vecinos",
                contenido="""
            CONVOCATORIA A REUNIÓN ORDINARIA

            Se convoca a todos los vecinos y vecinas a la próxima reunión mensual que se realizará el día:

            📅 Fecha: Sábado 15 de Enero 2024
            ⏰ Hora: 10:00 horas
            📍 Lugar: Sala Común de la Junta de Vecinos

            Temas a tratar:
            1. Bienvenida y aprobación del acta anterior
            2. Informe de gestión de la directiva
            3. Estado de proyectos en curso
            4. Propuestas de nuevos proyectos
            5. Asuntos varios

            ¡Su participación es muy importante para el desarrollo de nuestra comunidad!
            """,
                junta_vecinos=junta,
                autor=directivo,
                es_publica=True
            )
                        
            noticia3 = Noticia.objects.create(
                titulo="Mantenimiento de Áreas Verdes Programado",
                contenido="""
            AVISO IMPORTANTE

            Informamos a la comunidad que durante la próxima semana se realizarán trabajos de mantenimiento en las áreas verdes del condominio.

            📅 Fechas: Del 20 al 24 de Enero 2024
            🕘 Horario: 09:00 a 18:00 horas

            Trabajos a realizar:
            - Poda de árboles y arbustos
            - Corte de césped en todas las áreas
            - Riego y fertilización
            - Limpieza de jardineras

            Recomendaciones:
            - Mantener a mascotas y niños alejados de las zonas de trabajo
            - Retirar vehículos de las cercanías de las áreas verdes
            - Cerrar ventanas para evitar ingreso de polvo

            Agradecemos su comprensión y colaboración.
            """,
                junta_vecinos=junta,
                autor=directivo,
                es_publica=True
            )
            self.stdout.write("🖼️ Creando imágenes para noticias...")

            try:
                # Para noticia 1
                NoticiaImagen.objects.create(
                    noticia=noticia1,
                    imagen="noticias/noticia_1/noticia1.jpg",  
                    orden=0
                )
                self.stdout.write("✅ Imagen agregada a noticia 1")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Error con imagen noticia 1: {e}"))

            try:
                # Para noticia 2
                NoticiaImagen.objects.create(
                    noticia=noticia2,
                    imagen="noticias/noticia_2/noticia2.jpg",
                    orden=0
                )
                self.stdout.write("✅ Imagen agregada a noticia 2")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Error con imagen noticia 2: {e}"))

            try:
                # Para noticia 3
                NoticiaImagen.objects.create(
                    noticia=noticia3,
                    imagen="noticias/noticia_3/noticia3.jpg", 
                    orden=0
                )
                self.stdout.write("✅ Imagen agregada a noticia 3")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Error con imagen noticia 3: {e}"))

                
            
            # 4. Crear actividades
            self.stdout.write("🎯 Creando actividades...")
            
            actividad1 = Actividad.objects.create(
                titulo="Fiesta de la Primavera 2024",
                descripcion="Celebración comunitaria con música en vivo, comida típica y actividades para niños",
                fecha=timezone.now() + timedelta(days=30),
                cupo_maximo=150,
                cupo_por_vecino=5,
                permite_acompanantes=True,
                junta_vecinos=junta,
                creada_por=directivo
            )
            
            actividad2 = Actividad.objects.create(
                titulo="Taller de Reciclaje y Compostaje",
                descripcion="Aprende técnicas básicas de reciclaje y cómo hacer compost en casa",
                fecha=timezone.now() + timedelta(days=15),
                cupo_maximo=30,
                cupo_por_vecino=2,
                permite_acompanantes=True,
                junta_vecinos=junta,
                creada_por=directivo
            )
            
            actividad3 = Actividad.objects.create(
                titulo="Campeonato de Fútbol Vecinal",
                descripcion="Torneo de fútbol para todas las edades. ¡Inscríbete y participa!",
                fecha=timezone.now() + timedelta(days=45),
                cupo_maximo=40,
                cupo_por_vecino=1,
                permite_acompanantes=False,
                junta_vecinos=junta,
                creada_por=directivo
            )
            
            # 5. Crear inscripciones a actividades
            self.stdout.write("📝 Creando inscripciones...")
            
            InscripcionActividad.objects.create(
                actividad=actividad1,
                vecino=vecino1,
                cantidad_acompanantes=3,
                nombres_acompanantes=["María Pérez", "Pedro Pérez", "Laura Pérez"]
            )
            
            InscripcionActividad.objects.create(
                actividad=actividad2,
                vecino=vecino2,
                cantidad_acompanantes=1,
                nombres_acompanantes=["Carlos García"]
            )
            
            # 6. Crear espacios comunes
            self.stdout.write("🏟️ Creando espacios comunes...")
            
            cancha = Espacio.objects.create(
                nombre="Cancha de Fútbol",
                tipo="cancha",
                descripcion="Cancha de fútbol 7 con iluminación nocturna",
                disponible=True,
                junta_vecinos=junta
            )
            
            sala = Espacio.objects.create(
                nombre="Sala de Eventos",
                tipo="sala",
                descripcion="Sala común para reuniones y eventos, capacidad 50 personas",
                disponible=True,
                junta_vecinos=junta
            )
            
            # 7. Crear proyectos vecinales
            self.stdout.write("💡 Creando proyectos vecinales...")

            fecha_reciente = timezone.now() - timedelta(days=5)

            proyecto1 = ProyectoVecinal.objects.create(
                titulo="Instalación de Basureros de Reciclaje Comunitario",
                descripcion="Propuesta para implementar tres puntos limpios (vidrio, papel, plásticos) en las entradas principales del barrio para fomentar la sostenibilidad.",
                proponente=vecino1,
                junta_vecinos=junta,
                estado="pendiente"
            )

            proyecto2 = ProyectoVecinal.objects.create(
                titulo="Reparación y Pintura de la Sede Vecinal",
                descripcion="Solicitud de fondos para restaurar la fachada, reparar goteras en el techo y pintar el interior de la sede comunitaria.",
                proponente=vecino2,
                junta_vecinos=junta,
                estado="aprobado",
                fecha_revision=fecha_reciente,
                revisado_por=directivo
            )

            proyecto3 = ProyectoVecinal.objects.create(
                titulo="Taller de Huertos Urbanos para Adultos Mayores",
                descripcion="Creación de un espacio educativo semanal en el parque central para enseñar técnicas de cultivo hidropónico y orgánico a los vecinos, pero fue rechazado por falta de presupuesto.",
                proponente=vecino1,
                junta_vecinos=junta,
                estado="rechazado",
                fecha_revision=fecha_reciente + timedelta(hours=2), 
                revisado_por=directivo
            )

            proyecto4 = ProyectoVecinal.objects.create(
                titulo="Instalación de Cierres Perimetrales en Plazas",
                descripcion="Propuesta de seguridad para instalar cercas bajas alrededor de las plazas para evitar el ingreso de vehículos y perros sin correa, protegiendo a los niños.",
                proponente=vecino2,
                junta_vecinos=junta,
                estado="pendiente"
            )

            # 5. Proyecto En Revisión
            proyecto5 = ProyectoVecinal.objects.create(
                titulo="Campaña de Esterilización y Microchip",
                descripcion="Campaña masiva de esterilización y colocación de microchips para mascotas del barrio, en colaboración con veterinarios locales.",
                proponente=vecino1,
                junta_vecinos=junta,
                estado="pendiente",
            )



            
            # 8. Crear solicitudes de certificados
            self.stdout.write("📄 Creando solicitudes de certificados...")
            
            SolicitudCertificado.objects.create(
                vecino=vecino1,
                tipo="Certificado de Residencia",
                motivo="Para trámite bancario",
                estado="aprobado",
                resuelto_por=directivo
            )
            
            SolicitudCertificado.objects.create(
                vecino=vecino2,
                tipo="Certificado de Residencia",
                motivo="Para postulación a subsidio para aprobar",
                estado="pendiente"
            )
            SolicitudCertificado.objects.create(
                vecino=vecino2,
                tipo="Certificado de Residencia",
                motivo="Para postulación a subsidio para rechazar",
                estado="pendiente"
            )
            
            self.stdout.write(self.style.SUCCESS(
                f"""
                ✅ ¡Datos iniciales creados exitosamente!
                
                📊 Resumen:
                • 1 Junta de Vecinos
                • 4 Usuarios (1 admin, 1 directivo, 2 vecinos)
                • 3 Noticias
                • 3 Actividades
                • 2 Inscripciones
                • 2 Espacios comunes
                • 2 Proyectos vecinales
                • 2 Solicitudes de certificados
                
                🔑 Credenciales de acceso:
                • Administrador: admin@juntavecinos.cl / admin123
                • Directivo: directivo@juntavecinos.cl / directivo123
                • Vecino 1: juan.perez@email.com / vecino123
                • Vecino 2: ana.garcia@email.com / vecino123
                """
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creando datos iniciales: {e}'))
            import traceback
            traceback.print_exc()