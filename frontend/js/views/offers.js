import { api } from '../api.js';
import { escapeHtml } from '../sanitize.js';

export async function renderOffers(container) {
    let editingId = null;
    let currentItems = [];
    let professionals = [];

    // Load professionals first
    try {
        professionals = await api.get('/professionals/');
    } catch (e) {
        console.error("Falha ao carregar profissionais", e);
    }

    container.innerHTML = `
        <div class="card">
            <div class="header-actions">
                <h3>Lista de Ofertas</h3>
                <button id="btn-new-offer" class="btn btn-primary">
                    <span class="material-icons" style="margin-right: 0.5rem;">add</span>
                    Nova Oferta
                </button>
            </div>
            <div id="offers-list"></div>
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
                                    <option value="">-- Selecionar Profissional --</option>
                                    ${professionals.map(p => `<option value="${p.id}" data-role="${escapeHtml(p.role)}" data-level="${escapeHtml(p.level)}">${escapeHtml(p.name)} (${escapeHtml(p.role)} ${escapeHtml(p.level)})</option>`).join('')}
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

    // Load offers
    await loadOffers();

    // Modal controls
    const modal = document.getElementById('modal-offer');

    document.getElementById('btn-new-offer').onclick = () => {
        editingId = null;
        currentItems = [];
        document.getElementById('modal-offer-title').textContent = 'Nova Oferta';
        document.getElementById('btn-save-offer').textContent = 'Criar Oferta';
        clearForm();
        renderItemsList();
        modal.classList.add('active');
    };

    document.getElementById('btn-close-modal-offer').onclick = () => {
        modal.classList.remove('active');
        clearForm();
    };

    document.getElementById('btn-cancel-offer').onclick = () => {
        modal.classList.remove('active');
        clearForm();
    };

    // Close modal when clicking outside
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
            clearForm();
        }
    };

    // Function to update professional info display
    function updateProfessionalInfo() {
        const sel = document.getElementById('off-prof-select');
        const opt = sel.options[sel.selectedIndex];
        const profInfo = document.getElementById('prof-info');
        const profRoleLevel = document.getElementById('prof-role-level');
        const alloc = document.getElementById('off-alloc').value || '100';

        if (opt.value) {
            profRoleLevel.textContent = `${opt.dataset.role} ${opt.dataset.level} - ${alloc}% alocação`;
            profInfo.style.display = 'block';
        } else {
            profInfo.style.display = 'none';
        }
    }

    // Show professional info when selected
    document.getElementById('off-prof-select').onchange = updateProfessionalInfo;

    // Update info when allocation percentage changes
    document.getElementById('off-alloc').oninput = () => {
        const sel = document.getElementById('off-prof-select');
        if (sel.value) {
            updateProfessionalInfo();
        }
    };

    // Add item to current list
    document.getElementById('btn-add-item').onclick = () => {
        const profId = document.getElementById('off-prof-select').value;
        const alloc = parseFloat(document.getElementById('off-alloc').value) || 100;

        if (!profId) {
            alert('Por favor, selecione um profissional');
            return;
        }

        const professional = professionals.find(p => p.id == profId);
        if (!professional) {
            alert('Profissional não encontrado');
            return;
        }

        currentItems.push({
            role: professional.role,
            level: professional.level,
            quantity: 1,
            allocation_percentage: alloc,
            professional_id: parseInt(profId),
            professional_name: professional.name
        });

        renderItemsList();

        // Reset form
        document.getElementById('off-prof-select').value = '';
        document.getElementById('off-alloc').value = '100';
        document.getElementById('prof-info').style.display = 'none';
    };

    function renderItemsList() {
        const listDiv = document.getElementById('off-items-list');
        if (currentItems.length === 0) {
            listDiv.innerHTML = '<small style="color: #6b7280;">Nenhum item adicionado ainda</small>';
        } else {
            listDiv.innerHTML = currentItems.map((item, idx) => {
                let label = `${item.quantity}x ${escapeHtml(item.role)} - ${escapeHtml(item.level)}`;
                if (item.professional_name) {
                    label = `<strong>${escapeHtml(item.professional_name)}</strong> (${escapeHtml(item.role)} ${escapeHtml(item.level)})`;
                } else if (item.professional_id) {
                    // Fallback if name missing in object (e.g. from edit load)
                    const p = professionals.find(p => p.id == item.professional_id);
                    const pName = p ? escapeHtml(p.name) : 'Desconhecido';
                    label = `<strong>${pName}</strong> (${escapeHtml(item.role)} ${escapeHtml(item.level)})`;
                }

                const allocLabel = item.allocation_percentage ? ` - ${item.allocation_percentage}%` : '';
                label += allocLabel;

                return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: white; border-radius: 0.25rem; margin-bottom: 0.25rem;">
                    <span>${label}</span>
                    <button class="btn btn-sm btn-danger" data-remove-index="${idx}">Remover</button>
                </div>
            `}).join('');

            // Add event listeners for remove buttons
            listDiv.querySelectorAll('button[data-remove-index]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const idx = parseInt(btn.dataset.removeIndex);
                    window.removeOfferItem(idx);
                });
            });
        }
    }

    window.removeOfferItem = (idx) => {
        currentItems.splice(idx, 1);
        renderItemsList();
    };

    // Save (Create or Update)
    document.getElementById('btn-save-offer').onclick = async () => {
        const name = document.getElementById('off-name').value;

        if (!name) {
            alert('Por favor, insira um nome para a oferta');
            return;
        }

        if (currentItems.length === 0) {
            alert('Por favor, adicione pelo menos um item à oferta');
            return;
        }

        // Clean items for API
        const itemsPayload = currentItems.map(i => ({
            role: i.role,
            level: i.level,
            quantity: i.quantity,
            allocation_percentage: i.allocation_percentage,
            professional_id: i.professional_id
        }));

        if (editingId) {
            // Update
            await api.put(`/offers/${editingId}`, { name, items: itemsPayload });
            editingId = null;
        } else {
            // Create
            await api.post('/offers/', { name, items: itemsPayload });
        }

        modal.classList.remove('active');
        clearForm();
        loadOffers();
    };

    function clearForm() {
        currentItems = [];
        document.getElementById('off-name').value = '';
        document.getElementById('off-prof-select').value = '';
        document.getElementById('off-alloc').value = '100';
        document.getElementById('prof-info').style.display = 'none';
        renderItemsList();
    }

    async function loadOffers() {
        const offers = await api.get('/offers/');
        const listDiv = document.getElementById('offers-list');

        if (offers.length === 0) {
            listDiv.innerHTML = '<p style="color: #6b7280;">Nenhuma oferta criada ainda</p>';
            return;
        }

        listDiv.innerHTML = offers.map(t => `
            <div style="border: 1px solid #e5e7eb; border-radius: 0.375rem; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <div>
                        <h4 style="margin: 0 0 0.5rem 0;">${escapeHtml(t.name)}</h4>
                        <small style="color: #6b7280;">${t.items.length} item${t.items.length !== 1 ? 's' : ''}</small>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-sm" data-action="edit" data-offer-id="${t.id}">Editar</button>
                        <button class="btn btn-sm btn-danger" data-action="delete" data-offer-id="${t.id}" data-offer-name="${escapeHtml(t.name)}">Excluir</button>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #e5e7eb;">
                    ${t.items.map(item => {
            let label = `${item.quantity}x ${escapeHtml(item.role)} - ${escapeHtml(item.level)}`;
            if (item.professional_id) {
                const p = professionals.find(p => p.id == item.professional_id);
                const pName = p ? escapeHtml(p.name) : 'Profissional Específico';
                label = `<strong>${pName}</strong> (${escapeHtml(item.role)} ${escapeHtml(item.level)})`;
            }
            const allocLabel = item.allocation_percentage ? ` - ${item.allocation_percentage}%` : '';
            label += allocLabel;
            return `
                        <div style="padding: 0.25rem 0; color: #374151;">
                            • ${label}
                        </div>
                    `}).join('')}
                </div>
            </div>
        `).join('');

        // Add event delegation for offer action buttons
        listDiv.querySelectorAll('button[data-action]').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                const offerId = parseInt(btn.dataset.offerId);

                if (action === 'edit') {
                    window.editOffer(offerId);
                } else if (action === 'delete') {
                    const offerName = btn.dataset.offerName;
                    window.deleteOffer(offerId, offerName);
                }
            });
        });
    }

    // Edit offer
    window.editOffer = async (id) => {
        const offers = await api.get('/offers/');
        const offer = offers.find(t => t.id === id);

        if (offer) {
            editingId = id;
            currentItems = offer.items.map(item => ({
                role: item.role,
                level: item.level,
                quantity: item.quantity,
                allocation_percentage: item.allocation_percentage || 100,
                professional_id: item.professional_id
            }));

            document.getElementById('modal-offer-title').textContent = 'Editar Oferta';
            document.getElementById('btn-save-offer').textContent = 'Atualizar Oferta';
            document.getElementById('off-name').value = offer.name;
            renderItemsList();
            modal.classList.add('active');
        }
    };

    // Delete offer
    window.deleteOffer = async (id, name) => {
        if (confirm(`Tem certeza que deseja excluir a oferta "${name}"?`)) {
            await api.delete(`/offers/${id}`);
            loadOffers();
        }
    };
}
