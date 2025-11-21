import { api } from '../api.js';
import { formatCurrency } from '../utils.js';
import { escapeHtml } from '../sanitize.js';

export async function renderProjects(container) {
    let currentProjectId = null;
    let editingProjectId = null;
    let allocationTableData = null;
    let currentSortBy = 'name'; // default sort by name
    let currentSortDirection = 'asc'; // default ascending

    container.innerHTML = `
        <div class="card">
            <div class="header-actions">
                <h3>Lista de Projetos</h3>
                <button id="btn-new-project" class="btn btn-primary">
                    <span class="material-icons" style="margin-right: 0.5rem;">add</span>
                    Novo Projeto
                </button>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; padding: 0 0.5rem;">
                <label style="font-size: 0.875rem; color: var(--md-sys-color-on-surface-variant); font-weight: 500;">Ordenar por:</label>
                <select id="sort-select" style="padding: 0.5rem; border: 1px solid var(--md-sys-color-outline); border-radius: 0.25rem; background: var(--md-sys-color-surface); color: var(--md-sys-color-on-surface); font-size: 0.875rem;">
                    <option value="name">Nome</option>
                    <option value="start_date">Data de Início</option>
                    <option value="created_at">Data de Criação</option>
                </select>
                <button id="sort-direction-btn" class="btn btn-sm" style="display: flex; align-items: center; gap: 0.25rem; min-width: auto; padding: 0.5rem 0.75rem;">
                    <span class="material-icons" id="sort-icon" style="font-size: 1.25rem;">arrow_upward</span>
                </button>
            </div>
            <div id="projects-list"></div>
        </div>
        
        <div class="card" id="proj-details" style="display:none;">
            <h3 id="proj-title-display">Detalhes do Projeto</h3>
            
            <div class="form-group">
                <label>Aplicar Oferta</label>
                <div style="display: flex; gap: 0.5rem;">
                    <select id="sel-offer"></select>
                    <button id="btn-apply-off" class="btn btn-primary">Aplicar Oferta</button>
                </div>
            </div>
            
            <hr style="margin: 1rem 0;">
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <h4 style="margin: 0;">Tabela de Alocação</h4>
                <button id="btn-add-professional" class="btn btn-sm">➕ Adicionar Profissional</button>
            </div>
            <div id="allocation-table-container" style="overflow-x: auto; margin: 1rem 0;">
                <p style="color: #6b7280;">Nenhuma alocação ainda. Aplique uma oferta ou crie alocações manualmente.</p>
            </div>
            
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                <button id="btn-save-calc" class="btn btn-primary" style="display:none;">Salvar & Calcular</button>
                <button id="btn-export-excel" class="btn" style="display:none;">
                    <span class="material-icons" style="margin-right: 0.5rem; font-size: 1.125rem;">file_download</span>
                    Exportar para Excel
                </button>
            </div>
            
            <div id="price-result" style="display:none; margin-top: 1.5rem;">
                <h4 style="margin-bottom: 1rem; color: var(--md-sys-color-on-surface);">Resultado da Precificação</h4>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <!-- Detalhes à esquerda -->
                    <div style="background: var(--md-sys-color-surface-container-low); padding: 1.5rem; border-radius: var(--md-sys-shape-corner-large); box-shadow: var(--md-sys-elevation-1);">
                        <h5 style="margin: 0 0 1rem 0; font-size: 0.875rem; font-weight: 500; color: var(--md-sys-color-on-surface-variant); text-transform: uppercase; letter-spacing: 0.1px;">Detalhes</h5>
                        
                        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.75rem; border-bottom: 1px solid var(--md-sys-color-outline-variant, #C4C7C5);">
                                <span style="color: var(--md-sys-color-on-surface-variant); font-size: 0.875rem;">Custo Total</span>
                                <span id="res-cost" style="font-weight: 500; color: var(--md-sys-color-on-surface); font-size: 1rem;"></span>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.75rem; border-bottom: 1px solid var(--md-sys-color-outline-variant, #C4C7C5);">
                                <span style="color: var(--md-sys-color-on-surface-variant); font-size: 0.875rem;">Venda Total</span>
                                <span id="res-selling" style="font-weight: 500; color: var(--md-sys-color-on-surface); font-size: 1rem;"></span>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.75rem; border-bottom: 1px solid var(--md-sys-color-outline-variant, #C4C7C5);">
                                <span id="label-margin-total" style="color: var(--md-sys-color-on-surface-variant); font-size: 0.875rem;">Margem Total</span>
                                <span id="res-margin" style="font-weight: 500; color: var(--md-sys-color-on-surface); font-size: 1rem;"></span>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span id="label-tax-total" style="color: var(--md-sys-color-on-surface-variant); font-size: 0.875rem;">Impostos Totais</span>
                                <span id="res-tax" style="font-weight: 500; color: var(--md-sys-color-on-surface); font-size: 1rem;"></span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Cards destacados à direita -->
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                        <!-- Preço Final -->
                        <div style="background: linear-gradient(135deg, var(--md-sys-color-primary-container) 0%, var(--md-sys-color-primary-container) 100%); padding: 1.5rem; border-radius: var(--md-sys-shape-corner-large); box-shadow: var(--md-sys-elevation-2); border: 1px solid var(--md-sys-color-primary);">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span class="material-icons" style="color: var(--md-sys-color-primary); font-size: 1.25rem;">payments</span>
                                <span style="font-size: 0.75rem; font-weight: 500; color: var(--md-sys-color-on-primary-container); text-transform: uppercase; letter-spacing: 0.5px;">Preço Final</span>
                            </div>
                            <div id="res-price" style="font-size: 2rem; font-weight: 700; color: var(--md-sys-color-primary); line-height: 1.2;"></div>
                        </div>
                        
                        <!-- Margem Final -->
                        <div style="background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%); padding: 1.5rem; border-radius: var(--md-sys-shape-corner-large); box-shadow: var(--md-sys-elevation-2); border: 1px solid #10B981;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span class="material-icons" style="color: #059669; font-size: 1.25rem;">trending_up</span>
                                <span style="font-size: 0.75rem; font-weight: 500; color: #065F46; text-transform: uppercase; letter-spacing: 0.5px;">Margem Final</span>
                            </div>
                            <div id="res-final-margin" style="font-size: 2rem; font-weight: 700; color: #059669; line-height: 1.2;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal for Create/Edit Project -->
        <div id="modal-project" class="modal-overlay">
            <div class="modal-container">
                <div class="modal-header">
                    <h3 id="modal-project-title">Novo Projeto</h3>
                    <button class="modal-close" id="btn-close-modal-project">
                        <span class="material-icons">close</span>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Nome</label>
                        <input type="text" id="proj-name">
                    </div>
                    <div class="form-group">
                        <label>Data de Início</label>
                        <input type="date" id="proj-start">
                    </div>
                    <div class="form-group">
                        <label>Duração (Meses)</label>
                        <input type="number" id="proj-duration" value="3">
                    </div>
                    <div class="form-group">
                        <label>Taxa de Impostos (%)</label>
                        <input type="number" id="proj-tax" value="11">
                    </div>
                    <div class="form-group">
                        <label>Taxa de Margem (%)</label>
                        <input type="number" id="proj-margin" value="40">
                    </div>
                </div>
                <div class="modal-footer">
                    <button id="btn-cancel-project" class="btn">Cancelar</button>
                    <button id="btn-save-project" class="btn btn-primary">Criar Projeto</button>
                </div>
            </div>
        </div>

        <!-- Add Professional Modal -->
        <div id="modal-add-prof" style="display:none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 100; align-items: center; justify-content: center;">
            <div style="background: white; padding: 2rem; border-radius: 0.5rem; width: 400px; max-width: 90%;">
                <h3>Adicionar Profissional</h3>
                <div class="form-group">
                    <label>Selecionar Profissional</label>
                    <select id="sel-add-prof" style="width: 100%; padding: 0.5rem;"></select>
                    <p id="disp-prof-cost" style="margin-top: 0.5rem; color: #4b5563; font-size: 0.9rem; font-weight: 500;"></p>
                </div>
                <div class="form-group">
                    <label>Taxa de Venda (Opcional)</label>
                    <input type="number" id="input-add-prof-rate" placeholder="Deixe vazio para cálculo automático" style="width: 100%; padding: 0.5rem;">
                    <small style="color: #6b7280;">Se vazio, calculado a partir do custo + margem</small>
                </div>
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem; justify-content: flex-end;">
                    <button id="btn-cancel-add-prof" class="btn">Cancelar</button>
                    <button id="btn-confirm-add-prof" class="btn btn-primary">Adicionar</button>
                </div>
            </div>
        </div>
    `;

    // Load projects
    await loadProjects();

    // Sort controls event listeners
    document.getElementById('sort-select').addEventListener('change', (e) => {
        currentSortBy = e.target.value;
        loadProjects();
    });

    document.getElementById('sort-direction-btn').addEventListener('click', () => {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
        const icon = document.getElementById('sort-icon');
        icon.textContent = currentSortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward';
        loadProjects();
    });

    // Modal controls for project creation/edit
    const modalProject = document.getElementById('modal-project');

    document.getElementById('btn-new-project').onclick = () => {
        editingProjectId = null;
        document.getElementById('modal-project-title').textContent = 'Novo Projeto';
        document.getElementById('btn-save-project').textContent = 'Criar Projeto';
        clearProjectForm();
        modalProject.classList.add('active');
    };

    document.getElementById('btn-close-modal-project').onclick = () => {
        modalProject.classList.remove('active');
        clearProjectForm();
    };

    document.getElementById('btn-cancel-project').onclick = () => {
        modalProject.classList.remove('active');
        clearProjectForm();
    };

    // Close modal when clicking outside
    modalProject.onclick = (e) => {
        if (e.target === modalProject) {
            modalProject.classList.remove('active');
            clearProjectForm();
        }
    };

    // Save (Create or Update)
    document.getElementById('btn-save-project').onclick = async () => {
        const name = document.getElementById('proj-name').value;
        const start_date = document.getElementById('proj-start').value;
        const duration_months = parseInt(document.getElementById('proj-duration').value);
        const tax_rate = parseFloat(document.getElementById('proj-tax').value);
        const margin_rate = parseFloat(document.getElementById('proj-margin').value);

        if (!name || !start_date) {
            alert('Por favor, preencha todos os campos obrigatórios (Nome e Data de Início).');
            return;
        }

        if (editingProjectId) {
            // Update
            await api.put(`/projects/${editingProjectId}`, {
                name, start_date, duration_months, tax_rate, margin_rate
            });

            // If this project is currently being viewed, reload the allocation table
            if (currentProjectId === editingProjectId) {
                loadAllocationTable(currentProjectId);
            }

            editingProjectId = null;
            modalProject.classList.remove('active');
            clearProjectForm();
            loadProjects();
        } else {
            // Create
            const project = await api.post('/projects/', {
                name, start_date, duration_months, tax_rate, margin_rate, allocations: []
            });
            currentProjectId = project.id;
            document.getElementById('proj-title-display').textContent = `Projeto: ${project.name}`;
            document.getElementById('proj-details').style.display = 'block';

            modalProject.classList.remove('active');
            clearProjectForm();
            loadOffersSelect();
            loadProjects();
        }
    };

    function clearProjectForm() {
        document.getElementById('proj-name').value = '';
        document.getElementById('proj-start').value = '';
        document.getElementById('proj-duration').value = '3';
        document.getElementById('proj-tax').value = '11';
        document.getElementById('proj-margin').value = '40';
    }

    // Apply Offer
    document.getElementById('btn-apply-off').onclick = async () => {
        const offId = document.getElementById('sel-offer').value;
        if (currentProjectId && offId) {
            const res = await api.post(`/projects/${currentProjectId}/apply_offer/${offId}`, {});
            alert(`Oferta aplicada! Adicionados ${res.allocations.length} profissionais em ${res.weeks_count} semanas.`);
            loadAllocationTable(currentProjectId);
        }
    };

    // Save & Calculate
    document.getElementById('btn-save-calc').onclick = async () => {
        if (!allocationTableData) return;

        const updates = [];

        // Collect allocation-level selling rate updates
        const sellingInputs = document.querySelectorAll('.alloc-input-selling');
        sellingInputs.forEach(input => {
            const allocationId = parseInt(input.dataset.allocationId);
            const sellingRate = parseFloat(input.value) || 0;

            updates.push({
                allocation_id: allocationId,
                selling_hourly_rate: sellingRate
            });
        });

        // Collect weekly hours updates
        const hoursInputs = document.querySelectorAll('.alloc-input-hours');
        hoursInputs.forEach(input => {
            const weeklyAllocId = parseInt(input.dataset.weeklyAllocId);
            const hours = parseFloat(input.value) || 0;

            updates.push({
                weekly_allocation_id: weeklyAllocId,
                hours_allocated: hours
            });
        });

        try {
            // 1. Save Allocations
            const result = await api.put(`/projects/${currentProjectId}/allocations`, updates);

            // 2. Calculate Price
            const res = await api.get(`/projects/${currentProjectId}/calculate_price`);
            document.getElementById('res-cost').textContent = formatCurrency(res.total_cost);
            document.getElementById('res-selling').textContent = formatCurrency(res.total_selling);
            document.getElementById('res-margin').textContent = formatCurrency(res.total_margin);
            document.getElementById('res-tax').textContent = formatCurrency(res.total_tax);
            document.getElementById('res-price').textContent = formatCurrency(res.final_price);
            document.getElementById('res-final-margin').textContent = res.final_margin_percent.toFixed(2) + '%';
            document.getElementById('price-result').style.display = 'block';

            alert(`Salvos ${result.updated_count} itens e preço calculado!`);

        } catch (error) {
            alert('Erro ao salvar/calcular: ' + error.message);
        }
    };

    // Export to Excel
    document.getElementById('btn-export-excel').onclick = async () => {
        if (!currentProjectId) {
            alert('Nenhum projeto selecionado.');
            return;
        }

        try {
            const project = await api.get(`/projects/${currentProjectId}`);
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            const filename = `projeto_${project.name.replace(/\s+/g, '_')}_${timestamp}.xlsx`;

            await api.downloadBlob(`/projects/${currentProjectId}/export_excel`, filename);
            alert('Excel exportado com sucesso!');
        } catch (error) {
            alert('Erro ao exportar: ' + error.message);
        }
    };

    // Add Professional Modal Logic
    const modalAddProf = document.getElementById('modal-add-prof');

    document.getElementById('btn-add-professional').onclick = async () => {
        await loadProfessionalsForSelect();
        modalAddProf.style.display = 'flex';
    };

    document.getElementById('btn-cancel-add-prof').onclick = () => {
        modalAddProf.style.display = 'none';
        document.getElementById('input-add-prof-rate').value = '';
    };

    document.getElementById('btn-confirm-add-prof').onclick = async () => {
        const profId = document.getElementById('sel-add-prof').value;
        const rateInput = document.getElementById('input-add-prof-rate').value;
        const sellingRate = rateInput ? parseFloat(rateInput) : null;

        if (!profId) {
            alert('Por favor, selecione um profissional.');
            return;
        }

        try {
            let url = `/projects/${currentProjectId}/allocations/?professional_id=${profId}`;
            if (sellingRate !== null) {
                url += `&selling_hourly_rate=${sellingRate}`;
            }

            await api.post(url, {});

            modalAddProf.style.display = 'none';
            document.getElementById('input-add-prof-rate').value = '';
            alert('Profissional adicionado com sucesso!');
            loadAllocationTable(currentProjectId);
        } catch (error) {
            alert('Erro ao adicionar profissional: ' + error.message);
        }
    };

    async function loadProfessionalsForSelect() {
        const profs = await api.get('/professionals/');
        const sel = document.getElementById('sel-add-prof');

        sel.innerHTML = '<option value="">-- Selecionar --</option>' + profs.map(p => `<option value="${p.id}" data-cost="${p.hourly_cost}">${escapeHtml(p.name)} (${escapeHtml(p.role)} ${escapeHtml(p.level)})</option>`).join('');

        // Update cost display on change
        sel.onchange = () => {
            const selectedOption = sel.options[sel.selectedIndex];
            const cost = selectedOption.getAttribute('data-cost');
            const disp = document.getElementById('disp-prof-cost');
            if (cost) {
                disp.textContent = `Custo: ${formatCurrency(parseFloat(cost))}/h`;
            } else {
                disp.textContent = '';
            }
        };
    }

    // Remove Professional Logic
    window.removeProfessionalFromAllocation = async (allocationId, name) => {
        if (confirm(`Tem certeza que deseja remover ${name} deste projeto?`)) {
            try {
                await api.delete(`/projects/${currentProjectId}/allocations/${allocationId}`);
                alert('Profissional removido.');
                loadAllocationTable(currentProjectId);
            } catch (error) {
                alert('Erro ao remover profissional: ' + error.message);
            }
        }
    };

    async function loadOffersSelect() {
        const list = await api.get('/offers/');
        const sel = document.getElementById('sel-offer');
        sel.innerHTML = '<option value="">Selecione uma oferta</option>' +
            list.map(i => `<option value="${i.id}">${escapeHtml(i.name)}</option>`).join('');
    }

    async function loadAllocationTable(projectId) {
        try {
            const data = await api.get(`/projects/${projectId}/allocation_table`);
            allocationTableData = data;
            renderAllocationTable(data);
            document.getElementById('btn-save-calc').style.display = 'inline-block';
            document.getElementById('btn-export-excel').style.display = 'inline-block';
        } catch (error) {
            console.error('Erro ao carregar tabela de alocação:', error);
        }
    }

    function renderAllocationTable(data) {
        const container = document.getElementById('allocation-table-container');

        if (!data.allocations || data.allocations.length === 0) {
            container.innerHTML = '<p style="color: #6b7280;">Nenhuma alocação ainda.</p>';
            return;
        }

        // Build table
        let html = '<table class="allocation-table" style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">';

        // Header
        html += '<thead><tr style="background: #f9fafb;">';
        html += '<th style="padding: 0.5rem; text-align: left; border: 1px solid #e5e7eb; position: sticky; left: 0; background: #f9fafb; z-index: 10;">Profissional</th>';
        html += '<th style="padding: 0.5rem; text-align: left; border: 1px solid #e5e7eb;">Função/Nível</th>';
        html += '<th style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb; min-width: 100px;">Custo (R$/h)</th>';
        html += '<th style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb; background: #fef3c7; min-width: 100px;">Taxa de Venda (R$/h)</th>';
        html += '<th style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb; background: #dcfce7; min-width: 100px;">Margem (%)</th>';

        data.weeks.forEach(week => {
            const weekStart = new Date(week.week_start).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' });
            const weekEnd = new Date(week.week_end).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' });
            const hasHoliday = week.holidays && week.holidays.length > 0;
            const bgColor = hasHoliday ? '#fef3c7' : '';
            html += `<th style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb; background: ${bgColor}; min-width: 80px;">
                S${week.week_number}<br><small>${weekStart}-${weekEnd}</small><br><small>${week.available_hours}h</small>
            </th>`;
        });

        html += '<th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Total de Horas</th>';
        html += '<th style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb;">Ações</th>';
        html += '</tr></thead>';

        // Body - one row per professional
        html += '<tbody>';
        data.allocations.forEach(alloc => {
            html += '<tr>';
            html += `<td style="padding: 0.5rem; border: 1px solid #e5e7eb; position: sticky; left: 0; background: white; z-index: 5;">${escapeHtml(alloc.professional.name)}</td>`;
            html += `<td style="padding: 0.5rem; border: 1px solid #e5e7eb;">${escapeHtml(alloc.professional.role)} ${escapeHtml(alloc.professional.level)}</td>`;
            html += `<td style="padding: 0.5rem; border: 1px solid #e5e7eb; text-align: center;">${formatCurrency(alloc.professional.hourly_cost)}</td>`;

            // Selling Rate column (fixed per professional)
            html += `<td style="padding: 0.25rem; border: 1px solid #e5e7eb; text-align: center; background: #fef3c7;">
                <input type="number" 
                    class="alloc-input-selling" 
                    data-allocation-id="${alloc.allocation_id}"
                    data-cost="${alloc.professional.hourly_cost}"
                    value="${alloc.selling_hourly_rate.toFixed(2)}" 
                    min="0"
                    step="1"
                    style="width: 100%; padding: 0.25rem; text-align: center; border: 1px solid #d1d5db; border-radius: 0.25rem;">
            </td>`;

            // Margin column (calculated from cost and selling rate)
            const marginPercent = alloc.selling_hourly_rate > 0
                ? ((alloc.selling_hourly_rate - alloc.professional.hourly_cost) / alloc.selling_hourly_rate * 100).toFixed(2)
                : '0.00';
            html += `<td class="margin-cell" style="padding: 0.5rem; border: 1px solid #e5e7eb; text-align: center; background: #dcfce7; font-weight: 600;">${marginPercent}%</td>`;

            let totalHours = 0;
            data.weeks.forEach(week => {
                const weekData = alloc.weekly_hours[week.week_number];
                if (weekData) {
                    totalHours += weekData.hours_allocated;
                    html += `<td style="padding: 0.25rem; border: 1px solid #e5e7eb; text-align: center;">
                        <input type="number" 
                            class="alloc-input-hours" 
                            data-weekly-alloc-id="${weekData.id}"
                            value="${weekData.hours_allocated}" 
                            max="${weekData.available_hours}"
                            min="0"
                            step="0.5"
                            style="width: 100%; padding: 0.25rem; text-align: center; border: 1px solid #d1d5db; border-radius: 0.25rem;">
                    </td>`;
                } else {
                    html += '<td style="padding: 0.5rem; border: 1px solid #e5e7eb;"></td>';
                }
            });

            html += `<td class="total-hours-cell" style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb; font-weight: 600;">${Math.round(totalHours)}h</td>`;
            html += `<td style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb;">
                <button class="btn btn-sm btn-danger" data-allocation-id="${alloc.allocation_id}" data-professional-name="${escapeHtml(alloc.professional.name)}">🗑️</button>
            </td>`;
            html += '</tr>';
        });
        html += '</tbody></table>';

        container.innerHTML = html;

        // Add event delegation for delete buttons
        container.querySelectorAll('button[data-allocation-id]').forEach(btn => {
            btn.addEventListener('click', () => {
                const allocationId = btn.dataset.allocationId;
                const professionalName = btn.dataset.professionalName;
                window.removeProfessionalFromAllocation(allocationId, professionalName);
            });
        });

        // Add event listeners for dynamic total calculation
        const rows = container.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const inputs = row.querySelectorAll('.alloc-input-hours');
            const totalCell = row.querySelector('.total-hours-cell');

            if (inputs.length > 0 && totalCell) {
                const updateRowTotal = () => {
                    let sum = 0;
                    inputs.forEach(input => {
                        sum += parseFloat(input.value) || 0;
                    });
                    totalCell.textContent = `${Math.round(sum)}h`;
                };

                inputs.forEach(input => {
                    input.addEventListener('input', updateRowTotal);
                });
            }

            // Add event listener for selling rate to update margin
            const sellingInput = row.querySelector('.alloc-input-selling');
            const marginCell = row.querySelector('.margin-cell');

            if (sellingInput && marginCell) {
                sellingInput.addEventListener('input', () => {
                    const sellingRate = parseFloat(sellingInput.value) || 0;
                    const cost = parseFloat(sellingInput.dataset.cost) || 0;
                    const marginPercent = sellingRate > 0
                        ? ((sellingRate - cost) / sellingRate * 100).toFixed(2)
                        : '0.00';
                    marginCell.textContent = `${marginPercent}%`;
                });
            }
        });
    }

    function sortProjects(projects, sortBy, direction) {
        const sorted = [...projects].sort((a, b) => {
            let aVal, bVal;

            if (sortBy === 'name') {
                aVal = a.name.toLowerCase();
                bVal = b.name.toLowerCase();
                return direction === 'asc'
                    ? aVal.localeCompare(bVal)
                    : bVal.localeCompare(aVal);
            } else if (sortBy === 'start_date') {
                aVal = new Date(a.start_date);
                bVal = new Date(b.start_date);
            } else if (sortBy === 'created_at') {
                // If created_at exists, use it; otherwise fall back to id (older id = created earlier)
                aVal = a.created_at ? new Date(a.created_at) : a.id;
                bVal = b.created_at ? new Date(b.created_at) : b.id;
            }

            if (direction === 'asc') {
                return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
            } else {
                return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
            }
        });

        return sorted;
    }

    async function loadProjects() {
        const projects = await api.get('/projects/');
        const listDiv = document.getElementById('projects-list');

        if (projects.length === 0) {
            listDiv.innerHTML = '<p style="color: #6b7280;">Nenhum projeto criado ainda</p>';
            return;
        }

        // Sort projects
        const sortedProjects = sortProjects(projects, currentSortBy, currentSortDirection);

        listDiv.innerHTML = sortedProjects.map(p => `
            <div style="border: 1px solid #e5e7eb; border-radius: 0.375rem; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4 style="margin: 0 0 0.25rem 0;">${escapeHtml(p.name)}</h4>
                        <small style="color: #6b7280;">
                            Início: ${escapeHtml(p.start_date)} | Duração: ${p.duration_months} meses<br>
                            Impostos: ${p.tax_rate}% | Margem: ${p.margin_rate}%
                        </small>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-sm" data-action="view" data-project-id="${p.id}">Visualizar</button>
                        <button class="btn btn-sm" data-action="edit" data-project-id="${p.id}">Editar</button>
                        <button class="btn btn-sm btn-danger" data-action="delete" data-project-id="${p.id}" data-project-name="${escapeHtml(p.name)}">Excluir</button>
                    </div>
                </div>
            </div>
        `).join('');

        // Add event delegation for project action buttons
        listDiv.querySelectorAll('button[data-action]').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                const projectId = parseInt(btn.dataset.projectId);

                if (action === 'view') {
                    window.viewProject(projectId);
                } else if (action === 'edit') {
                    window.editProject(projectId);
                } else if (action === 'delete') {
                    const projectName = btn.dataset.projectName;
                    window.deleteProject(projectId, projectName);
                }
            });
        });
    }

    // View project details
    window.viewProject = async (id) => {
        const project = await api.get(`/projects/${id}`);
        currentProjectId = id;
        document.getElementById('proj-title-display').textContent = `Projeto: ${project.name}`;
        document.getElementById('proj-details').style.display = 'block';
        loadOffersSelect();
        loadAllocationTable(id);
    };

    // Edit project
    window.editProject = async (id) => {
        const project = await api.get(`/projects/${id}`);

        editingProjectId = id;
        document.getElementById('modal-project-title').textContent = 'Editar Projeto';
        document.getElementById('btn-save-project').textContent = 'Atualizar Projeto';

        document.getElementById('proj-name').value = project.name;
        document.getElementById('proj-start').value = project.start_date;
        document.getElementById('proj-duration').value = project.duration_months;
        document.getElementById('proj-tax').value = project.tax_rate;
        document.getElementById('proj-margin').value = project.margin_rate;

        modalProject.classList.add('active');
    };

    // Delete project
    window.deleteProject = async (id, name) => {
        if (confirm(`Tem certeza que deseja excluir o projeto "${name}"?`)) {
            await api.delete(`/projects/${id}`);
            if (currentProjectId === id) {
                currentProjectId = null;
                document.getElementById('proj-details').style.display = 'none';
            }
            loadProjects();
        }
    };
}
