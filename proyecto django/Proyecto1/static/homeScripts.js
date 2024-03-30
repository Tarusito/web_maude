document.addEventListener('DOMContentLoaded', function () {
    const chatColumn = document.getElementById('columnaChats'); // Ajusta la clase según tu layout
    const toggleButton = document.getElementById('toggle-chats-btn');

    toggleButton.addEventListener('click', function () {
      chatColumn.classList.toggle('hidden'); // 'hidden' es una clase que oculta el elemento
    });
  });

  //funcion para guardar el modulo en la base de datos con el modal
  document.addEventListener('DOMContentLoaded', function () {
    const botonModalModulo = document.getElementById('modalBoton'); // Ajusta la clase según tu layout

    botonModalModulo.addEventListener('click', function () {
      const chatId = activeChatLink ? activeChatLink.getAttribute('data-chat-id') : '';

      if (!chatId) {
        console.error("No hay un chat activo seleccionado.");
        return;
      }

      const moduloMaude = document.getElementById('maudeModuloModal').value;
      fetch(`/saveModule/${chatId}/`, {
        method: "POST",
        body: moduloMaude,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
      .catch(error => console.error('Error:', error));
    })
  
  });
  
  document.addEventListener("DOMContentLoaded", function () {
    var chatLinks = document.querySelectorAll('.chat-link');
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
            let contentHtml = `
              <h4 class="mt-3">${data.nombre}</h4>
              <div id="maudeModuleSection" class="mb-3">
                <h5>Módulo Maude:</h5>
                <textarea id="maudeCode" class="form-control" rows="5">${data.modulo}</textarea>
              </div>
              <div class="chat-history">`;
            data.mensajes.forEach(mensaje => {
              contentHtml += `
                <div class="mensaje">
                  <p class="usuario">Tú:</p>
                  <p>${mensaje.comando}</p>
                </div>
                <div class="respuesta">
                  <p class="maude">Maude:</p>
                  <p>${mensaje.respuesta}</p>
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
          })
          .catch(error => console.error('Error:', error));
      });
    });

    // Botón para ocultar/mostrar el código del módulo
    document.getElementById("toggleModuleButton").addEventListener("click", function () {
      var moduleSection = document.getElementById("maudeModuleSection");
      if (moduleSection) {
        moduleSection.classList.toggle("hidden");
      }
    });
    
    function sendMaudeCommand() {
      const activeChatLink = document.querySelector('.chat-link.active');
      const chatId = activeChatLink ? activeChatLink.getAttribute('data-chat-id') : '';

      if (!chatId) {
        console.error("No hay un chat activo seleccionado.");
        return;
      }
      var commandInput = document.getElementById('maudeCommand');
      var csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
      var maudeCode = document.getElementById('maudeCode').value;
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
      if (event.target && event.target.matches("#maudeForm .btn-primary")) {
        sendMaudeCommand();
      }
    });

    const chatHistory = document.querySelector('.chat-history');
    if (chatHistory) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

  });