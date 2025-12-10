import { api } from '../api.js';
import { normalizeText, formatCurrency } from '../utils.js';
import { escapeHtml } from '../sanitize.js';



export async function renderProjects(container) {
    let currentProjectId = null;
    let currentProjectData = null;
    let editingProjectId = null;
    let allocationTableData = null;
    let currentSortBy = 'name';
    let currentSortDirection = 'asc';
    let allocationSortColumn = 'professional_name';
    let allocationSortDirection = 'asc';
    let currentPage = 1;

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
        <div id="projects-list">
            <div style="padding: 2rem; text-align: center; color: #6b7280;">Carregando projetos...</div>
        </div>
        <div id="pagination-controls" style="display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1rem; padding: 1rem;">
            <button id="btn-prev-page" class="btn btn-sm" disabled>Anterior</button>
            <span id="page-indicator" style="color: var(--md-sys-color-on-surface); font-size: 0.875rem;">Página 1 de 1</span>
            <button id="btn-next-page" class="btn btn-sm" disabled>Próxima</button>
        </div>
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
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
            <div style="display: flex; gap: 0.5rem;">
                <button id="btn-save-calc" class="btn btn-primary" style="display:none;">Salvar & Calcular</button>
                <button id="btn-export-excel" class="btn" style="display:none;">
                    <span class="material-icons" style="margin-right: 0.5rem; font-size: 1.125rem;">file_download</span>
                    Excel
                </button>
                <button id="btn-export-png" class="btn" style="display:none;">
                    <span class="material-icons" style="margin-right: 0.5rem; font-size: 1.125rem;">image</span>
                    PNG (cliente)
                </button>
            </div>
            <div id="project-total-hours" style="font-weight: 600; font-size: 1.1rem; color: var(--md-sys-color-on-surface); display: none;">
                Total de horas: <span id="val-project-total-hours">0</span>h
            </div>
        </div>
        
        <div id="price-result" style="display:none; margin-top: 1.5rem;">
            <h4 style="margin-bottom: 1rem; color: var(--md-sys-color-on-surface);">Resultado da Precificação</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <!-- Left Details -->
                <div style="background: var(--md-sys-color-surface-container-low); padding: 1.5rem; border-radius: var(--md-sys-shape-corner-large); box-shadow: var(--md-sys-elevation-1);">
                    <h5 style="margin: 0 0 1rem 0; font-size: 0.875rem; font-weight: 500; color: var(--md-sys-color-on-surface-variant); text-transform: uppercase; letter-spacing: 0.1px;">Detalhes</h5>
                    
                    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.75rem; border-bottom: 1px solid var(--md-sys-color-outline-variant, #C4C7C5);">
                            <span style="color: var(--md-sys-color-on-surface-variant); font-size: 0.875rem;">Custo (+)</span>
                            <span id="res-cost" style="font-weight: 500; color: var(--md-sys-color-on-surface); font-size: 1rem;"></span>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.75rem; border-bottom: 1px solid var(--md-sys-color-outline-variant, #C4C7C5);">
                            <span id="label-margin-total" style="color: var(--md-sys-color-on-surface-variant); font-size: 0.875rem;">Margem (+)</span>
                            <span id="res-margin" style="font-weight: 500; color: var(--md-sys-color-on-surface); font-size: 1rem;"></span>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.75rem; border-bottom: 1px solid var(--md-sys-color-outline-variant, #C4C7C5);">
                            <span style="color: var(--md-sys-color-on-surface-variant); font-size: 0.875rem;">Venda (=)</span>
                            <span id="res-selling" style="font-weight: 500; color: var(--md-sys-color-on-surface); font-size: 1rem;"></span>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span id="label-tax-total" style="color: var(--md-sys-color-on-surface-variant); font-size: 0.875rem;">Impostos (+)</span>
                            <span id="res-tax" style="font-weight: 500; color: var(--md-sys-color-on-surface); font-size: 1rem;"></span>
                        </div>
                    </div>
                </div>
                
                <!-- Right Highlights -->
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    <!-- Final Price -->
                    <div style="background: linear-gradient(135deg, var(--md-sys-color-primary-container) 0%, var(--md-sys-color-primary-container) 100%); padding: 1.5rem; border-radius: var(--md-sys-shape-corner-large); box-shadow: var(--md-sys-elevation-2); border: 1px solid var(--md-sys-color-primary);">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span class="material-icons" style="color: var(--md-sys-color-primary); font-size: 1.25rem;">payments</span>
                            <span style="font-size: 0.75rem; font-weight: 500; color: var(--md-sys-color-on-primary-container); text-transform: uppercase; letter-spacing: 0.5px;">Preço Final (=)</span>
                        </div>
                        <div id="res-price" style="font-size: 2rem; font-weight: 700; color: var(--md-sys-color-primary); line-height: 1.2;"></div>
                    </div>
                    
                    <!-- Final Margin -->
                    <div style="background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%); padding: 1.5rem; border-radius: var(--md-sys-shape-corner-large); box-shadow: var(--md-sys-elevation-2); border: 1px solid #10B981;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span class="material-icons" style="color: #059669; font-size: 1.25rem;">trending_up</span>
                            <span style="font-size: 0.75rem; font-weight: 500; color: #065F46; text-transform: uppercase; letter-spacing: 0.5px;">Margem Final (sem impostos)</span>
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
                <select id="sel-add-prof" style="width: 100%; padding: 0.5rem;">
                    <option>Carregando...</option>
                </select>
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

    await loadProjects();

    // --- Event Listeners ---

    document.getElementById('sort-select').addEventListener('change', (e) => {
        currentSortBy = e.target.value;
        currentPage = 1; // Resetar para primeira página ao mudar ordenação
        loadProjects();
    });

    document.getElementById('sort-direction-btn').addEventListener('click', () => {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
        const icon = document.getElementById('sort-icon');
        icon.textContent = currentSortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward';
        currentPage = 1; // Resetar para primeira página ao mudar ordenação
        loadProjects();
    });

    // Event listeners para paginação
    document.getElementById('btn-prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadProjects();
        }
    });

    document.getElementById('btn-next-page').addEventListener('click', () => {
        currentPage++;
        loadProjects();
    });

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

    modalProject.onclick = (e) => {
        if (e.target === modalProject) {
            modalProject.classList.remove('active');
            clearProjectForm();
        }
    };

    document.getElementById('btn-save-project').onclick = async () => {
        const name = normalizeText(document.getElementById('proj-name').value);
        const start_date = document.getElementById('proj-start').value;
        const duration_months = parseInt(document.getElementById('proj-duration').value);
        const tax_rate = parseFloat(document.getElementById('proj-tax').value);
        const margin_rate = parseFloat(document.getElementById('proj-margin').value);

        if (!name || !start_date) {
            alert('Por favor, preencha todos os campos obrigatórios (Nome e Data de Início).');
            return;
        }

        const btn = document.getElementById('btn-save-project');
        setLoading(btn, true, 'Salvando...');

        try {
            if (editingProjectId) {
                await api.patch(`/projects/${editingProjectId}`, {
                    id: parseInt(editingProjectId),
                    name, start_date, duration_months, tax_rate, margin_rate
                });

                if (currentProjectId === editingProjectId) {
                    // Check if duration or start_date changed (these affect weekly allocations)
                    const durationChanged = currentProjectData && 
                        currentProjectData.duration_months !== duration_months;
                    const startDateChanged = currentProjectData && 
                        currentProjectData.start_date !== start_date;
                    
                    // Update local state to reflect changes immediately
                    currentProjectData = {
                        ...currentProjectData,
                        name,
                        start_date,
                        duration_months,
                        tax_rate,
                        margin_rate
                    };
                    document.getElementById('proj-title-display').textContent = `Projeto: ${name}`;
                    // Reload allocation table (always reload to ensure consistency)
                    loadAllocationTable(currentProjectId);
                }

                editingProjectId = null;
                modalProject.classList.remove('active');
                clearProjectForm();
                loadProjects();
            } else {
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
        } catch (error) {
            alert('Erro ao salvar projeto:\n\n' + getApiErrorMessage(error));
        } finally {
            setLoading(btn, false);
        }
    };

    function clearProjectForm() {
        document.getElementById('proj-name').value = '';
        document.getElementById('proj-start').value = '';
        document.getElementById('proj-duration').value = '3';
        document.getElementById('proj-tax').value = '11';
        document.getElementById('proj-margin').value = '40';
    }

    document.getElementById('btn-apply-off').onclick = async () => {
        const offId = document.getElementById('sel-offer').value;
        if (!currentProjectId || !offId) return;

        const btn = document.getElementById('btn-apply-off');
        setLoading(btn, true, 'Aplicando...');

        try {
            await api.post(`/projects/${currentProjectId}/offers`, {
                offer_id: parseInt(offId)
            });

            btn.innerHTML = '<span class="material-icons" style="font-size: 1.25rem;">check</span> Aplicado!';
            btn.classList.add('btn-success');

            setTimeout(() => {
                setLoading(btn, false);
                btn.classList.remove('btn-success');
            }, 2000);

            // Allocations changed; reload from API
            loadAllocationTable(currentProjectId);
        } catch (error) {
            alert('Erro ao aplicar oferta:\n\n' + getApiErrorMessage(error));
            setLoading(btn, false);
        }
    };

    // Save & Calculate
    document.getElementById('btn-save-calc').onclick = async () => {
        if (!currentProjectId) {
            alert('Nenhum projeto selecionado.');
            return;
        }
        if (!allocationTableData) return;

        const btn = document.getElementById('btn-save-calc');
        setLoading(btn, true, 'Calculando...');

        const updates = [];

        const sellingInputs = document.querySelectorAll('.alloc-input-selling');
        sellingInputs.forEach(input => {
            const allocationId = parseInt(input.dataset.allocationId);
            const sellingRate = parseFloat(input.value) || 0;

            updates.push({
                allocation_id: allocationId,
                selling_hourly_rate: sellingRate
            });
        });

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
            // Atualização parcial de alocações usa PATCH no backend
            await api.patch(`/projects/${currentProjectId}/allocations`, updates);
            const res = await api.get(`/projects/${currentProjectId}/pricing`);

            document.getElementById('res-cost').textContent = formatCurrency(res.total_cost);
            document.getElementById('res-selling').textContent = formatCurrency(res.total_selling);
            document.getElementById('res-margin').textContent = formatCurrency(res.total_margin);
            document.getElementById('res-tax').textContent = formatCurrency(res.total_tax);
            document.getElementById('res-price').textContent = formatCurrency(res.final_price);
            document.getElementById('res-final-margin').textContent = res.final_margin_percent.toFixed(2) + '%';

            const marginCard = document.getElementById('res-final-margin').parentElement;
            const finalMargin = res.final_margin_percent.toFixed(2);

            // Default to 0 if not available
            const configuredMargin = (currentProjectData && currentProjectData.margin_rate !== undefined)
                ? currentProjectData.margin_rate.toFixed(2)
                : '0.00';

            if (parseFloat(finalMargin) >= parseFloat(configuredMargin)) {
                marginCard.style.background = 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)';
                marginCard.style.borderColor = '#10B981';
                document.getElementById('res-final-margin').style.color = '#059669';
                marginCard.querySelector('.material-icons').style.color = '#059669';
                marginCard.querySelector('span:not(.material-icons)').style.color = '#065F46';
            } else {
                marginCard.style.background = 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)';
                marginCard.style.borderColor = '#EF4444';
                document.getElementById('res-final-margin').style.color = '#DC2626';
                marginCard.querySelector('.material-icons').style.color = '#DC2626';
                marginCard.querySelector('span:not(.material-icons)').style.color = '#991B1B';
            }

            document.getElementById('price-result').style.display = 'block';

            // Success feedback
            btn.innerHTML = '<span class="material-icons" style="font-size: 1.25rem;">check</span> Salvo!';
            btn.classList.add('btn-success');

            setTimeout(() => {
                setLoading(btn, false);
                btn.classList.remove('btn-success');
            }, 2000);

        } catch (error) {
            alert('Erro ao salvar/calcular:\n\n' + getApiErrorMessage(error));
            setLoading(btn, false);
        }
    };

    document.getElementById('btn-export-excel').onclick = async () => {
        if (!currentProjectId) {
            alert('Nenhum projeto selecionado.');
            return;
        }

        const btn = document.getElementById('btn-export-excel');
        setLoading(btn, true, 'Exportando...');

        try {
            await api.downloadBlob(`/projects/${currentProjectId}/export?format=xlsx`);

            btn.innerHTML = '<span class="material-icons" style="font-size: 1.25rem;">check</span> Exportado!';
            btn.classList.add('btn-success');

            setTimeout(() => {
                setLoading(btn, false);
                btn.classList.remove('btn-success');
            }, 2000);

        } catch (error) {
            alert('Erro ao exportar:\n\n' + getApiErrorMessage(error));
            setLoading(btn, false);
        }
    };

    document.getElementById('btn-export-png').onclick = async () => {
        if (!currentProjectId) {
            alert('Nenhum projeto selecionado.');
            return;
        }

        const btn = document.getElementById('btn-export-png');
        setLoading(btn, true, 'Exportando...');

        try {
            await api.downloadBlob(`/projects/${currentProjectId}/export?format=png`);

            btn.innerHTML = '<span class="material-icons" style="font-size: 1.25rem;">check</span> Exportado!';
            btn.classList.add('btn-success');

            setTimeout(() => {
                setLoading(btn, false);
                btn.classList.remove('btn-success');
            }, 2000);

        } catch (error) {
            alert('Erro ao exportar PNG:\n\n' + getApiErrorMessage(error));
            setLoading(btn, false);
        }
    };

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

        const btn = document.getElementById('btn-confirm-add-prof');
        setLoading(btn, true, 'Adicionando...');

        try {
            let url = `/projects/${currentProjectId}/allocations/?professional_id=${profId}`;
            if (sellingRate !== null) {
                url += `&selling_hourly_rate=${sellingRate}`;
            }

            const response = await api.post(url, {});
            const allocationId = response.allocation_id;

            btn.innerHTML = '<span class="material-icons" style="font-size: 1.25rem;">check</span> Adicionado!';
            btn.classList.add('btn-success');

            setTimeout(() => {
                modalAddProf.style.display = 'none';
                document.getElementById('input-add-prof-rate').value = '';
                // Reload allocations from API since we just added a new professional
                loadAllocationTable(currentProjectId, allocationId);
                setLoading(btn, false);
                btn.classList.remove('btn-success');
            }, 1500);

        } catch (error) {
            alert('Erro ao adicionar profissional:\n\n' + getApiErrorMessage(error));
            setLoading(btn, false);
        }
    };

    async function loadProfessionalsForSelect() {
        const sel = document.getElementById('sel-add-prof');
        sel.innerHTML = '<option value="">Carregando...</option>';

        try {
            const profs = await api.get('/professionals/');
            const profsList = profs.items;

            sel.innerHTML = '<option value="">-- Selecionar --</option>' + profsList.map(p => `<option value="${p.id}" data-cost="${p.hourly_cost}">${escapeHtml(p.name)} (${escapeHtml(p.role)} ${escapeHtml(p.level)})</option>`).join('');

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
        } catch (e) {
            sel.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }


    async function removeProfessional(allocationId, name) {
        if (confirm(`Tem certeza que deseja remover ${name} deste projeto?`)) {
            try {
                await api.delete(`/projects/${currentProjectId}/allocations/${allocationId}`);
                // Allocations changed; reload from API
                loadAllocationTable(currentProjectId);
            } catch (error) {
                alert('Erro ao remover profissional:\n\n' + getApiErrorMessage(error));
            }
        }
    }

    async function loadOffersSelect() {
        try {
            const list = await api.get('/offers/');
            const sel = document.getElementById('sel-offer');
            sel.innerHTML = '<option value="">Selecione uma oferta</option>' +
                list.map(i => `<option value="${i.id}">${escapeHtml(i.name)}</option>`).join('');
        } catch (e) {
            console.error("Erro ao carregar ofertas para select", e);
        }
    }

    async function loadAllocationTable(projectId, highlightAllocationId = null) {
        try {
            // Always fetch fresh data from API to ensure consistency
            const [weeks, pData] = await Promise.all([
                api.get(`/projects/${projectId}/timeline`),
                api.get(`/projects/${projectId}`)
            ]);
            const allocations = pData.allocations;
            
            // Update currentProjectData to keep it in sync
            if (currentProjectId === projectId) {
                currentProjectData = pData;
            }

            allocationTableData = { weeks, allocations };
            renderAllocationTable(weeks, allocations, highlightAllocationId);

            document.getElementById('btn-save-calc').style.display = 'inline-block';
            document.getElementById('btn-export-excel').style.display = 'inline-block';
            document.getElementById('btn-export-png').style.display = 'inline-block';
        } catch (error) {
            console.error('Erro ao carregar tabela de alocação:', error);
            document.getElementById('allocation-table-container').innerHTML =
                '<p style="color: red;">Erro ao carregar timeline. Tente novamente.</p>';
        }
    }

    function applyMarginColor(marginCell, marginPercent, configuredMargin) {
        const margin = parseFloat(marginPercent);
        const target = parseFloat(configuredMargin);

        if (margin >= target) {
            marginCell.style.background = '#dcfce7';
            marginCell.style.color = '#059669';
        } else {
            marginCell.style.background = '#fee2e2';
            marginCell.style.color = '#dc2626';
        }
    }

    function calculateSellingRateFromMargin(cost, marginRate) {
        // Fórmula: selling_rate = cost / (1 - margin_rate/100)
        const marginDecimal = marginRate > 1 ? marginRate / 100.0 : marginRate;
        const divisor = 1 - marginDecimal;
        if (divisor <= 0) {
            return cost;
        }
        return cost / divisor;
    }

    function updateAllocationHeaderStyles() {
        const container = document.getElementById('allocation-table-container');
        if (!container) return;
        
        container.querySelectorAll('th.sortable').forEach((th) => {
            th.classList.remove('sorted-asc', 'sorted-desc');
            if (th.dataset.column === allocationSortColumn) {
                th.classList.add(
                    allocationSortDirection === 'asc' ? 'sorted-asc' : 'sorted-desc'
                );
            }
        });
    }

    function sortAllocationData(allocations) {
        return [...allocations].sort((a, b) => {
            let valA, valB;

            switch (allocationSortColumn) {
                case 'professional_name':
                    valA = a.professional.name.toLowerCase();
                    valB = b.professional.name.toLowerCase();
                    break;
                case 'role_level':
                    valA = `${a.professional.role} ${a.professional.level}`.toLowerCase();
                    valB = `${b.professional.role} ${b.professional.level}`.toLowerCase();
                    break;
                case 'cost_hourly_rate':
                    valA = a.cost_hourly_rate;
                    valB = b.cost_hourly_rate;
                    break;
                case 'selling_hourly_rate':
                    valA = a.selling_hourly_rate;
                    valB = b.selling_hourly_rate;
                    break;
                case 'margin_percent':
                    valA = a.selling_hourly_rate > 0
                        ? ((a.selling_hourly_rate - a.cost_hourly_rate) / a.selling_hourly_rate * 100)
                        : 0;
                    valB = b.selling_hourly_rate > 0
                        ? ((b.selling_hourly_rate - b.cost_hourly_rate) / b.selling_hourly_rate * 100)
                        : 0;
                    break;
                default:
                    return 0;
            }

            if (valA === null || valA === undefined) valA = '';
            if (valB === null || valB === undefined) valB = '';

            if (typeof valA === 'string') valA = valA.toLowerCase();
            if (typeof valB === 'string') valB = valB.toLowerCase();

            if (valA < valB) return allocationSortDirection === 'asc' ? -1 : 1;
            if (valA > valB) return allocationSortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }

    function renderAllocationTable(weeks, allocations, highlightAllocationId = null) {
        const container = document.getElementById('allocation-table-container');

        if (!allocations || allocations.length === 0) {
            container.innerHTML = '<p style="color: #6b7280;">Nenhuma alocação ainda.</p>';
            return;
        }

        // Ordenar dados antes de renderizar
        const sortedAllocations = sortAllocationData(allocations);

        let html = '<table class="allocation-table" style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">';

        html += '<thead><tr style="background: #f9fafb;">';
        html += '<th class="sortable" data-column="professional_name" style="padding: 0.5rem; text-align: left; border: 1px solid #e5e7eb; position: sticky; left: 0; background: #f9fafb; z-index: 10; white-space: nowrap;">Profissional <span class="material-icons sort-icon">arrow_upward</span></th>';
        html += '<th class="sortable" data-column="role_level" style="padding: 0.5rem; text-align: left; border: 1px solid #e5e7eb; white-space: nowrap;">Função/Nível <span class="material-icons sort-icon">arrow_upward</span></th>';
        html += '<th class="sortable" data-column="cost_hourly_rate" style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb; min-width: 100px; white-space: nowrap;">Custo (R$/h) <span class="material-icons sort-icon">arrow_upward</span></th>';
        html += '<th class="sortable" data-column="selling_hourly_rate" style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb; background: #fef3c7; min-width: 100px; white-space: nowrap;">Taxa de Venda (R$/h) <span class="material-icons sort-icon">arrow_upward</span></th>';
        html += '<th class="sortable" data-column="margin_percent" style="padding: 0.5rem; text-align: center; border: 1px solid #e5e7eb; background: #dcfce7; min-width: 100px; white-space: nowrap;">Margem (%) <span class="material-icons sort-icon">arrow_upward</span></th>';

        weeks.forEach(week => {
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

        html += '<tbody>';
        sortedAllocations.forEach(alloc => {
            const weeklyHoursMap = {};
            if (alloc.weekly_allocations) {
                alloc.weekly_allocations.forEach(wa => {
                    weeklyHoursMap[wa.week_number] = wa;
                });
            }

            html += `<tr data-allocation-id="${alloc.id}">`;
            html += `<td style="padding: 0.5rem; border: 1px solid #e5e7eb; position: sticky; left: 0; background: white; z-index: 5;">${escapeHtml(alloc.professional.name)}</td>`;
            html += `<td style="padding: 0.5rem; border: 1px solid #e5e7eb;">${escapeHtml(alloc.professional.role)} ${escapeHtml(alloc.professional.level)}</td>`;
            html += `<td style="padding: 0.5rem; border: 1px solid #e5e7eb; text-align: center;">${formatCurrency(alloc.cost_hourly_rate)}</td>`;

            html += `<td style="padding: 0.25rem; border: 1px solid #e5e7eb; text-align: center; background: #fef3c7;">
                <input type="number" 
                    class="alloc-input-selling" 
                    data-allocation-id="${alloc.id}"
                    data-cost="${alloc.cost_hourly_rate}"
                    value="${alloc.selling_hourly_rate.toFixed(2)}" 
                    min="0"
                    step="1"
                    style="width: 100%; padding: 0.25rem; text-align: center; border: 1px solid #d1d5db; border-radius: 0.25rem;">
            </td>`;

            const marginPercent = alloc.selling_hourly_rate > 0
                ? ((alloc.selling_hourly_rate - alloc.cost_hourly_rate) / alloc.selling_hourly_rate * 100).toFixed(2)
                : '0.00';
            html += `<td class="margin-cell" data-margin="${marginPercent}" style="padding: 0.5rem; border: 1px solid #e5e7eb; text-align: center; font-weight: 600;">${marginPercent}%</td>`;

            let totalHours = 0;
            weeks.forEach(week => {
                const weekData = weeklyHoursMap[week.week_number];
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
                <div style="display: flex; gap: 0.25rem; justify-content: center;">
                    <button class="btn btn-sm" data-action="recalculate-rate" data-allocation-id="${alloc.id}" data-cost="${alloc.cost_hourly_rate}" title="Recalcular preço de venda">
                        <span class="material-icons" style="font-size: 1.1rem;">refresh</span>
                    </button>
                    <button class="btn btn-sm btn-danger" data-action="delete" data-allocation-id="${alloc.id}" data-professional-name="${escapeHtml(alloc.professional.name)}">🗑️</button>
                </div>
            </td>`;
            html += '</tr>';
        });
        html += '</tbody></table>';

        container.innerHTML = html;

        // Aplicar highlight na linha recém-adicionada, se especificado
        if (highlightAllocationId !== null) {
            const highlightedRow = container.querySelector(`tr[data-allocation-id="${highlightAllocationId}"]`);
            if (highlightedRow) {
                highlightedRow.classList.add('row-highlight');
                // Remover a classe após a animação completar (2.5s)
                setTimeout(() => {
                    highlightedRow.classList.remove('row-highlight');
                }, 1000);
            }
        }

        // Adicionar event listeners para ordenação nos headers
        container.querySelectorAll('th.sortable').forEach((th) => {
            th.addEventListener('click', () => {
                const column = th.dataset.column;
                if (allocationSortColumn === column) {
                    allocationSortDirection = allocationSortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    allocationSortColumn = column;
                    allocationSortDirection = 'asc';
                }
                renderAllocationTable(weeks, allocations);
            });
        });

        // Atualizar estilos dos headers
        updateAllocationHeaderStyles();

        const totalHoursContainer = document.getElementById('project-total-hours');
        if (totalHoursContainer) {
            totalHoursContainer.style.display = (allocations && allocations.length > 0) ? 'block' : 'none';
        }

        const updateProjectTotalHours = () => {
            const allHoursInputs = container.querySelectorAll('.alloc-input-hours');
            let total = 0;
            allHoursInputs.forEach(input => {
                total += parseFloat(input.value) || 0;
            });
            const display = document.getElementById('val-project-total-hours');
            if (display) {
                display.textContent = Math.round(total);
            }
        };

        updateProjectTotalHours();

        if (currentProjectData && currentProjectData.margin_rate !== undefined) {
            const rows = container.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const marginCell = row.querySelector('.margin-cell');
                if (marginCell) {
                    const marginPercent = marginCell.dataset.margin;
                    applyMarginColor(marginCell, marginPercent, currentProjectData.margin_rate);
                }
            });
        }

        // Event listeners para botões de ação
        container.querySelectorAll('button[data-action]').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                const allocationId = parseInt(btn.dataset.allocationId);
                
                if (action === 'delete') {
                    const professionalName = btn.dataset.professionalName;
                    removeProfessional(allocationId, professionalName);
                } else if (action === 'recalculate-rate') {
                    // Recalcular preço de venda baseado na margem do projeto
                    if (!currentProjectData || currentProjectData.margin_rate === undefined) {
                        alert('Margem do projeto não configurada.');
                        return;
                    }
                    
                    const cost = parseFloat(btn.dataset.cost);
                    const marginRate = currentProjectData.margin_rate;
                    const newSellingRate = calculateSellingRateFromMargin(cost, marginRate);
                    
                    // Encontrar o input de selling rate correspondente e atualizar
                    const row = btn.closest('tr');
                    const sellingInput = row.querySelector('.alloc-input-selling');
                    if (sellingInput) {
                        sellingInput.value = newSellingRate.toFixed(2);
                        // Disparar evento input para atualizar a margem calculada
                        sellingInput.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }
            });
        });

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
                    input.addEventListener('input', updateProjectTotalHours);
                });
            }

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
                    marginCell.dataset.margin = marginPercent;

                    if (currentProjectData && currentProjectData.margin_rate !== undefined) {
                        applyMarginColor(marginCell, marginPercent, currentProjectData.margin_rate);
                    }
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

    function updatePaginationControls(page, totalPages) {
        const prevBtn = document.getElementById('btn-prev-page');
        const nextBtn = document.getElementById('btn-next-page');
        const indicator = document.getElementById('page-indicator');
        
        if (!prevBtn || !nextBtn || !indicator) return;
        
        prevBtn.disabled = page <= 1;
        nextBtn.disabled = page >= totalPages || totalPages === 0;
        indicator.textContent = `Página ${page} de ${totalPages || 1}`;
    }

    async function loadProjects() {
        try {
            // Evita overfetch: lista não precisa de alocações embutidas
            const skip = (currentPage - 1) * 10;
            const response = await api.get(`/projects/?skip=${skip}&limit=10`);
            const projects = response.items;
            const total = response.total;
            const listDiv = document.getElementById('projects-list');

            if (projects.length === 0) {
                listDiv.innerHTML = '<p style="color: #6b7280;">Nenhum projeto criado ainda</p>';
                const totalPages = Math.ceil(total / 10);
                updatePaginationControls(currentPage, totalPages);
                return;
            }

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
                        <button class="btn btn-sm" data-action="clone" data-project-id="${p.id}" title="Clonar Projeto">
                            <span class="material-icons" style="font-size: 1.1rem;">content_copy</span>
                        </button>
                        <button class="btn btn-sm btn-danger" data-action="delete" data-project-id="${p.id}" data-project-name="${escapeHtml(p.name)}">Excluir</button>
                    </div>
                </div>
            </div>
        `).join('');

            // Event Delegation
            listDiv.querySelectorAll('button[data-action]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const action = btn.dataset.action;
                    const projectId = parseInt(btn.dataset.projectId);

                    if (action === 'view') {
                        handleViewProject(projectId, btn);
                    } else if (action === 'edit') {
                        handleEditProject(projectId, btn);
                    } else if (action === 'clone') {
                        handleCloneProject(projectId, btn);
                    } else if (action === 'delete') {
                        const projectName = btn.dataset.projectName;
                        handleDeleteProject(projectId, projectName, btn);
                    }
                });
            });
            
            // Atualizar controles de paginação
            const totalPages = Math.ceil(total / 10);
            updatePaginationControls(currentPage, totalPages);
        } catch (error) {
            document.getElementById('projects-list').innerHTML = '<p style="color:red">Erro ao carregar projetos.</p>';
            console.error(error);
        }
    };

    // --- Scoped Action Handlers (No Window Globals) ---

    async function handleViewProject(id, btnElement) {
        setLoading(btnElement, true, '...');

        try {
            const project = await api.get(`/projects/${id}`);
            currentProjectId = id;
            currentProjectData = project;
            document.getElementById('proj-title-display').textContent = `Projeto: ${project.name}`;
            document.getElementById('price-result').style.display = 'none';
            document.getElementById('proj-details').style.display = 'block';
            loadOffersSelect();
            // Load allocation table
            loadAllocationTable(id);

            // Scroll to details
            document.getElementById('proj-details').scrollIntoView({ behavior: 'smooth' });
        } catch (e) {
            alert('Erro ao visualizar projeto.');
        } finally {
            setLoading(btnElement, false);
        }
    }

    async function handleEditProject(id, btnElement) {
        setLoading(btnElement, true, '...');

        try {
            const project = await api.get(`/projects/${id}`);

            editingProjectId = id;
            document.getElementById('modal-project-title').textContent = 'Editar Projeto';
            document.getElementById('btn-save-project').textContent = 'Atualizar Projeto';

            document.getElementById('proj-name').value = project.name;
            document.getElementById('proj-start').value = project.start_date;
            document.getElementById('proj-duration').value = project.duration_months;
            document.getElementById('proj-tax').value = project.tax_rate;
            document.getElementById('proj-margin').value = project.margin_rate;

            document.getElementById('price-result').style.display = 'none';

            modalProject.classList.add('active');
        } catch (e) {
            alert('Erro ao carregar projeto para edição.');
        } finally {
            setLoading(btnElement, false);
        }
    }

    async function handleCloneProject(id, btnElement) {
        if (confirm('Deseja clonar este projeto?')) {
            setLoading(btnElement, true, '');

            try {
                const original = await api.get(`/projects/${id}`);
                await api.post('/projects/', {
                    name: `Cópia de ${original.name}`,
                    start_date: original.start_date,
                    duration_months: original.duration_months,
                    tax_rate: original.tax_rate,
                    margin_rate: original.margin_rate,
                    from_project_id: id,
                    allocations: []
                });
                if (currentProjectId === id) {
                    currentProjectId = null;
                    document.getElementById('proj-details').style.display = 'none';
                    document.getElementById('price-result').style.display = 'none';
                }
                loadProjects();
            } catch (error) {
                alert('Erro ao clonar projeto:\n\n' + getApiErrorMessage(error));
            } finally {
                setLoading(btnElement, false);
            }
        }
    }

    async function handleDeleteProject(id, name, btnElement) {
        if (confirm(`Tem certeza que deseja excluir o projeto "${name}"?`)) {
            setLoading(btnElement, true, '');

            try {
                await api.delete(`/projects/${id}`);
                if (currentProjectId === id) {
                    currentProjectId = null;
                    document.getElementById('proj-details').style.display = 'none';
                    document.getElementById('price-result').style.display = 'none';
                }
                loadProjects();
            } catch (error) {
                console.error("Delete Error:", error);
                alert(`Não foi possível excluir "${name}".\n\n${getApiErrorMessage(error)}`);

                // Restore button only if error occurs
                if (btnElement && document.body.contains(btnElement)) {
                    setLoading(btnElement, false);
                }
            }
        }
    }

    // --- Helper Functions ---

    // Extracts a readable error message from API responses (FastAPI/Pydantic)
    function getApiErrorMessage(error) {
        if (error.detail) {
            if (Array.isArray(error.detail)) {
                return error.detail.map(e => e.msg).join('\n');
            }
            return error.detail;
        }
        if (error.error) return error.error;
        return error.message || "Erro desconhecido.";
    }

    // Manages the visual loading state of buttons
    function setLoading(btn, isLoading, loadingText = 'Carregando...', originalHtml = '') {
        if (!btn) return;
        if (isLoading) {
            // Save original HTML if not already saved
            if (!btn.dataset.originalHtml) {
                btn.dataset.originalHtml = btn.innerHTML;
            }
            btn.disabled = true;
            btn.innerHTML = `<span class="material-icons spin" style="font-size: 1.25rem; vertical-align: bottom; margin-right: 5px;">refresh</span> ${loadingText}`;
        } else {
            btn.disabled = false;
            // Restore: use explicit param OR saved dataset OR current fallback
            btn.innerHTML = originalHtml || btn.dataset.originalHtml || btn.innerHTML;
        }
    }
}
