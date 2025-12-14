/**
 * MODAL-MANAGER.JS - Gestión centralizada de modales
 * Centro Minero SENA
 * 
 * Soluciona problemas comunes con modales de Bootstrap:
 * - Múltiples backdrops
 * - Scroll bloqueado
 * - Z-index conflicts
 */

(function() {
  'use strict';
  
  // ==========================================
  // CONFIGURACIÓN
  // ==========================================
  
  const config = {
    cleanupBackdrops: true,
    restoreScroll: true,
    debug: false
  };
  
  // ==========================================
  // GESTIÓN DE BACKDROPS
  // ==========================================
  
  function cleanupBackdrops() {
    const backdrops = document.querySelectorAll('.modal-backdrop');
    const openModals = document.querySelectorAll('.modal.show');
    
    // Si no hay modales abiertos, remover todos los backdrops
    if (openModals.length === 0) {
      backdrops.forEach(backdrop => backdrop.remove());
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }
    // Si hay múltiples backdrops, mantener solo uno
    else if (backdrops.length > 1) {
      for (let i = 1; i < backdrops.length; i++) {
        backdrops[i].remove();
      }
    }
  }
  
  // ==========================================
  // EVENT LISTENERS
  // ==========================================
  
  // Limpiar al cerrar cualquier modal
  document.addEventListener('hidden.bs.modal', function(e) {
    if (config.cleanupBackdrops) {
      // Pequeño delay para que Bootstrap termine su limpieza
      setTimeout(cleanupBackdrops, 100);
    }
    
    if (config.debug) {
      console.log('Modal cerrado:', e.target.id);
    }
  });
  
  // Prevenir múltiples backdrops al abrir modales
  document.addEventListener('show.bs.modal', function(e) {
    if (config.cleanupBackdrops) {
      cleanupBackdrops();
    }
    
    if (config.debug) {
      console.log('Modal abierto:', e.target.id);
    }
  });
  
  // ==========================================
  // API PÚBLICA
  // ==========================================
  
  window.ModalManager = {
    /**
     * Limpiar backdrops manualmente
     */
    cleanup: cleanupBackdrops,
    
    /**
     * Abrir modal por ID
     * @param {string} modalId - ID del modal (sin #)
     */
    open: function(modalId) {
      const modalElement = document.getElementById(modalId);
      if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
      }
    },
    
    /**
     * Cerrar modal por ID
     * @param {string} modalId - ID del modal (sin #)
     */
    close: function(modalId) {
      const modalElement = document.getElementById(modalId);
      if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
          modal.hide();
        }
      }
    },
    
    /**
     * Cerrar todos los modales
     */
    closeAll: function() {
      document.querySelectorAll('.modal.show').forEach(modal => {
        const instance = bootstrap.Modal.getInstance(modal);
        if (instance) {
          instance.hide();
        }
      });
    },
    
    /**
     * Configurar el manager
     * @param {Object} options - Opciones de configuración
     */
    configure: function(options) {
      Object.assign(config, options);
    }
  };
  
  // ==========================================
  // INICIALIZACIÓN
  // ==========================================
  
  // Limpiar al cargar la página (por si hay backdrops residuales)
  document.addEventListener('DOMContentLoaded', function() {
    setTimeout(cleanupBackdrops, 500);
  });
  
  if (config.debug) {
    console.log('✅ Modal Manager inicializado');
  }
  
})();
