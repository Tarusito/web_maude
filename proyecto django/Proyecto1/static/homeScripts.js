document.addEventListener('DOMContentLoaded', function () {
    const chatColumn = document.getElementById('columnaChats'); // Ajusta la clase según tu layout
    const toggleButton = document.getElementById('toggle-chats-btn');

    toggleButton.addEventListener('click', function () {
      chatColumn.classList.toggle('hidden'); // 'hidden' es una clase que oculta el elemento
    });
  });

  document.addEventListener('DOMContentLoaded', function () {
    const botonModalModulo = document.getElementById('modalBoton');
    botonModalModulo.addEventListener('click', function () {
      const modalBody = document.getElementById('cuerpoModal');
      var chatId = modalBody.getAttribute('chat');
      const moduloMaude = document.getElementById('maudeModuloModal').value;
      // Obtener el token CSRF del meta tag
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
      console.log(moduloMaude);
      console.log(csrfToken); // Esto debería mostrarte el token CSRF correctamente en la consola.
  
      fetch(`/saveModule/${chatId}/`, {
        method: "POST",
        body: moduloMaude,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": csrfToken, // Asegúrate de que el nombre de la cabecera es "X-CSRFToken"
          "Content-Type": "application/json" // Añadido para asegurar que el contenido se envía como JSON
        },
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json(); // O manejar la respuesta según sea necesario.
      })
      .then(data => {
        console.log(data); // Procesar los datos de la respuesta.
      })
      .catch(error => console.error('Error:', error));
    });
  });
  
  
  
  document.addEventListener("DOMContentLoaded", function () {
    var chatLinks = document.querySelectorAll('.chat-link');
    var maudeLogoUrl = document.getElementById('staticUrlsMaude').getAttribute('data-maude-logo-url');
    var userLogoUrl = document.getElementById('staticUrlsUser').getAttribute('data-user-logo-url');
    chatLinks.forEach(function (link) {
      link.addEventListener('click', function (event) {
        event.preventDefault();
        const currentActive = document.querySelector('.chat-link.active');
            if (currentActive) {
                currentActive.classList.remove('active');
            }
            this.classList.add('active');
        var chatId = this.getAttribute('data-chat-id');
        fetch(`/get_chat_content/${chatId}/`)
          .then(response => response.json())
          .then(data => {
            console.log(data);
            const chatContainer = document.querySelector('.col-md-8');
            const moduloContainer = document.getElementById('maudeModuloModal');
            const idChat = document.getElementById('cuerpoModal')
            idChat.setAttribute('chat', chatId);
            moduloContainer
            let contentHtml = `
            <h4 class="mt-3">${data.nombre}</h4>
            <div class="chat-history">
              `;
            let contentModal = data.modulo;         
            data.mensajes.forEach(mensaje => {
              contentHtml += `
              <div class="mensaje">
              <div class="row">
                <p class="usuario"><img src="${userLogoUrl}" alt="logoMaude" width="20" height="20">Tú:</p>
              </div>
              <div class="row">
                <p>${mensaje.comando}</p>
              </div>
            </div>
            
            <div class="respuesta">
              <div class="row">
                  <p class="maude"><img src="${maudeLogoUrl}" alt="logoMaude" width="20" height="20">Maude:</p>
              </div>
              <div class="row">
                <p>${mensaje.respuesta}</p>
              </div>
            </div>`;
            });
            contentHtml += `</div>
              <div class="chat-input">
                <form id="maudeForm">
                  <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
                  <div class="input-group mb-3">
                    <input type="text" id="maudeCommand" name="maude_execution" class="form-control" placeholder="Escribe tu comando aquí...">
                    <button class="btn btn-primary" type="button">Enviar</button>
                  </div>
                </form>
              </div>`;
            chatContainer.innerHTML = contentHtml;
            moduloContainer.innerHTML = contentModal;
          })
          .catch(error => console.error('Error:', error));
      });
    });

    
    function sendMaudeCommand() {
      const activeChatLink = document.querySelector('.chat-link.active');
      const chatId = activeChatLink ? activeChatLink.getAttribute('data-chat-id') : '';

      console.log("entro en el sendcomando");

      if (!chatId) {
        console.error("No hay un chat activo seleccionado.");
        return;
      }
      var commandInput = document.getElementById('maudeCommand');
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
      var maudeCode = document.getElementById('maudeModuloModal').value;
      var formData = new FormData();
      formData.append('csrfmiddlewaretoken', csrfToken);
      formData.append('maude_code', maudeCode);
      formData.append('maude_execution', commandInput.value);

      fetch(`/run_maude_command/${chatId}/`, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
      .then(response => response.json())
      .then(data => {
        const historySection = document.querySelector('.chat-history');
        if (historySection) {
          historySection.innerHTML += `
            <div class="mensaje">
              <p class="usuario">Tú:</p>
              <p>${data.comando}</p>
            </div>
            <div class="respuesta">
              <p class="maude">Maude:</p>
              <p>${data.respuesta}</p>
            </div>`;
          commandInput.value = '';
        }
      })
      .catch(error => console.error('Error:', error));
    }

    // Asigna el controlador sendMaudeCommand al botón de enviar en el formulario actualizado del chat
    document.addEventListener('click', function (event) {
      console.log("entro en el click");
      if (event.target && event.target.matches("#maudeForm .btn-primary")) {
        sendMaudeCommand();
      }
    });

    const chatHistory = document.querySelector('.chat-history');
    if (chatHistory) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

  });

  // Selecciona el botón y asigna el evento click
const deleteChatsButton = document.getElementById('deleteChatsButton');

if(deleteChatsButton) {
  deleteChatsButton.addEventListener('click', deleteChats);
}
deleteChatsButton.addEventListener('click', function () {
  // Selecciona los checkboxes marcados
  const selectedCheckboxes = document.querySelectorAll('.chat-checkbox:checked');
  // Obtiene los IDs de los chats a eliminar
  const chatIds = Array.from(selectedCheckboxes).map(cb => cb.value);

  // Asegúrate de que al menos un chat ha sido seleccionado
  if (chatIds.length === 0) {
    alert('Selecciona al menos un chat para eliminar.');
    return;
  }

  // Confirma con el usuario
  if (!confirm('¿Estás seguro de que quieres eliminar los chats seleccionados?')) {
    return;
  }

  // CSRF token necesario para la petición POST
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  // Datos a enviar
  const formData = new FormData();
  formData.append('chat_ids', JSON.stringify(chatIds));

  // Ejecuta la petición fetch para enviar los datos al servidor
  fetch('/ruta-para-eliminar-chats/', { // Sustituye con la ruta correcta
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': csrfToken,
    },
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Error en la respuesta de la red');
    }
    return response.json();
  })
  .then(data => {
    // Actualiza la UI aquí si es necesario
    alert('Chats eliminados correctamente');
  })
  .catch(error => {
    console.error('Error:', error);
  });
});
