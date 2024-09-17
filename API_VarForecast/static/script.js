document.addEventListener('DOMContentLoaded', function() {
    // Función para poblar los dropdowns
    async function loadDropdownOptions() {
        const response = await fetch('/filter-options');
        const data = await response.json();
        
        populateDropdown('grupo-filter', data.grupo);
        populateDropdown('sistema-filter', data.sistema);
        populateDropdown('formato-filter', data.formato);
        populateDropdown('categoria-filter', data.categoria);
        populateDropdown('pinta-filter', data.pinta);
        populateDropdown('item-filter', data.item);
    }

    function populateDropdown(dropdownId, options) {
        const dropdown = document.getElementById(dropdownId);
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.value;
            opt.text = option.label;
            dropdown.appendChild(opt);
        });
    }

    // Función para actualizar opciones basadas en el filtro seleccionado
    async function updateFilterOptions() {
        const grupoFilter = document.getElementById('grupo-filter').value;
        const response = await fetch(`/filter-options?grupo=${grupoFilter}`);
        const data = await response.json();
        
        populateDropdown('sistema-filter', data.sistema);
        populateDropdown('formato-filter', data.formato);
        populateDropdown('categoria-filter', data.categoria);
        populateDropdown('pinta-filter', data.pinta);
        populateDropdown('item-filter', data.item);
    }

    // Llamar a la función al cargar la página
    loadDropdownOptions();

    // Event listeners para actualizar filtros
    document.getElementById('grupo-filter').addEventListener('change', updateFilterOptions);

    // Event listener para aplicar los filtros y actualizar el gráfico
    document.getElementById('apply-filters').addEventListener('click', async function() {
        const grupoFilter = document.getElementById('grupo-filter').value;
        const sistemaFilter = document.getElementById('sistema-filter').value;
        const formatoFilter = document.getElementById('formato-filter').value;
        const categoriaFilter = document.getElementById('categoria-filter').value;
        const pintaFilter = document.getElementById('pinta-filter').value;
        const itemFilter = document.getElementById('item-filter').value;

        const queryParams = new URLSearchParams({
            grupo: grupoFilter,
            sistema: sistemaFilter,
            formato: formatoFilter,
            categoria: categoriaFilter,
            pinta: pintaFilter,
            item: itemFilter
        });

        const response = await fetch(`/filtered-data?${queryParams.toString()}`);
        const plotData = await response.json();

        // Actualizar el gráfico con los datos filtrados
        Plotly.newPlot('plotContainer', plotData.data, plotData.layout);
    });
});
