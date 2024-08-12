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
        currentActive.classList.setAttribute('aria-selected', 'false');
      }
      this.classList.add('active');
      this.classList.setAttribute('aria-selected', 'true');
      var chatId = this.getAttribute('data-chat-id');
      fetch(`/get_chat_content/${chatId}/`)
  .then(response => response.json())
  .then(data => {
    console.log(data); // Verifica que los mensajes tengan un id en la consola
    const chatContainer = document.querySelector('.col-md-8');
    const moduloContainer = document.getElementById('maudeModuloModal');
    const idChat = document.getElementById('cuerpoModal');
    idChat.setAttribute('chat', chatId);
    
    let contentHtml = `
      <h4 class="mt-3">${data.nombre}</h4>
      <div class="chat-history">
    `;
    
    let contentModal = data.modulo;
    
    data.mensajes.forEach((mensaje) => {
      const estado = mensaje.estado;
      const botonBienActivo = estado === 'bien' ? 'active' : '';
      const botonMalActivo = estado === 'mal' ? 'active' : '';
    
      contentHtml += `
        <div class="mensaje" data-mensaje-id="${mensaje.mensaje_id}">
          <div class="row">
            <p class="usuario">
              <img src="${userLogoUrl}" alt="logoMaude" width="20" height="20">Tú:
            </p>
          </div>
          <div class="row">
            <p>${mensaje.comando}</p>
          </div>
        </div>
        <div class="respuesta">
          <div class="row">
            <p class="maude">
              <img src="${maudeLogoUrl}" alt="logoMaude" width="20" height="20">Maude: 
              <span class="modulo-titulo">${mensaje.titulo_modulo}</span>
            </p>
          </div>
          <div class="row">
            <p>${mensaje.respuesta}</p>
          </div>
          <div class="row justify-content-start"">
            <div class="col-2">
              <button class="btn btn-outline-success btn-sm ${botonBienActivo}" onclick="actualizarEstadoMensaje('${mensaje.mensaje_id}', 'bien')">
                <i class="bi bi-check-circle">✓</i>
              </button>
            </div>
            <div class="col-2">
              <button class="btn btn-outline-danger btn-sm ${botonMalActivo}" onclick="actualizarEstadoMensaje('${mensaje.mensaje_id}', 'mal')">
                <i class="bi bi-x-circle">X</i>
              </button>
            </div>
          </div>
        </div>`;
    });
    
    contentHtml += `
      </div>
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

    if (!chatId) {
        console.error("No hay un chat activo seleccionado.");
        return;
    }

    const commandInput = document.getElementById('maudeCommand');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const maudeCode = document.getElementById('codigoMaude').value;

    const formData = new FormData();
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
                <div class="mensaje" data-mensaje-id="${data.mensaje_id}">
                    <div class="row">
                        <p class="usuario"><img src="${userLogoUrl}" alt="logoMaude" width="20" height="20">Tú:</p>
                    </div>
                    <div class="row">
                        <p>${data.comando}</p>
                    </div>
                </div>
                <div class="respuesta">
                    <div class="row">
                        <p class="maude">
                            <img src="${maudeLogoUrl}" alt="logoMaude" width="20" height="20">Maude(<span class="modulo-titulo">${data.titulo_modulo}</span>):
                        </p>
                    </div>
                    <div class="row">
                        <p>${data.respuesta}</p>
                    </div>
                    <div class="row justify-content-start">
                      <div class="col-2">
                          <button class="btn btn-outline-success btn-sm" onclick="actualizarEstadoMensaje('${data.mensaje_id}', 'bien')">
                              <i class="bi bi-check-circle">✓</i>
                          </button>
                      </div>
                      <div class="col-2">
                          <button class="btn btn-outline-danger btn-sm" onclick="actualizarEstadoMensaje('${data.mensaje_id}', 'mal')">
                              <i class="bi bi-x-circle">X</i>
                          </button>
                      </div>
                  </div>
                </div>`;
            commandInput.value = '';
            historySection.scrollTop = historySection.scrollHeight; // Desplazar la vista al final
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

document.addEventListener("DOMContentLoaded", function () {
  function deleteChats() {
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
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
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
        // Podrías querer actualizar la lista de chats aquí
        selectedCheckboxes.forEach(checkbox => {
          const chatItem = checkbox.closest('.d-flex'); // Asumiendo que cada checkbox está dentro de un contenedor '.d-flex'
          chatItem.remove();
        });

      })
      .catch(error => {
        console.error('Error:', error);
      });
  }

  // Obtiene el botón de eliminar chats y le asigna el eventListener
  const deleteChatsButton = document.getElementById('deleteChatsButton');
  if (deleteChatsButton) {
    deleteChatsButton.addEventListener('click', deleteChats);
  }
});
document.addEventListener('DOMContentLoaded', function () {
  const newChatForm = document.getElementById('newChatForm');
  const newChatModal = new bootstrap.Modal(document.getElementById('newChatModal'));

  if (newChatForm) {
    newChatForm.addEventListener('submit', function (event) {
      event.preventDefault();
      const chatName = document.getElementById('chatName').value.trim(); // trim para evitar nombres solo con espacios
      if (chatName === "") {
        alert('Por favor, introduzca un nombre válido para el chat.');
        return;
      }

      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

      fetch('/new_chat/', {
        method: 'POST',
        body: JSON.stringify({ nombre: chatName }),
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Failed to create chat');
          }
          return response.json();
        })
        .then(data => {
          if (data.status === 'success') {
            renderChatList(data.chats);
            newChatModal.hide();
            newChatForm.reset();
          } else {
            alert('Error al crear el chat: ' + data.message);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Error al crear el chat.');
        });
    });
  }

  function renderChatList(chats) {
    const chatList = document.querySelector('.list-group');
    chatList.innerHTML = ''; // Limpiar la lista existente
    chats.forEach(chat => {
      const chatItemHTML = `
                <div class="d-flex align-items-center list-group-item list-group-item-action">
                    <a href="#" class="chat-link flex-grow-1 list-group-item-action" data-chat-id="${chat.id}">
                        ${chat.nombre}
                    </a>
                    <input class="form-check-input chat-checkbox me-1" type="checkbox" value="${chat.id}" id="deleteChat${chat.id}">
                </div>`;
      chatList.insertAdjacentHTML('beforeend', chatItemHTML);
    });
    addChatListeners(); // Re-aplica listeners para los nuevos elementos
  }

  function addChatListeners() {
    const chatLinks = document.querySelectorAll('.chat-link');
    chatLinks.forEach(link => {
      link.removeEventListener('click', handleChatLinkClick);
      link.addEventListener('click', handleChatLinkClick);
    });
  }

  function handleChatLinkClick(event) {
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
        updateChatContent(data, chatId); // Aquí pasas chatId como segundo argumento
      })
      .catch(error => console.error('Error:', error));
  }

  function updateChatContent(data, chatId) {
    const chatContainer = document.querySelector('.col-md-8');
    const moduloContainer = document.getElementById('maudeModuloModal');
    const idChat = document.getElementById('cuerpoModal');
    var maudeLogoUrl = document.getElementById('staticUrlsMaude').getAttribute('data-maude-logo-url');
    var userLogoUrl = document.getElementById('staticUrlsUser').getAttribute('data-user-logo-url');

    idChat.setAttribute('chat', chatId); // Usar chatId que ahora está disponible como argumento
    let contentHtml = `<h4 class="mt-3">${data.nombre}</h4><div class="chat-history">`;
    let contentModal = data.modulo;
    
    data.mensajes.forEach((mensaje) => {
      const estado = mensaje.estado;
      const botonBienActivo = estado === 'bien' ? 'active' : '';
      const botonMalActivo = estado === 'mal' ? 'active' : '';
      const botonBienColor = estado !== 'mal' ? 'text-success' : 'text-muted';
      const botonMalColor = estado !== 'bien' ? 'text-danger' : 'text-muted';
    
      contentHtml += `
        <div class="mensaje" data-mensaje-id="${mensaje.mensaje_id}">
          <div class="row">
            <p class="usuario">
              <img src="${userLogoUrl}" alt="logoMaude" width="20" height="20">Tú:
            </p>
          </div>
          <div class="row">
            <p>${mensaje.comando}</p>
          </div>
        </div>
        <div class="respuesta">
          <div class="row">
            <p class="maude">
              <img src="${maudeLogoUrl}" alt="logoMaude" width="20" height="20">Maude: 
              <span class="modulo-titulo">${mensaje.titulo_modulo}</span>
            </p>
          </div>
          <div class="row">
            <p>${mensaje.respuesta}</p>
          </div>
          <div class="row justify-content-start">
            <div class="col-2">
              <button class="btn btn-outline-success btn-sm ${botonBienActivo} ${botonBienColor}" onclick="actualizarEstadoMensaje('${mensaje.mensaje_id}', 'bien')">
                <i class="bi bi-check-circle">✓</i>
              </button>
            </div>
            <div class="col-2">
              <button class="btn btn-outline-danger btn-sm ${botonMalActivo} ${botonMalColor}" onclick="actualizarEstadoMensaje('${mensaje.mensaje_id}', 'mal')">
                <i class="bi bi-x-circle">X</i>
              </button>
            </div>
          </div>
        </div>`;
    });
    
    contentHtml += `
      </div>
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
}


  addChatListeners();

  window.renderChatList = function (chats) { // Función global para llamar desde cualquier actualización de lista
    const chatList = document.querySelector('.list-group');
    chatList.innerHTML = ''; // Limpiar la lista existente
    chats.forEach(chat => {
      const chatItemHTML = `<div class="d-flex align-items-center list-group-item list-group-item-action"><a href="#" class="chat-link flex-grow-1 list-group-item-action" data-chat-id="${chat.id}">${chat.nombre}</a><input class="form-check-input chat-checkbox me-1" type="checkbox" value="${chat.id}" id="deleteChat${chat.id}"></div>`;
      chatList.insertAdjacentHTML('beforeend', chatItemHTML);
    });
    addChatListeners(); // Re-asignar listeners después de actualizar la lista
  };
});

document.addEventListener('DOMContentLoaded', function () {
  const marketModal = document.getElementById('marketModal');
  marketModal.addEventListener('show.bs.modal', function () {
    fetchModules();
  });

  function fetchModules() {
    const query = document.getElementById('market-search-input').value || '';
    const orderBy = document.getElementById('market-order-by').value;
    const direction = document.getElementById('market-direction').value;
    const status = document.getElementById('market-status').value;

    fetch(`/get_available_modules/?q=${query}&order_by=${orderBy}&direction=${direction}&status=${status}`)
      .then(response => response.text())
      .then(data => {
        const marketModalBody = document.getElementById('marketModalBody');
        marketModalBody.querySelector('#market-modulos-list').innerHTML = data;
        attachModuleEventHandlers();
      })
      .catch(error => console.error('Error al cargar los módulos:', error));
  }

  document.getElementById('market-search-input').addEventListener('input', fetchModules);
  document.getElementById('market-order-by').addEventListener('change', fetchModules);
  document.getElementById('market-direction').addEventListener('change', fetchModules);
  document.getElementById('market-status').addEventListener('change', fetchModules);

  function attachModuleEventHandlers() {
    document.querySelectorAll('.download-btn').forEach(function(button) {
      button.addEventListener('click', function() {
        const codigo = this.getAttribute('data-codigo');
        const titulo = this.getAttribute('data-titulo');
        const chatId = document.querySelector('.chat-link.active').getAttribute('data-chat-id');
        saveModuleVersion(chatId, titulo, codigo);
      });
    });

    document.querySelectorAll('.info-btn').forEach(function(button) {
      button.addEventListener('click', function() {
        const moduleId = this.getAttribute('data-module-id');
        showModuleInfo(moduleId);
      });
    });
}


  function saveModuleVersion(chatId, titulo, codigo) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    fetch('/create_version/', {
      method: "POST",
      body: JSON.stringify({
          chat_id: chatId,
          titulo: titulo,
          codigo: codigo
      }),
      headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json"
      },
  })
  .then(response => response.json())
  .then(data => {
      if (data.status === 'success') {
        const modalElement = document.getElementById('marketModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
      } else {
          console.error('Error al crear la nueva versión');
      }
  })
  .catch(error => console.error('Error:', error));
  }

  function showModuleInfo(moduleId) {
    const marketModalElement = document.getElementById('marketModal');
    const marketModal = bootstrap.Modal.getInstance(marketModalElement);
    const moduleInfoModal = new bootstrap.Modal(document.getElementById('moduleInfoModal'));

    // Cerrar el modal del Market
    marketModal.hide();

    fetch(`/get_module_info/${moduleId}/`)
      .then(response => response.json())
      .then(data => {
        const moduleInfoBody = document.getElementById('moduleInfoBody');
        moduleInfoBody.innerHTML = `
          <h5>Nombre: ${data.info.nombre}</h5>
          <p>Descripción: ${data.info.descripcion}</p>
          <pre><code>${data.info.codigo_maude}</code></pre>
        `;
        // Mostrar el modal de información del módulo
        moduleInfoModal.show();

        // Configurar el evento para volver a abrir el modal del Market al cerrar el modal de información del módulo
        document.getElementById('moduleInfoModal').addEventListener('hidden.bs.modal', function () {
          marketModal.show();
        }, { once: true });
      })
      .catch(error => console.error('Error al obtener la información del módulo:', error));
}

});


document.addEventListener('DOMContentLoaded', function () {
  // Manejar la apertura del modal de opciones del módulo
  document.getElementById('opcionesModuloModal').addEventListener('show.bs.modal', function () {
    const chatId = document.querySelector('.chat-link.active').getAttribute('data-chat-id');
    document.getElementById('chatIdModificar').value = chatId;
    document.getElementById('chatIdSeleccionar').value = chatId;
    document.getElementById('chatIdComparar').value = chatId;
  });

  // Manejar la apertura del modal de modificación del módulo y cargar el código actual
  document.getElementById('modificarModuloModal').addEventListener('show.bs.modal', function () {
    const chatId = document.getElementById('chatIdModificar').value;
    fetch(`/get_chat_content/${chatId}/`)
      .then(response => response.json())
      .then(data => {
        document.getElementById('codigoMaude').value = data.modulo;
      })
      .catch(error => console.error('Error:', error));
  });

  // Manejar el formulario de modificación del módulo
  document.getElementById('modificarModuloForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const chatId = document.getElementById('chatIdModificar').value;
    const titulo = document.getElementById('tituloVersion').value;
    const codigo = document.getElementById('codigoMaude').value;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/create_version/', {
      method: 'POST',
      body: JSON.stringify({ chat_id: chatId, titulo: titulo, codigo: codigo }),
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          alert('Versión creada con éxito');
          document.getElementById('modificarModuloModal').querySelector('.btn-close').click();
        } else {
          alert('Error al crear la versión');
        }
      })
      .catch(error => console.error('Error:', error));
  });

  // Manejar la apertura del modal de selección de versión
  document.getElementById('seleccionarVersionModal').addEventListener('show.bs.modal', function () {
    const chatId = document.getElementById('chatIdSeleccionar').value;
    const versionSelect = document.getElementById('versionSelect');

    fetch(`/get_versions/${chatId}/`)
      .then(response => response.json())
      .then(data => {
        versionSelect.innerHTML = '';
        data.forEach(version => {
          const option = document.createElement('option');
          option.value = version.id;
          option.textContent = `${version.titulo} - ${version.fecha_creacion}`;
          versionSelect.appendChild(option);
        });
      })
      .catch(error => console.error('Error:', error));
  });

  // Manejar el formulario de selección de versión
  document.getElementById('seleccionarVersionForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const selectedVersionId = document.getElementById('versionSelect').value;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/select_version/', {
      method: "POST",
      body: JSON.stringify({ version_id: selectedVersionId }),
      headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
      },
  })
  .then(response => response.json())
  .then(data => {
      if (data.status === 'success') {
        const modalElement = document.getElementById('seleccionarVersionModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
      } else {
          console.error('Error al seleccionar la versión');
      }
  })
  .catch(error => console.error('Error:', error));  
  });

  // Manejar la apertura del modal de comparación de versiones
  document.getElementById('compararVersionesModal').addEventListener('show.bs.modal', function () {
    const chatId = document.getElementById('chatIdComparar').value;
    const versionSelect1 = document.getElementById('versionSelect1');
    const versionSelect2 = document.getElementById('versionSelect2');

    fetch(`/get_versions/${chatId}/`)
      .then(response => response.json())
      .then(data => {
        versionSelect1.innerHTML = '';
        versionSelect2.innerHTML = '';
        data.forEach(version => {
          const option1 = document.createElement('option');
          const option2 = document.createElement('option');
          option1.value = version.id;
          option2.value = version.id;
          option1.textContent = `${version.titulo} - ${version.fecha_creacion}`;
          option2.textContent = `${version.titulo} - ${version.fecha_creacion}`;
          versionSelect1.appendChild(option1);
          versionSelect2.appendChild(option2);
        });
      })
      .catch(error => console.error('Error:', error));
  });

  // Manejar el formulario de comparación de versiones
  document.getElementById('compararVersionesForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const versionId1 = document.getElementById('versionSelect1').value;
    const versionId2 = document.getElementById('versionSelect2').value;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/compare_versions/', {
      method: 'POST',
      body: JSON.stringify({ version_id_1: versionId1, version_id_2: versionId2 }),
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          document.getElementById('diffOutput').innerHTML = data.diff;
        } else {
          alert('Error al comparar las versiones');
        }
      })
      .catch(error => console.error('Error:', error));
  });
});

function actualizarEstadoMensaje(mensajeId, nuevoEstado) {
  console.log('ID del mensaje:', mensajeId);  // Asegúrate de que este valor no sea undefined

  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  fetch(`/update_message_status/`, {
      method: 'POST',
      body: JSON.stringify({ mensaje_id: mensajeId, estado: nuevoEstado }),
      headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
      },
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      return response.json();
  })
  .then(data => {
      if (data.status === 'success') {
          // Actualiza los botones según el nuevo estado
          const botonBien = document.querySelector(`button[onclick="actualizarEstadoMensaje('${mensajeId}', 'bien')"]`);
          const botonMal = document.querySelector(`button[onclick="actualizarEstadoMensaje('${mensajeId}', 'mal')"]`);

          if (nuevoEstado === 'bien') {
              botonBien.classList.add('active');
              botonBien.classList.remove('text-muted');
              botonBien.classList.add('text-success');

              botonMal.classList.remove('active');
              botonMal.classList.add('text-muted');
              botonMal.classList.remove('text-danger');
          } else if (nuevoEstado === 'mal') {
              botonMal.classList.add('active');
              botonMal.classList.remove('text-muted');
              botonMal.classList.add('text-danger');

              botonBien.classList.remove('active');
              botonBien.classList.add('text-muted');
              botonBien.classList.remove('text-success');
          }
      }
  })
  .catch(error => console.error('Error al actualizar el estado del mensaje:', error));
}

document.addEventListener('DOMContentLoaded', function () {
  const entregarModal = document.getElementById('entregarModal');

  entregarModal.addEventListener('show.bs.modal', function () {
    const activeChatLink = document.querySelector('.chat-link.active');
    const chatId = activeChatLink ? activeChatLink.getAttribute('data-chat-id') : '';

    if (chatId) {
      fetch(`/get_mensajes_bien/${chatId}/`)
        .then(response => response.json())
        .then(data => {
          const mensajesContainer = document.getElementById('mensajesBienContainer');
          let mensajesHtml = '';

          if (data.mensajes.length > 0) {
            data.mensajes.forEach(mensaje => {
              mensajesHtml += `
                <div class="alert alert-success">
                  <strong>Comando:</strong> ${mensaje.comando}<br>
                  <strong>Respuesta:</strong> ${mensaje.respuesta}<br>
                  <strong>Título módulo:</strong> ${mensaje.titulo_modulo}
                </div>`;
            });
          } else {
            mensajesHtml = '<p>No hay mensajes con estado "bien".</p>';
          }

          mensajesContainer.innerHTML = mensajesHtml;

          // Cargar la lista de administradores en el select
          const administradorSelect = document.getElementById('administradorSelect');
          administradorSelect.innerHTML = ''; // Limpiar el select
          data.administradores.forEach(administrador => {
            const option = document.createElement('option');
            option.value = administrador.id;
            option.textContent = administrador.nombre;
            administradorSelect.appendChild(option);
          });
        })
        .catch(error => console.error('Error:', error));
    }
  });
});

document.addEventListener('DOMContentLoaded', function () {
  const entregarForm = document.getElementById('entregarForm');
  const userId = document.getElementById('userInfo').getAttribute('data-user-id');

  entregarForm.addEventListener('submit', function (event) {
    event.preventDefault();

    const activeChatLink = document.querySelector('.chat-link.active');
    const chatId = activeChatLink ? activeChatLink.getAttribute('data-chat-id') : '';
    const administradorId = document.getElementById('administradorSelect').value;
    const tituloEntrega = document.getElementById('tituloEntrega').value;

    if (!administradorId) {
      alert('Por favor, selecciona un administrador.');
      return;
    }

    if (!tituloEntrega) {
      alert('Por favor, introduce un título para la entrega.');
      return;
    }

    if (chatId) {
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

      fetch(`/enviar_mensajes_bien/${chatId}/`, {
        method: 'POST',
        body: JSON.stringify({
          administrador_id: administradorId,
          titulo: tituloEntrega,
          remitente_id: userId  // Utiliza la variable userId que leíste del atributo data-*
        }),
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            alert('Mensajes enviados correctamente.');
            const modal = bootstrap.Modal.getInstance(entregarModal);
            modal.hide();
          } else {
            alert('Error al enviar los mensajes.');
          }
        })
        .catch(error => console.error('Error:', error));
    }
  });
});
