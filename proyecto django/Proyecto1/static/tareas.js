function showEntregaDetails(entregaId) {
    fetch(`/entrega_detalles/${entregaId}/`)
        .then(response => response.json())
        .then(data => {
            // Rellenar el modal con la información de la entrega
            document.getElementById('modalTitulo').textContent = data.titulo;
            document.getElementById('modalAdministrador').textContent = data.administrador;
            document.getElementById('modalFecha').textContent = data.fecha;
            document.getElementById('modalEstado').textContent = data.corregido ? 'Corregida' : 'No corregida';

            if (data.corregido) {
                document.getElementById('notaSection').style.display = 'block';
                document.getElementById('modalNota').textContent = data.nota;
            } else {
                document.getElementById('notaSection').style.display = 'none';
            }

            const mensajesHtml = data.mensajes.map(mensaje => `
                <div class="alert alert-secondary">
                    <div class="row">
                        <div class="col">
                            <div class="row">
                                <div class="col">
                                    <strong>Comando:</strong> ${mensaje.comando}<br>
                                    <strong>Respuesta:</strong> ${mensaje.respuesta}<br>
                                </div>
                                <div class="col">
                                    <div class="row">
                                        <p><strong>Código del Módulo:</strong></p>
                                    </div>
                                    <div class="row">
                                        <pre><code>${mensaje.codigo_maude}</code></pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`).join('');

            document.getElementById('modalMensajes').innerHTML = mensajesHtml;

            // Mostrar el modal
            const modal = new bootstrap.Modal(document.getElementById('entregaModal'));
            modal.show();
        })
        .catch(error => console.error('Error:', error));
}

function eliminarEntregasSeleccionadas() {
    const selectedCheckboxes = document.querySelectorAll('.entrega-checkbox:checked');
    const selectedIds = Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
    console.log(selectedIds)

    if (selectedIds.length === 0) {
        alert('No has seleccionado ninguna entrega.');
        return;
    }

    if (!confirm(`¿Estás seguro de que deseas eliminar las ${selectedIds.length} entregas seleccionadas?`)) {
        return;
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/eliminar_entregas/`, {
        method: 'POST',
        body: JSON.stringify({ ids: selectedIds }),
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Entregas eliminadas correctamente.');
            fetchEntregas();  // Recargar la lista de entregas
        } else {
            alert('Error al eliminar las entregas.');
        }
    })
    .catch(error => console.error('Error:', error));
}



function fetchEntregas(page = 1) {
    const searchInput = document.getElementById('searchInput');
    const orderSelect = document.getElementById('orderSelect');
    const corregidoSelect = document.getElementById('corregidoSelect');

    const params = new URLSearchParams();
    const searchQuery = searchInput.value;
    const orderValue = orderSelect.value;
    const corregidoValue = corregidoSelect.value;

    if (searchQuery) {
        params.append('q', searchQuery);
    }
    if (orderValue) {
        const [orderBy, direction] = orderValue.split('_');
        params.append('order_by', orderBy === 'fecha' ? 'fecha' : orderBy);
        params.append('direction', direction);
    }
    if (corregidoValue !== 'both') {
        params.append('corregido', corregidoValue);
    }
    params.append('page', page);

    fetch(`/entregas_usuario/?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            const entregasContainer = document.getElementById('entregasContainer');
            let entregasHtml = '';

            if (data.entregas.length > 0) {
                data.entregas.forEach(entrega => {
                    entregasHtml += `
                        <div class="col-md-4 mb-3">
                            <div class="card">
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col">
                                            <div class="row">
                                                <input type="checkbox" class="form-check-input entrega-checkbox" value="${entrega.id}">
                                                <h5 class="card-title d-inline">${entrega.titulo}</h5>
                                                <p class="card-text"><strong>Fecha de Entrega:</strong> ${entrega.fecha}</p>
                                                <p class="card-text"><strong>Estado:</strong> ${entrega.corregido ? 'Corregida' : 'No corregida'}</p>
                                                ${entrega.nota ? `<p class="card-text rounded-pill"><strong>Nota del Administrador:</strong> ${entrega.nota}</p>` : ''}
                                                <button class="btn btn-primary" onclick="showEntregaDetails(${entrega.id})">Ver Detalles</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                });

                // Agregar paginación
                entregasHtml += `
                    <div class="col-12 mt-3">
                        <nav aria-label="Page navigation">
                            <ul class="pagination justify-content-center">
                                ${data.has_previous ? `<li class="page-item"><a class="page-link" href="#" onclick="fetchEntregas(${data.page - 1})">Anterior</a></li>` : ''}
                                ${Array.from({ length: data.num_pages }, (_, i) => i + 1).map(pageNum => `
                                    <li class="page-item ${data.page === pageNum ? 'active' : ''}">
                                        <a class="page-link" href="#" onclick="fetchEntregas(${pageNum})">${pageNum}</a>
                                    </li>`).join('')}
                                ${data.has_next ? `<li class="page-item"><a class="page-link" href="#" onclick="fetchEntregas(${data.page + 1})">Siguiente</a></li>` : ''}
                            </ul>
                        </nav>
                    </div>`;
            } else {
                entregasHtml = '<p>No hay entregas disponibles.</p>';
            }

            entregasContainer.innerHTML = entregasHtml;
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const orderSelect = document.getElementById('orderSelect');
    const corregidoSelect = document.getElementById('corregidoSelect');
    let currentPage = 1;

    searchInput.addEventListener('input', () => fetchEntregas(currentPage));
    orderSelect.addEventListener('change', () => fetchEntregas(currentPage));
    corregidoSelect.addEventListener('change', () => fetchEntregas(currentPage));

    // Cargar entregas iniciales
    fetchEntregas(currentPage);
});
