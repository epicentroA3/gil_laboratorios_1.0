/**
 * MAIN.JS - Scripts principales del sistema GIL
 * Centro Minero SENA
 */

// ==========================================
// INICIALIZACIÓN
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
  console.log('🔬 Sistema GIL - Centro Minero SENA');
  
  // Inicializar componentes
  initSidebar();
  initFAB();
  initFooterCarousel();
  initTooltips();
});

// ==========================================
// SIDEBAR
// ==========================================

function initSidebar() {
  const toggleBtn = document.getElementById('toggleSidebar');
  const sidebar = document.getElementById('sidebar');
  
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      sidebar.classList.toggle('show');
    });
    
    // Cerrar sidebar al hacer clic fuera (mobile)
    document.addEventListener('click', function(e) {
      if (window.innerWidth < 992) {
        if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
          sidebar.classList.remove('show');
        }
      }
    });
  }
}

// ==========================================
// FAB (Floating Action Button)
// ==========================================

function initFAB() {
  const fabBtn = document.getElementById('fabMain');
  const fabMenu = document.getElementById('fabMenu');
  
  if (fabBtn && fabMenu) {
    fabBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      fabMenu.classList.toggle('active');
      fabBtn.classList.toggle('active');
    });
    
    // Cerrar FAB al hacer clic fuera
    document.addEventListener('click', function(e) {
      if (!fabBtn.contains(e.target) && !fabMenu.contains(e.target)) {
        fabMenu.classList.remove('active');
        fabBtn.classList.remove('active');
      }
    });
  }
}

// ==========================================
// FOOTER CAROUSEL
// ==========================================

function initFooterCarousel() {
  const slides = document.querySelectorAll('.footer-slide');
  const dots = document.querySelectorAll('.footer-dots .dot');
  
  if (slides.length === 0) return;
  
  let currentSlide = 0;
  let autoPlayInterval;
  
  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === index);
    });
    dots.forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });
  }
  
  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }
  
  // Auto-rotate every 5 seconds
  autoPlayInterval = setInterval(nextSlide, 5000);
  
  // Click on dots
  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      currentSlide = index;
      showSlide(currentSlide);
      // Reset autoplay
      clearInterval(autoPlayInterval);
      autoPlayInterval = setInterval(nextSlide, 5000);
    });
  });
}

// ==========================================
// TOOLTIPS
// ==========================================

function initTooltips() {
  // Bootstrap tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipTriggerList.forEach(el => {
    new bootstrap.Tooltip(el);
  });
}

// ==========================================
// UTILITIES
// ==========================================

/**
 * Mostrar notificación toast
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo: success, error, warning, info
 */
function showToast(message, type = 'info') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
  alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
  
  const icons = {
    success: 'check-circle',
    error: 'x-circle',
    warning: 'exclamation-triangle',
    info: 'info-circle'
  };
  
  alertDiv.innerHTML = `
    <i class="bi bi-${icons[type] || 'info-circle'} me-2"></i>
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  document.body.appendChild(alertDiv);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    alertDiv.classList.remove('show');
    setTimeout(() => alertDiv.remove(), 300);
  }, 5000);
}

/**
 * Formatear fecha
 * @param {string|Date} date - Fecha a formatear
 * @returns {string} Fecha formateada
 */
function formatDate(date) {
  const d = new Date(date);
  return d.toLocaleDateString('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
}

/**
 * Formatear hora
 * @param {string|Date} date - Fecha/hora a formatear
 * @returns {string} Hora formateada
 */
function formatTime(date) {
  const d = new Date(date);
  return d.toLocaleTimeString('es-CO', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Confirmar acción
 * @param {string} message - Mensaje de confirmación
 * @returns {Promise<boolean>} Resultado de la confirmación
 */
function confirmAction(message) {
  return new Promise((resolve) => {
    resolve(confirm(message));
  });
}

/**
 * Copiar texto al portapapeles
 * @param {string} text - Texto a copiar
 */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copiado al portapapeles', 'success');
  } catch (err) {
    showToast('Error al copiar', 'error');
  }
}

// ==========================================
// KEYBOARD SHORTCUTS
// ==========================================

document.addEventListener('keydown', function(e) {
  // Alt + L = Logout
  if (e.altKey && e.key === 'l') {
    e.preventDefault();
    window.location.href = '/logout';
  }
  
  // Alt + D = Dashboard
  if (e.altKey && e.key === 'd') {
    e.preventDefault();
    window.location.href = '/dashboard';
  }
  
  // Escape = Cerrar modales y menús
  if (e.key === 'Escape') {
    const fabMenu = document.getElementById('fabMenu');
    if (fabMenu) fabMenu.classList.remove('active');
    
    const sidebar = document.getElementById('sidebar');
    if (sidebar && window.innerWidth < 992) {
      sidebar.classList.remove('show');
    }
  }
});

// Exportar funciones globales
window.GIL = {
  showToast,
  formatDate,
  formatTime,
  confirmAction,
  copyToClipboard
};
