import { api } from '../api.js';
import { normalizeText, $ } from '../utils.js';
import { escapeHtml } from '../sanitize.js';



export async function renderOffers(container) {
    let editingId = null;
    let currentItems = [];
    let editingOriginalItems = [];
    let professionalsMap = new Map();
    let currentSortBy = 'name';
    let currentSortDirection = 'asc';
    let offersCache = new Map();
    let adjustmentsEnabled = false;

    // Initial HTML Structure
    container.innerHTML = `
    <div class="card">
        <div class="header-actions">
            <h3>Lista de Ofertas</h3>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <div class="adjustments-toggle">
                    <span class="adjustments-toggle__label">Habilitar ajustes</span>
                    <label class="toggle-switch">
                        <input type="checkbox" id="toggle-adjustments">
                        <span class="toggle-slider" aria-hidden="true"></span>
                    </label>
                    <span id="adjustments-indicator" class="adjustments-indicator" title="Bloqueado">
                        <span class="material-icons" aria-hidden="true">lock</span>
                    </span>
                </div>
                <button id="btn-new-offer" class="btn btn-primary">
                    <span class="material-icons" style="margin-right: 0.5rem;">add</span>
                    Nova Oferta
                </button>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; padding: 0 0.5rem;">
            <label style="font-size: 0.875rem; color: var(--md-sys-color-on-surface-variant); font-weight: 500;">Ordenar por:</label>
            <select id="sort-select" style="padding: 0.5rem; border: 1px solid var(--md-sys-color-outline); border-radius: 0.25rem; background: var(--md-sys-color-surface); color: var(--md-sys-color-on-surface); font-size: 0.875rem;">
                <option value="name">Nome</option>
                <option value="items_count">Número de Itens</option>
                <option value="created_at">Data de Criação</option>
            </select>
            <button id="sort-direction-btn" class="btn btn-sm" style="display: flex; align-items: center; gap: 0.25rem; min-width: auto; padding: 0.5rem 0.75rem;">
                <span class="material-icons" id="sort-icon" style="font-size: 1.25rem;">arrow_upward</span>
            </button>
        </div>
        <div id="offers-list">
            <div style="padding: 2rem; text-align: center; color: #6b7280;">Carregando ofertas...</div>
        </div>
    </div>

    <!-- Modal for Create/Edit Offer -->
    <div id="modal-offer" class="modal-overlay">
        <div class="modal-container wide">
            <div class="modal-header">
                <h3 id="modal-offer-title">Nova Oferta</h3>
                <button class="modal-close" id="btn-close-modal-offer">
                    <span class="material-icons">close</span>
                </button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Nome</label>
                    <input type="text" id="off-name">
                </div>
                <div class="form-group">
                    <div style="display: grid; grid-template-columns: 1fr auto; gap: 1rem; margin-bottom: 0.5rem;">
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 500; font-size: 0.75rem; letter-spacing: 0.5px; color: var(--md-sys-color-on-surface-variant); text-transform: uppercase;">Adicionar Profissional</label>
                            <select id="off-prof-select" style="width: 100%; padding: 0.5rem;">
                                <option value="">-- Carregando... --</option>
                            </select>
                        </div>
                        <div style="width: 120px;">
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 500; font-size: 0.75rem; letter-spacing: 0.5px; color: var(--md-sys-color-on-surface-variant); text-transform: uppercase;">Alocação (%)</label>
                            <input type="number" id="off-alloc" value="100" style="width: 100%; padding: 0.5rem;" placeholder="100">
                        </div>
                    </div>
                    <div id="prof-info" style="margin-bottom: 0.5rem; padding: 0.5rem; background: #f3f4f6; border-radius: 0.25rem; display: none;">
                        <small style="color: #374151;"><strong>Função/Nível:</strong> <span id="prof-role-level"></span></small>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <button id="btn-add-item" class="btn btn-primary" style="width: 100%;">Adicionar à Oferta</button>
                    </div>
                    <small style="color: #6b7280;">Selecione um profissional da comparação. A função e nível serão preenchidos automaticamente com base no profissional selecionado.</small>
                </div>
                <div id="off-items-list" style="min-height: 60px; padding: 0.5rem; background: #f9fafb; border-radius: 0.375rem; margin-bottom: 1rem;">
                    <small style="color: #6b7280;">Nenhum item adicionado ainda</small>
                </div>
            </div>
            <div class="modal-footer">
                <button id="btn-cancel-offer" class="btn">Cancelar</button>
                <button id="btn-save-offer" class="btn btn-primary">Criar Oferta</button>
            </div>
        </div>
    </div>
  `;

    const toggleAdjustments = $('toggle-adjustments');
    if (toggleAdjustments) {
        toggleAdjustments.checked = false;
        toggleAdjustments.addEventListener('change', (e) => {
            const nextEnabled = e.target.checked;
            if (nextEnabled) {
                const ok = confirm(
                    'Atenção: a mudança das informações só deve ser feita pela equipe do CoE.\n\nDeseja habilitar ajustes?'
                );
                if (!ok) {
                    e.target.checked = false;
                    return;
                }
                setAdjustmentsEnabled(true);
            } else {
                setAdjustmentsEnabled(false);
            }
        });
    }
    applyLockState();

    // Fetch critical data in parallel
    try {
        const [profs, offersData] = await Promise.all([
            api.get('/professionals/'),
            api.get('/offers/')
        ]);

        const profsList = profs.items;
        professionalsMap = new Map(profsList.map(p => [p.id, p]));

        populateProfessionalSelect(profsList);
        await enrichAndRenderOffers(offersData);
    } catch (e) {
        console.error("Initialization error", e);
        $('offers-list').innerHTML = '<p style="color: red;">Erro ao carregar dados.</p>';
    }

    // --- Event Listeners ---

    $('sort-select').addEventListener('change', (e) => {
        currentSortBy = e.target.value;
        reloadOffers();
    });

    $('sort-direction-btn').addEventListener('click', () => {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
        const icon = $('sort-icon');
        icon.textContent = currentSortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward';
        reloadOffers();
    });

    const modal = $('modal-offer');

    $('btn-new-offer').onclick = () => {
        if (!adjustmentsEnabled) return;
        editingId = null;
        currentItems = [];
        $('modal-offer-title').textContent = 'Nova Oferta';
        $('btn-save-offer').textContent = 'Criar Oferta';
        clearForm();
        renderItemsList();
        modal.classList.add('active');
    };

    $('btn-close-modal-offer').onclick = () => { modal.classList.remove('active'); clearForm(); };
    $('btn-cancel-offer').onclick = () => { modal.classList.remove('active'); clearForm(); };
    modal.onclick = (e) => { if (e.target === modal) { modal.classList.remove('active'); clearForm(); } };

    // --- Helper Functions ---

    function populateProfessionalSelect(profList) {
        const list = profList || Array.from(professionalsMap.values());
        const select = $('off-prof-select');

        const options = list
            .filter(p => p.is_template)
            .map(p => `<option value="${p.id}" data-role="${escapeHtml(p.role)}" data-level="${escapeHtml(p.level)}">${escapeHtml(p.name)} (${escapeHtml(p.role)} ${escapeHtml(p.level)})</option>`)
            .join('');
        select.innerHTML = '<option value="">-- Selecionar Profissional --</option>' + options;
    }

    function updateProfessionalInfo() {
        const sel = $('off-prof-select');
        const opt = sel.options[sel.selectedIndex];
        const profInfo = $('prof-info');
        const profRoleLevel = $('prof-role-level');
        const alloc = $('off-alloc').value || '100';

        if (opt.value) {
            profRoleLevel.textContent = `${opt.dataset.role} ${opt.dataset.level} - ${alloc}% alocação`;
            profInfo.style.display = 'block';
        } else {
            profInfo.style.display = 'none';
        }
    }

    $('off-prof-select').onchange = updateProfessionalInfo;
    $('off-alloc').oninput = () => {
        if ($('off-prof-select').value) updateProfessionalInfo();
    };

    $('btn-add-item').onclick = () => {
        if (!adjustmentsEnabled) return;
        const profId = $('off-prof-select').value;
        const alloc = parseFloat($('off-alloc').value) || 100;

        if (!profId) { alert('Por favor, selecione um profissional'); return; }

        const professional = professionalsMap.get(parseInt(profId));
        if (!professional) { alert('Profissional não encontrado'); return; }

        currentItems.push({
            role: professional.role,
            level: professional.level,
            allocation_percentage: alloc,
            professional_id: professional.id,
            professional_name: professional.name
        });

        renderItemsList();

        $('off-prof-select').value = '';
        $('off-alloc').value = '100';
        $('prof-info').style.display = 'none';
    };

    function renderItemsList() {
        const listDiv = $('off-items-list');
        if (currentItems.length === 0) {
            listDiv.innerHTML = '<small style="color: #6b7280;">Nenhum item adicionado ainda</small>';
            return;
        }

        listDiv.innerHTML = currentItems.map((item, idx) => {
            let label = '';
            if (item.professional_id) {
                const p = professionalsMap.get(item.professional_id);
                const pName = p ? escapeHtml(p.name) : (item.professional_name || 'Profissional Específico');
                const pRole = p ? escapeHtml(p.role) : (item.role || '?');
                const pLevel = p ? escapeHtml(p.level) : (item.level || '?');
                label = `<strong>${pName}</strong> (${pRole} ${pLevel})`;
            } else {
                label = `${escapeHtml(item.role || '?')} - ${escapeHtml(item.level || '?')}`;
            }

            const allocLabel = item.allocation_percentage ? ` - ${item.allocation_percentage}%` : '';

            return `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: white; border-radius: 0.25rem; margin-bottom: 0.25rem;">
            <span>${label}${allocLabel}</span>
            <button class="btn btn-sm btn-danger" data-remove-index="${idx}" ${adjustmentsEnabled ? '' : 'disabled'}>Remover</button>
        </div>
      `;
        }).join('');

        listDiv.querySelectorAll('button[data-remove-index]').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!adjustmentsEnabled) return;
                handleRemoveOfferItem(parseInt(btn.dataset.removeIndex));
            });
        });
    }

    function handleRemoveOfferItem(idx) {
        if (!adjustmentsEnabled) return;
        currentItems.splice(idx, 1);
        renderItemsList();
    }

    // --- API Interactions ---

    $('btn-save-offer').onclick = async () => {
        if (!adjustmentsEnabled) return;
        const name = normalizeText($('off-name').value);

        if (!name) { alert('Por favor, insira um nome para a oferta'); return; }
        if (currentItems.length === 0) { alert('Por favor, adicione pelo menos um item à oferta'); return; }

        const btn = $('btn-save-offer');
        setLoading(btn, true, 'Salvando...');

        const itemsPayload = currentItems.map(i => ({
            allocation_percentage: i.allocation_percentage,
            professional_id: i.professional_id
        }));

        try {
            if (editingId) {
                await api.patch(`/offers/${editingId}`, { name });
                const itemsToDelete = editingOriginalItems || [];
                const deletePromises = itemsToDelete.map(item =>
                    api.delete(`/offers/${editingId}/items/${item.id}`)
                );
                const createPromises = itemsPayload.map(item =>
                    api.post(`/offers/${editingId}/items`, item)
                );

                await Promise.all([...deletePromises, ...createPromises]);

                editingId = null;
                editingOriginalItems = [];
            } else {
                await api.post('/offers/', { name, items: itemsPayload });
            }

            btn.innerHTML = '<span class="material-icons" style="font-size: 1.25rem;">check</span> Salvo!';
            btn.classList.add('btn-success');

            setTimeout(() => {
                modal.classList.remove('active');
                clearForm();
                reloadOffers();
                setLoading(btn, false);
                btn.classList.remove('btn-success');
            }, 1500);

        } catch (error) {
            alert('Erro ao salvar oferta:\n\n' + getApiErrorMessage(error));
            setLoading(btn, false);
        }
    };

    function clearForm() {
        currentItems = [];
        editingOriginalItems = [];
        $('off-name').value = '';
        $('off-prof-select').value = '';
        $('off-alloc').value = '100';
        $('prof-info').style.display = 'none';
        renderItemsList();
    }

    function sortOffers(offers, sortBy, direction) {
        return [...offers].sort((a, b) => {
            let aVal, bVal;
            if (sortBy === 'name') {
                aVal = a.name.toLowerCase(); bVal = b.name.toLowerCase();
                return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            } else if (sortBy === 'items_count') {
                aVal = a.items.length; bVal = b.items.length;
            } else if (sortBy === 'created_at') {
                aVal = a.created_at ? new Date(a.created_at) : a.id;
                bVal = b.created_at ? new Date(b.created_at) : b.id;
            }
            if (direction === 'asc') return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
            return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
        });
    }

    async function reloadOffers() {
        const listDiv = $('offers-list');
        listDiv.innerHTML = '<div style="padding: 1rem; text-align: center; color: #6b7280;">Atualizando...</div>';
        try {
            const offers = await api.get('/offers/');
            await enrichAndRenderOffers(offers);
        } catch (e) {
            listDiv.innerHTML = '<p style="color:red">Erro ao atualizar ofertas.</p>';
        }
    }

    async function enrichAndRenderOffers(offers) {
        const listDiv = $('offers-list');

        if (offers.length === 0) {
            listDiv.innerHTML = '<p style="color: #6b7280;">Nenhuma oferta criada ainda</p>';
            applyLockState();
            return;
        }

        const offersWithItems = offers.map(o => ({
            ...o,
            items: Array.isArray(o.items) ? o.items : []
        }));

        offersCache = new Map(offersWithItems.map(o => [o.id, o]));

        const sortedOffers = sortOffers(offersWithItems, currentSortBy, currentSortDirection);

        listDiv.innerHTML = sortedOffers.map(t => {
            const errorBadge = t.error ? '<small style="color:red; margin-left: 0.5rem;">(Erro ao carregar detalhes)</small>' : '';
            return `
        <div style="border: 1px solid #e5e7eb; border-radius: 0.375rem; padding: 1rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                <div>
                    <h4 style="margin: 0 0 0.5rem 0;">${escapeHtml(t.name)}${errorBadge}</h4>
                    <small style="color: #6b7280;">${t.items.length} item${t.items.length !== 1 ? 's' : ''}</small>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-sm" data-action="edit" data-offer-id="${t.id}" ${adjustmentsEnabled ? '' : 'disabled'}>Editar</button>
                    <button class="btn btn-sm btn-danger" data-action="delete" data-offer-id="${t.id}" data-offer-name="${escapeHtml(t.name)}" ${adjustmentsEnabled ? '' : 'disabled'}>Excluir</button>
                </div>
            </div>
            <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #e5e7eb;">
                ${t.items.map(item => {
                let label = '';
                if (item.professional_id) {
                    const p = professionalsMap.get(item.professional_id);
                    const pName = p ? escapeHtml(p.name) : 'Profissional Específico';
                    label = `<strong>${pName}</strong> (${p ? escapeHtml(p.role) : '?'} ${p ? escapeHtml(p.level) : '?'})`;
                }
                const allocLabel = item.allocation_percentage ? ` - ${item.allocation_percentage}%` : '';
                return `<div style="padding: 0.25rem 0; color: #374151;">• ${label}${allocLabel}</div>`;
            }).join('')}
            </div>
        </div>
      `;
        }).join('');

        listDiv.querySelectorAll('button[data-action]').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!adjustmentsEnabled) return;
                const action = btn.dataset.action;
                const offerId = parseInt(btn.dataset.offerId);

                if (action === 'edit') handleEditOffer(offerId, btn);
                else if (action === 'delete') handleDeleteOffer(offerId, btn.dataset.offerName, btn);
            });
        });

        applyLockState();
    }

    // --- Scoped Internal Handlers ---

    async function handleEditOffer(id, btnElement) {
        if (!adjustmentsEnabled) return;
        setLoading(btnElement, true, '');

        try {
            const offer = await api.get(`/offers/${id}`);

            editingId = id;
            editingOriginalItems = Array.isArray(offer.items) ? offer.items : [];
            currentItems = editingOriginalItems.map(item => {
                const p = professionalsMap.get(item.professional_id);
                return {
                    id: item.id,
                    role: p ? p.role : '?',
                    level: p ? p.level : '?',
                    allocation_percentage: item.allocation_percentage || 100,
                    professional_id: item.professional_id,
                    professional_name: p ? p.name : 'Profissional Específico'
                };
            });

            $('modal-offer-title').textContent = 'Editar Oferta';
            $('btn-save-offer').textContent = 'Atualizar Oferta';
            $('off-name').value = offer.name || (offersCache.get(id)?.name ?? '');
            renderItemsList();
            modal.classList.add('active');
        } catch (e) {
            console.error(e);
            alert('Erro ao carregar oferta.');
        } finally {
            setLoading(btnElement, false);
        }
    }

    async function handleDeleteOffer(id, name, btnElement) {
        if (!adjustmentsEnabled) return;
        if (confirm(`Tem certeza que deseja excluir a oferta "${name}"?`)) {
            setLoading(btnElement, true, '');
            try {
                await api.delete(`/offers/${id}`);
                reloadOffers();
            } catch (error) {
                alert(`Não foi possível excluir "${name}".\n\n${getApiErrorMessage(error)}`);
                setLoading(btnElement, false);
            }
        }
    }

    // --- Helper Functions ---
    function setAdjustmentsEnabled(enabled) {
        adjustmentsEnabled = enabled;

        const toggle = $('toggle-adjustments');
        if (toggle) toggle.checked = enabled;

        if (!enabled) {
            const modal = $('modal-offer');
            if (modal) modal.classList.remove('active');
            clearForm();
            editingId = null;
        }

        applyLockState();
    }

    function applyLockState() {
        const locked = !adjustmentsEnabled;

        const toggleWrap = container.querySelector('.adjustments-toggle');
        if (toggleWrap) toggleWrap.classList.toggle('is-unlocked', !locked);

        const indicator = $('adjustments-indicator');
        if (indicator) {
            const icon = indicator.querySelector('.material-icons');
            if (icon) icon.textContent = locked ? 'lock' : 'lock_open';
            indicator.title = locked ? 'Bloqueado' : 'Ajustes habilitados';
            indicator.classList.toggle('is-unlocked', !locked);
        }

        const btnNew = $('btn-new-offer');
        if (btnNew) btnNew.disabled = locked;

        const btnAddItem = $('btn-add-item');
        const btnSave = $('btn-save-offer');
        if (btnAddItem) btnAddItem.disabled = locked;
        if (btnSave) btnSave.disabled = locked;

        document
            .querySelectorAll('#modal-offer .modal-body input, #modal-offer .modal-body select')
            .forEach((el) => {
                el.disabled = locked;
            });

        document.querySelectorAll('#offers-list button[data-action]').forEach((btn) => {
            btn.disabled = locked;
        });

        document.querySelectorAll('#off-items-list button[data-remove-index]').forEach((btn) => {
            btn.disabled = locked;
        });
    }

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
            btn.dataset.originalHtml = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = `<span class="material-icons spin" style="font-size: 1.25rem; vertical-align: bottom; margin-right: 5px;">refresh</span> ${loadingText}`;
        } else {
            btn.disabled = false;
            btn.innerHTML = originalHtml || btn.dataset.originalHtml || btn.innerHTML;
        }
    }
}
