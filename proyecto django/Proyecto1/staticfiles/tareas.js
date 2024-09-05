document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const orderSelect = document.getElementById('orderSelect');
    const corregidoSelect = document.getElementById('corregidoSelect');

    function fetchEntregas() {
        const searchQuery = searchInput.value;
        const order = orderSelect.value.split('_');
        const orderBy = order[0];
        const direction = order[1];
        const corregido = corregidoSelect.value;

        const params = new URLSearchParams({
            q: searchQuery,
            order_by: orderBy,
            direction: direction,
            corregido: corregido
        });

        function fetchEntregas() {
            fetch(`/entregas_usuario/?${params.toString()}`)
                .then(response => response.json())
                .then(data => {
                    const entregasContainer = document.getElementById('entregasContainer');
                    let entregasHtml = '';
    
                    if (data.length > 0) {
                        data.forEach(entrega => {
                            entregasHtml += `
                                <div class="col-md-4 mb-3">
                                    <div class="card">
                                        <div class="card-body">
                                            <h5 class="card-title">${entrega.titulo}</h5>
                                            <p class="card-text"><strong>Fecha de Entrega:</strong> ${new Date(entrega.fecha_entrega).toLocaleDateString()}</p>
                                            <p class="card-text"><strong>Estado:</strong> ${entrega.corregido ? 'Corregido' : 'Pendiente'}</p>
                                            ${entrega.nota ? `<p class="card-text"><strong>Nota del Administrador:</strong> ${entrega.nota}</p>` : ''}
                                        </div>
                                    </div>
                                </div>`;
                        });
                    } else {
                        entregasHtml = '<p>No hay entregas disponibles.</p>';
                    }
    
                    entregasContainer.innerHTML = entregasHtml;
                })
                .catch(error => console.error('Error:', error));
        }
    }

    searchInput.addEventListener('input', fetchEntregas);
    orderSelect.addEventListener('change', fetchEntregas);
    corregidoSelect.addEventListener('change', fetchEntregas);

    // Cargar entregas iniciales
    fetchEntregas();
});
