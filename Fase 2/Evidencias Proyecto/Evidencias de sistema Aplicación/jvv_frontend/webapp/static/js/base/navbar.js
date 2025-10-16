// Función de login compatible con navbar seguro
async function login(email, password) {
    try {
        const response = await fetch(`${URL_API}api/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Guardar datos
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            localStorage.setItem('user_role', data.user.rol);

            // Actualizar navbar de forma segura
            if (typeof safeNavbarUpdate === 'function') {
                safeNavbarUpdate();
            }

            return { success: true, data };
        } else {
            return { success: false, error: data.detail || 'Error en el login' };
        }
    } catch (error) {
        return { success: false, error: 'Error de conexión' };
    }
}

// Función de logout compatible
function logout() {
    if (typeof safeLogout === 'function') {
        safeLogout();
    } else {
        // Fallback seguro
        if (confirm('¿Está seguro que desea cerrar sesión?')) {
            localStorage.clear();
            window.location.href = "/login/";
        }
    }
}

// Actualiza dinámicamente el navbar según el estado de autenticación
function safeNavbarUpdate() {
    const authSection = document.getElementById('navbar-auth-section');
    const userData = localStorage.getItem('user_data');
    const userRole = localStorage.getItem('user_role');
    
    // Referencias a los elementos del menú
    const navEventos = document.getElementById('nav-eventos-link');
    const navMiBarrio = document.getElementById('nav-mibarrio-link');
    const navPanelControl = document.getElementById('nav-panel-control-link');

    // Ocultar todos los enlaces por defecto
    if (navEventos) navEventos.style.display = 'none';
    if (navMiBarrio) navMiBarrio.style.display = 'none';
    if (navPanelControl) navPanelControl.style.display = 'none';

    if (authSection) {
        if (userData) {
            // Usuario logeado: mostrar links específicos y botón de logout
            const user = JSON.parse(userData);
            authSection.innerHTML = `
                <span class="me-3 text-white fw-bold">
                    <a href="${miPerfilUrl}" class="text-white text-decoration-none">
                        <i class="bi bi-person-circle"></i> ${user.nombre || user.username || 'Usuario'}
                    </a>
                </span>
                <button class="btn btn-outline-light btn-sm" onclick="logout()">
                    <i class="bi bi-box-arrow-right"></i> Cerrar sesión
                </button>
            `;
            
            // Mostrar los links si el usuario está logeado
            if (navEventos) navEventos.style.display = 'block';
            if (navMiBarrio) navMiBarrio.style.display = 'block';
            
            // Lógica para mostrar el panel de control solo a directivos
            if (navPanelControl && userRole === 'directivo') {
                navPanelControl.style.display = 'block';
            }
            
        } else {
            // Usuario no logeado: mostrar botones de login/registro
            authSection.innerHTML = `
                <a class="btn btn-secondary me-2" href="/registro/">
                    <i class="bi bi-person-plus"></i> Registrarse
                </a>
                <a class="btn btn-light" href="/login/">
                    <i class="bi bi-box-arrow-in-right"></i> Iniciar sesión
                </a>
            `;
        }
    }
}
window.safeNavbarUpdate = safeNavbarUpdate;

document.addEventListener('DOMContentLoaded', function() {
    var navbarCollapse = document.getElementById('navbarNav');
    if (navbarCollapse) {
        navbarCollapse.querySelectorAll('.nav-link').forEach(function(link) {
            link.addEventListener('click', function() {
                // Solo cerrar si está visible (en mobile)
                if (navbarCollapse.classList.contains('show')) {
                    var collapseInstance = bootstrap.Collapse.getOrCreateInstance(navbarCollapse);
                    collapseInstance.hide();
                }
            });
        });
    }
});


// Llama a la función al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    safeNavbarUpdate();
});