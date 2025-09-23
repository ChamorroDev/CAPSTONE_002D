document.addEventListener('DOMContentLoaded', async function() {
    // Genera la URL base dinámicamente usando la ubicación actual del navegador.

    
    const token = localStorage.getItem('access_token');
    
    // Obtenemos el ID del proyecto desde la URL.
    const pathSegments = window.location.pathname.split('/');
    const proyectoId = pathSegments[pathSegments.length - 2];

    const urlApiProyecto = `${URL_API}api/proyectos/${proyectoId}/`;

    // Elementos del DOM para actualizar
    const tituloProyecto = document.getElementById('titulo-proyecto');
    const proponenteProyecto = document.getElementById('proponente-proyecto');
    const descripcionProyecto = document.getElementById('descripcion-proyecto');
    const estadoProyecto = document.getElementById('estado-proyecto');
    const fechaCreacionProyecto = document.getElementById('fecha-creacion-proyecto');

    // Botones de acción
    const aprobarBtn = document.getElementById('aprobar-btn');
    const rechazarBtn = document.getElementById('rechazar-btn');
    
    try {
        const response = await fetch(urlApiProyecto, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const proyecto = await response.json();
            
            // Actualizamos el contenido de la página con los datos de la API
            if (tituloProyecto) tituloProyecto.textContent = proyecto.titulo;
            if (proponenteProyecto) proponenteProyecto.textContent = `Enviado por ${proyecto.proponente_nombre}`;
            if (descripcionProyecto) descripcionProyecto.textContent = proyecto.descripcion;
            if (estadoProyecto) estadoProyecto.textContent = proyecto.estado;
            if (fechaCreacionProyecto) fechaCreacionProyecto.textContent = `Fecha de Creación: ${proyecto.fecha_creacion}`;
            
            // Si el proyecto no está pendiente, ocultamos los botones de acción
            if (proyecto.estado !== 'pendiente') {
                if (aprobarBtn) aprobarBtn.style.display = 'none';
                if (rechazarBtn) rechazarBtn.style.display = 'none';
            } else {
                // Asignamos la funcionalidad a los botones de acción
                if (aprobarBtn) aprobarBtn.addEventListener('click', () => enviarAccion('aprobar'));
                if (rechazarBtn) rechazarBtn.addEventListener('click', () => enviarAccion('rechazar'));
            }

        } else {
            console.error('Error al cargar los detalles del proyecto:', response.status);
            alert('Error al cargar los detalles del proyecto.');
        }

    } catch (error) {
        console.error('Error de conexión:', error);
        alert('Error de conexión. Por favor, inténtalo de nuevo.');
    }

    async function enviarAccion(accion) {
        try {
            const urlAccion = `${URL_API}api/proyectos/${proyectoId}/${accion}/`;
            const response = await fetch(urlAccion, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Se usa una variable para construir el mensaje dinámicamente
                const mensajeAccion = accion === 'aprobar' ? 'aprobó' : 'rechazó';
                alert(`Proyecto se ${mensajeAccion} correctamente. Volviendo a la lista.`);
                window.location.href = '/proyectos_lista/';
            } else {
                alert(`Error al ${accion} el proyecto.`);
            }
        } catch (error) {
            alert(`Error de conexión.`);
        }
    }
});