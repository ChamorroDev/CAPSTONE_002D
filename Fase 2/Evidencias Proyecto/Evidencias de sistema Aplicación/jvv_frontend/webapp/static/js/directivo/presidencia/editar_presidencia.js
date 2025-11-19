// gestion_presidente.js

let presidenteActual = null;
let directivosDisponibles = [];

// --- Función para obtener CSRF token si lo necesitas ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- Inicialización ---
document.addEventListener('DOMContentLoaded', async () => {
    await fetchConfigPresidente();

    // Event listeners
    document.getElementById('asignar-presidente-btn').addEventListener('click', async () => {
        await asignarPresidente();
    });

    document.getElementById('actualizar-firma-btn').addEventListener('click', async () => {
        await actualizarFirma();
    });
});

// --- Fetch de datos de la API ---
async function fetchConfigPresidente() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${URL_API}api/directivo/obtener_firma_presidente/`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Error al obtener configuración');

        const data = await response.json();
        console.log("Datos obtenidos: ", data);

        presidenteActual = data.presidente_actual;
        directivosDisponibles = data.directivos_disponibles;

        renderPresidente();
        renderDirectivos();
    } catch (error) {
        console.error('Error:', error);
        alert('No se pudo cargar la configuración del presidente.');
    }
}

// --- Renderizar presidente actual ---
function renderPresidente() {
    const div = document.getElementById('presidente-info');
    if (!presidenteActual || !presidenteActual.id) {
        div.innerHTML = `<p>No hay presidente asignado actualmente.</p>`;
        return;
    }

    div.innerHTML = `
        <p><strong>Nombre:</strong> ${presidenteActual.nombre}</p>
        <p><strong>RUT:</strong> ${presidenteActual.rut}</p>
        <p><strong>Firma:</strong></p>
        ${presidenteActual.firma_url
            ? `<img src="${presidenteActual.firma_url}" class="img-fluid" style="max-width: 250px;">`
            : `<p class="text-muted">No hay firma registrada.</p>`}
    `;
}

// --- Renderizar dropdown de directivos disponibles ---
function renderDirectivos() {
    const select = document.getElementById('directivos-select');
    select.innerHTML = '';

    directivosDisponibles.forEach(d => {
        const option = document.createElement('option');
        option.value = d.id;
        option.textContent = `${d.nombre_completo} - ${d.rut}`;
        select.appendChild(option);
    });
}

// --- Asignar presidente ---
async function asignarPresidente() {
    const userId = document.getElementById('directivos-select').value;
    if (!userId) {
        alert('Debe seleccionar un directivo.');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${URL_API}api/directivo/establecer_presidente/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Error al asignar presidente');

        alert(data.mensaje);
        await fetchConfigPresidente(); // refrescar datos
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// --- Actualizar firma ---
async function actualizarFirma() {
    const fileInput = document.getElementById('firma-file');
    if (!fileInput.files.length) {
        alert('Debe seleccionar un archivo de firma.');
        return;
    }

    const formData = new FormData();
    formData.append('firma', fileInput.files[0]);

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${URL_API}api/directivo/actualizar_firma_presidente/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Error al actualizar firma');

        alert(data.mensaje);
        fileInput.value = ''; // limpiar input
        await fetchConfigPresidente(); // refrescar datos
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}
