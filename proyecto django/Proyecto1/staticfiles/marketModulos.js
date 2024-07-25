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
