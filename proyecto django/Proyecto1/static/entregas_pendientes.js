let currentEntregaId = null;

function showEntregaDetails(entregaId) {
    fetch(`/entrega_detalles/${entregaId}/`)
        .then(response => response.json())
        .then(data => {
            // Rellenar el modal con la información de la entrega
            document.getElementById('modalTitulo').textContent = data.titulo;
            document.getElementById('modalRemitente').textContent = data.remitente;
            
            const mensajesHtml = data.mensajes.map(mensaje => `
                <div class="alert alert-secondary">
                    <strong>Comando:</strong> ${mensaje.comando}<br>
                    <strong>Respuesta:</strong> ${mensaje.respuesta}<br>
                    <strong>Código del Módulo:</strong> ${mensaje.codigo_maude}
                </div>`).join('');

            document.getElementById('modalMensajes').innerHTML = mensajesHtml;
            currentEntregaId = entregaId;

            // Mostrar el modal
            const modal = new bootstrap.Modal(document.getElementById('corregirModal'));
            modal.show();
        })
        .catch(error => console.error('Error:', error));
}

function corregirEntrega(entregaId) {
    const notaInput = document.getElementById('notaInput');
    if (!notaInput) {
        alert('No se pudo encontrar el campo para la nota.');
        return;
    }

    const nota = notaInput.value;
    console.log(nota)
    if (!nota) {
        alert('Por favor, ingrese una nota antes de corregir.');
        return;
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    

    fetch(`/corregir_entrega/${entregaId}/`, {
        method: 'POST',
        body: JSON.stringify({ nota: nota }),
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Entrega corregida con éxito.');
            const modal = bootstrap.Modal.getInstance(document.getElementById('corregirModal'));
            modal.hide();
            fetchEntregas();  // Recargar la lista de entregas pendientes
        } else {
            alert('Error al corregir la entrega.');
        }
    })
    .catch(error => console.error('Error:', error));
}

function fetchEntregas(page = 1) {
    const searchInput = document.getElementById('searchInput');
    const orderSelect = document.getElementById('orderSelect');

    const params = new URLSearchParams();
    const searchQuery = searchInput.value;
    const orderValue = orderSelect.value;

    if (searchQuery) {
        params.append('q', searchQuery);
    }
    if (orderValue) {
        const [orderBy, direction] = orderValue.split('_');
        params.append('order_by', orderBy === 'fecha' ? 'fecha' : orderBy);
        params.append('direction', direction);
    }
    params.append('page', page);

    fetch(`/entregas_pendientes_data/?${params.toString()}`)
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
                                    <h5 class="card-title">${entrega.titulo}</h5>
                                    <p class="card-text"><strong>Fecha de Entrega:</strong> ${entrega.fecha}</p>
                                    <p class="card-text"><strong>Remitente:</strong> ${entrega.remitente}</p>
                                    <button class="btn btn-primary" onclick="showEntregaDetails(${entrega.id})">Corregir</button>
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
                entregasHtml = '<p>No hay entregas pendientes.</p>';
            }

            entregasContainer.innerHTML = entregasHtml;
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const orderSelect = document.getElementById('orderSelect');
    let currentPage = 1;

    searchInput.addEventListener('input', () => fetchEntregas(currentPage));
    orderSelect.addEventListener('change', () => fetchEntregas(currentPage));

    // Cargar entregas iniciales
    fetchEntregas(currentPage);
});
