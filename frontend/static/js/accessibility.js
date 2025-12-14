/**
 * ACCESSIBILITY.JS - Gestión de accesibilidad
 * Centro Minero SENA
 */

(function() {
  'use strict';

  // Aplicar preferencias guardadas
  function aplicarAccesibilidad() {
    const body = document.body;
    const altoContraste = localStorage.getItem('accesibilidad_alto_contraste') === 'true';
    const tamanoTexto = localStorage.getItem('accesibilidad_tamano_texto') || '100';
    const modoOscuro = localStorage.getItem('accesibilidad_modo_oscuro') === 'true';
    const animaciones = localStorage.getItem('accesibilidad_animaciones') === 'true';
    
    body.classList.toggle('alto-contraste', altoContraste);
    body.classList.toggle('modo-oscuro', modoOscuro);
    body.classList.toggle('animaciones-reducidas', animaciones);
    body.style.fontSize = tamanoTexto + '%';
    
    // Actualizar controles del modal si existen
    const switchAC = document.getElementById('switchAltoContraste');
    const rangeTT = document.getElementById('rangeTamanoTexto');
    const badgeTT = document.getElementById('badgeTamanoTexto');
    const switchMO = document.getElementById('switchModoOscuro');
    const switchAN = document.getElementById('switchAnimaciones');
    
    if (switchAC) switchAC.checked = altoContraste;
    if (rangeTT) {
      rangeTT.value = tamanoTexto;
      if (badgeTT) badgeTT.textContent = tamanoTexto + '%';
    }
    if (switchMO) switchMO.checked = modoOscuro;
    if (switchAN) switchAN.checked = animaciones;
  }

  // Inicializar cuando el DOM esté listo
  document.addEventListener('DOMContentLoaded', function() {
    aplicarAccesibilidad();
    
    // Guardar preferencias
    const btnGuardar = document.getElementById('btnGuardarAccesibilidad');
    if (btnGuardar) {
      btnGuardar.addEventListener('click', function() {
        const altoContraste = document.getElementById('switchAltoContraste')?.checked || false;
        const tamanoTexto = document.getElementById('rangeTamanoTexto')?.value || '100';
        const modoOscuro = document.getElementById('switchModoOscuro')?.checked || false;
        const animaciones = document.getElementById('switchAnimaciones')?.checked || false;
        
        localStorage.setItem('accesibilidad_alto_contraste', altoContraste);
        localStorage.setItem('accesibilidad_tamano_texto', tamanoTexto);
        localStorage.setItem('accesibilidad_modo_oscuro', modoOscuro);
        localStorage.setItem('accesibilidad_animaciones', animaciones);
        
        aplicarAccesibilidad();
        
        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalAccesibilidad'));
        if (modal) modal.hide();
        
        // Mostrar notificación
        if (window.GIL && window.GIL.showToast) {
          window.GIL.showToast('Configuración guardada exitosamente', 'success');
        }
      });
    }
    
    // Aplicar cambios en tiempo real - Switches
    ['switchAltoContraste', 'switchModoOscuro', 'switchAnimaciones'].forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        element.addEventListener('change', function() {
          const body = document.body;
          if (id === 'switchAltoContraste') {
            body.classList.toggle('alto-contraste', this.checked);
          } else if (id === 'switchModoOscuro') {
            body.classList.toggle('modo-oscuro', this.checked);
          } else if (id === 'switchAnimaciones') {
            body.classList.toggle('animaciones-reducidas', this.checked);
          }
        });
      }
    });
    
    // Aplicar cambios en tiempo real - Tamaño de texto
    const rangeTamano = document.getElementById('rangeTamanoTexto');
    const badgeTamano = document.getElementById('badgeTamanoTexto');
    if (rangeTamano) {
      rangeTamano.addEventListener('input', function() {
        const valor = this.value;
        if (badgeTamano) badgeTamano.textContent = valor + '%';
        document.body.style.fontSize = valor + '%';
      });
    }
  });

  // Exportar función global
  window.aplicarAccesibilidad = aplicarAccesibilidad;
})();
