document.addEventListener("DOMContentLoaded", function () {
  var exampleModal = document.getElementById('moduloModal');
  exampleModal.addEventListener('show.bs.modal', function (event) {
      // Botón que activó el modal
      var button = event.relatedTarget;
      // Extraer información de los atributos data-*
      var nombre = button.getAttribute('data-nombre');
      var descripcion = button.getAttribute('data-descripcion');
      var imagen = button.getAttribute('data-imagen');

      // Depuración
      console.log("Nombre:", nombre);
      console.log("Descripción:", descripcion);
      console.log("Imagen:", imagen);

      // Actualizar los contenidos del modal.
      var modalTitle = exampleModal.querySelector('.modal-title');
      var modalBodyDescription = exampleModal.querySelector('.modal-body #modalDescription');
      var modalBodyImage = exampleModal.querySelector('.modal-body #modalImage');

      modalTitle.textContent = nombre;
      modalBodyDescription.textContent = descripcion;
      modalBodyImage.src = imagen;
  });
});

document.addEventListener("DOMContentLoaded", function () {
  function attachToggleHandlers() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
      $('.toggle-btn').off('click').on('click', function() {
          var button = $(this);
          var moduloNombre = button.data('nombre');

          $.ajax({
              url: '/toggle_modulo/' + moduloNombre + '/',
              type: 'POST',
              data: {
                  'csrfmiddlewaretoken': csrfToken
              },
              success: function(response) {
                  if (response.success) {
                      if (response.activo) {
                          button.removeClass('btn-success').addClass('btn-warning');
                          button.text('Desactivar');
                      } else {
                          button.removeClass('btn-warning').addClass('btn-success');
                          button.text('Activar');
                      }
                  } else {
                      alert('Error al actualizar el estado del módulo.');
                  }
              },
              error: function() {
                  alert('Error al actualizar el estado del módulo.');
              }
          });
      });
  }

  function fetchModulos() {
      var query = $('#search-input').val();
      var order_by = $('#order-by').val();
      var direction = $('#direction').val();
      var status = $('#status').val();

      $.ajax({
        url: marketModulosUrl,
        type: 'GET',
        data: {
            'q': query,
            'order_by': order_by,
            'direction': direction,
            'status': status
        },
        success: function(data) {
            $('#modulos-list').html(data);
            attachToggleHandlers();
            $('#search-input').val(query); // Mantener el valor de búsqueda
        },
        error: function() {
            alert('Error al realizar la búsqueda.');
        }
    });
    
  }

    $(document).ready(function() {
      attachToggleHandlers();

      $('#search-input').on('input', fetchModulos);
      $('#order-by, #direction, #status').on('change', fetchModulos);

      var exampleModal = document.getElementById('moduloModal');
      var guardarBtn = exampleModal.querySelector('.modal-body #guardarBtn');
      var modalCodigo = exampleModal.querySelector('.modal-body #modalCodigo');
      var modalBodyDescription = exampleModal.querySelector('.modal-body #modalDescription');
      var imagenInput = exampleModal.querySelector('.modal-body #imagenModulo');

      exampleModal.addEventListener('show.bs.modal', function(event) {
          var button = event.relatedTarget;
          var nombre = button.getAttribute('data-nombre');
          var descripcion = button.getAttribute('data-descripcion');
          var imagen = button.getAttribute('data-imagen');
          var codigo = button.getAttribute('data-codigo');

          var modalTitle = exampleModal.querySelector('.modal-title');
          var modalBodyImage = exampleModal.querySelector('.modal-body #modalImage');

          modalTitle.textContent = nombre;
          modalBodyDescription.value = descripcion;
          modalBodyImage.src = imagen;
          modalCodigo.value = codigo;

          var initialCodigo = codigo;
          var initialDescripcion = descripcion;

          function handleInputChange() {
              if (modalCodigo.value !== initialCodigo || modalBodyDescription.value !== initialDescripcion || imagenInput.files.length > 0) {
                  guardarBtn.style.display = 'block';
              } else {
                  guardarBtn.style.display = 'none';
              }
          }

          modalCodigo.removeEventListener('input', handleInputChange);
          modalCodigo.addEventListener('input', handleInputChange);
          modalBodyDescription.removeEventListener('input', handleInputChange);
          modalBodyDescription.addEventListener('input', handleInputChange);
          imagenInput.removeEventListener('change', handleInputChange);
          imagenInput.addEventListener('change', handleInputChange);

          guardarBtn.removeEventListener('click', handleSaveClick);
          guardarBtn.addEventListener('click', handleSaveClick);

          const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

          function handleSaveClick() {
              var formData = new FormData();
              formData.append('csrfmiddlewaretoken', csrfToken);
              formData.append('codigo_maude', modalCodigo.value);
              formData.append('descripcion', modalBodyDescription.value);
              if (imagenInput.files.length > 0) {
                  formData.append('imagen', imagenInput.files[0]);
              }

              $.ajax({
                url: '/update_modulo/' + encodeURIComponent(nombre) + '/',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.success) {
                        alert('Módulo actualizado con éxito.');
                        $('#moduloModal').modal('hide');
                        fetchModulos(); // Recargar la lista de módulos
                    } else {
                        alert('Error al actualizar el módulo.');
                    }
                },
                error: function() {
                    alert('Error al actualizar el módulo.');
                }
            });
          }
      });


      // Manejar la creación del módulo
      $('#crearModuloForm').on('submit', function(event) {
          event.preventDefault();
          var formData = new FormData(this);
          const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
          formData.append('csrfmiddlewaretoken', csrfToken);

          $.ajax({
              url: '/create_modulo/',
              type: 'POST',
              data: formData,
              processData: false,
              contentType: false,
              success: function(response) {
                  if (response.success) {
                      alert('Módulo creado con éxito.');
                      $('#crearModuloModal').modal('hide');
                      fetchModulos();
                  } else {
                      alert('Error al crear el módulo.');
                  }
              },
              error: function() {
                  alert('Error al crear el módulo.');
              }
          });
      });
  });
});
document.addEventListener("DOMContentLoaded", function () {
  const deleteSelectedButton = document.getElementById('deleteSelected');

  function toggleDeleteButton() {
      const checkboxes = document.querySelectorAll('.delete-checkbox');
      const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
      deleteSelectedButton.style.display = anyChecked ? 'inline-block' : 'none';
  }
  function fetchModulos() {
    var query = $('#search-input').val();
    var order_by = $('#order-by').val();
    var direction = $('#direction').val();
    var status = $('#status').val();

    $.ajax({
      url: marketModulosUrl,
      type: 'GET',
      data: {
          'q': query,
          'order_by': order_by,
          'direction': direction,
          'status': status
      },
      success: function(data) {
          $('#modulos-list').html(data);
          attachToggleHandlers();
          $('#search-input').val(query); // Mantener el valor de búsqueda
      },
      error: function() {
          alert('Error al realizar la búsqueda.');
      }
  });
  
}

  document.addEventListener('change', function (event) {
      if (event.target.classList.contains('delete-checkbox')) {
          toggleDeleteButton();
      }
  });

  deleteSelectedButton.addEventListener('click', function () {
      const selectedCheckboxes = document.querySelectorAll('.delete-checkbox:checked');
      const idsToDelete = Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

      if (confirm(`¿Está seguro de que desea eliminar ${idsToDelete.length} módulo(s)?`)) {
          $.ajax({
              url: '/delete_modulos/',  
              type: 'POST',
              data: JSON.stringify({ ids: idsToDelete }),
              contentType: 'application/json',
              headers: {
                  'X-CSRFToken': csrfToken
              },
              success: function (response) {
                  if (response.success) {
                      alert('Módulos eliminados con éxito.');
                      fetchModulos();  
                  } else {
                      alert('Error al eliminar los módulos.');
                  }
              },
              error: function () {
                  alert('Error al eliminar los módulos.');
              }
          });
      }
  });

  toggleDeleteButton(); 
});
