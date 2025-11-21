import { api } from '../api.js';

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
                        <label>Adicionar Item</label>
                        <div style="margin-bottom: 0.5rem;">
                            <select id="off-prof-select" style="width: 100%; padding: 0.5rem; margin-bottom: 0.5rem;">
                                <option value="">-- Selecionar Profissional Específico (Opcional) --</option>
                                ${professionals.map(p => `<option value="${p.id}" data-role="${p.role}" data-level="${p.level}">${p.name} (${p.role} ${p.level})</option>`).join('')}
                            </select>
                        </div>
                        <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <input type="text" id="off-role" placeholder="Função (ex: Desenvolvedor)" style="flex: 1;">
                            <input type="text" id="off-level" placeholder="Nível (ex: Sênior)" style="flex: 1;">
                            <input type="number" id="off-qty" value="1" style="width: 70px;" placeholder="Qtd">
                            <input type="number" id="off-alloc" value="100" style="width: 80px;" placeholder="Aloc %">
                            <button id="btn-add-item" class="btn">Adicionar</button>
                        </div>
                        <small style="color: #6b7280;">Se um profissional for selecionado, Função/Nível são preenchidos automaticamente.</small>
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

    // Auto-fill role/level when professional selected
    document.getElementById('off-prof-select').onchange = (e) => {
        const sel = e.target;
        const opt = sel.options[sel.selectedIndex];
        if (opt.value) {
            document.getElementById('off-role').value = opt.dataset.role;
            document.getElementById('off-level').value = opt.dataset.level;
            document.getElementById('off-qty').value = '1';
            document.getElementById('off-qty').disabled = true; // Can only add 1 specific person
            document.getElementById('off-alloc').value = '100';
        } else {
            document.getElementById('off-role').value = '';
            document.getElementById('off-level').value = '';
            document.getElementById('off-qty').disabled = false;
        }
    };

    // Add item to current list
    document.getElementById('btn-add-item').onclick = () => {
        const profId = document.getElementById('off-prof-select').value;
        const role = document.getElementById('off-role').value;
        const level = document.getElementById('off-level').value;
        let qty = parseInt(document.getElementById('off-qty').value);
        let alloc = parseFloat(document.getElementById('off-alloc').value) || 100;

        if (profId) {
            qty = 1; // Force 1 for specific professional
        }

        if (role && level && qty > 0) {
            const profName = profId ? professionals.find(p => p.id == profId)?.name : null;

            currentItems.push({
                role,
                level,
                quantity: qty,
                allocation_percentage: alloc,
                professional_id: profId ? parseInt(profId) : null,
                professional_name: profName // For display only
            });
            renderItemsList();

            // Reset form
            document.getElementById('off-prof-select').value = '';
            document.getElementById('off-role').value = '';
            document.getElementById('off-level').value = '';
            document.getElementById('off-qty').value = '1';
            document.getElementById('off-alloc').value = '100';
            document.getElementById('off-qty').disabled = false;
        } else {
            alert('Por favor, preencha função, nível e quantidade');
        }
    };

    function renderItemsList() {
        const listDiv = document.getElementById('off-items-list');
        if (currentItems.length === 0) {
            listDiv.innerHTML = '<small style="color: #6b7280;">Nenhum item adicionado ainda</small>';
        } else {
            listDiv.innerHTML = currentItems.map((item, idx) => {
                let label = `${item.quantity}x ${item.role} - ${item.level}`;
                if (item.professional_name) {
                    label = `<strong>${item.professional_name}</strong> (${item.role} ${item.level})`;
                } else if (item.professional_id) {
                    // Fallback if name missing in object (e.g. from edit load)
                    const p = professionals.find(p => p.id == item.professional_id);
                    const pName = p ? p.name : 'Desconhecido';
                    label = `<strong>${pName}</strong> (${item.role} ${item.level})`;
                }

                const allocLabel = item.allocation_percentage ? ` - ${item.allocation_percentage}%` : '';
                label += allocLabel;

                return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: white; border-radius: 0.25rem; margin-bottom: 0.25rem;">
                    <span>${label}</span>
                    <button class="btn btn-sm btn-danger" onclick="removeOfferItem(${idx})">Remover</button>
                </div>
            `}).join('');
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
        document.getElementById('off-role').value = '';
        document.getElementById('off-level').value = '';
        document.getElementById('off-qty').value = '1';
        document.getElementById('off-alloc').value = '100';
        document.getElementById('off-qty').disabled = false;
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
                        <h4 style="margin: 0 0 0.5rem 0;">${t.name}</h4>
                        <small style="color: #6b7280;">${t.items.length} item${t.items.length !== 1 ? 's' : ''}</small>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-sm" onclick="editOffer(${t.id})">Editar</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteOffer(${t.id}, '${t.name}')">Excluir</button>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #e5e7eb;">
                    ${t.items.map(item => {
            let label = `${item.quantity}x ${item.role} - ${item.level}`;
            if (item.professional_id) {
                const p = professionals.find(p => p.id == item.professional_id);
                const pName = p ? p.name : 'Profissional Específico';
                label = `<strong>${pName}</strong> (${item.role} ${item.level})`;
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
