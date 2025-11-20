import { api } from '../api.js';
import { formatCurrency } from '../utils.js';

export async function renderProfessionals(container) {
    let editingId = null;

    container.innerHTML = `
        <div class="card">
            <div class="header-actions">
                <h3>Lista de Profissionais</h3>
                <button id="btn-new-prof" class="btn btn-primary">
                    <span class="material-icons" style="margin-right: 0.5rem;">add</span>
                    Novo Profissional
                </button>
            </div>
            <table class="table" id="prof-table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Função</th>
                        <th>Nível</th>
                        <th>Tipo</th>
                        <th>Custo Horário</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>

        <!-- Modal for Create/Edit Professional -->
        <div id="modal-prof" class="modal-overlay">
            <div class="modal-container">
                <div class="modal-header">
                    <h3 id="modal-prof-title">Novo Profissional / Vaga</h3>
                    <button class="modal-close" id="btn-close-modal-prof">
                        <span class="material-icons">close</span>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Nome</label>
                        <input type="text" id="prof-name">
                    </div>
                    <div class="form-group">
                        <label>Função</label>
                        <input type="text" id="prof-role" placeholder="ex: Desenvolvedor">
                    </div>
                    <div class="form-group">
                        <label>Nível</label>
                        <input type="text" id="prof-level" placeholder="ex: Sênior">
                    </div>
                    <div class="form-group">
                        <label>Tipo</label>
                        <select id="prof-type">
                            <option value="false">Pessoa</option>
                            <option value="true">Vaga</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Custo Horário</label>
                        <input type="number" id="prof-cost" value="0.0">
                    </div>
                </div>
                <div class="modal-footer">
                    <button id="btn-cancel-prof" class="btn">Cancelar</button>
                    <button id="btn-save-prof" class="btn btn-primary">Criar</button>
                </div>
            </div>
        </div>
    `;

    // Load Professionals
    await loadProfessionals();

    // Modal controls
    const modal = document.getElementById('modal-prof');

    document.getElementById('btn-new-prof').onclick = () => {
        editingId = null;
        document.getElementById('modal-prof-title').textContent = 'Novo Profissional / Vaga';
        document.getElementById('btn-save-prof').textContent = 'Criar';
        clearForm();
        modal.classList.add('active');
    };

    document.getElementById('btn-close-modal-prof').onclick = () => {
        modal.classList.remove('active');
        clearForm();
    };

    document.getElementById('btn-cancel-prof').onclick = () => {
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

    // Save (Create or Update)
    document.getElementById('btn-save-prof').onclick = async () => {
        const name = document.getElementById('prof-name').value;
        const role = document.getElementById('prof-role').value;
        const level = document.getElementById('prof-level').value;
        const is_vacancy = document.getElementById('prof-type').value === 'true';
        const hourly_cost = parseFloat(document.getElementById('prof-cost').value);

        if (name && role && level) {
            if (editingId) {
                // Update
                await api.put(`/professionals/${editingId}`, { name, role, level, is_vacancy, hourly_cost });
                editingId = null;
            } else {
                // Create
                await api.post('/professionals/', { name, role, level, is_vacancy, hourly_cost });
            }

            modal.classList.remove('active');
            clearForm();
            loadProfessionals();
        } else {
            alert('Por favor, preencha todos os campos obrigatórios (Nome, Função, Nível)');
        }
    };

    function clearForm() {
        document.getElementById('prof-name').value = '';
        document.getElementById('prof-role').value = '';
        document.getElementById('prof-level').value = '';
        document.getElementById('prof-cost').value = '0.0';
        document.getElementById('prof-type').value = 'false';
    }

    async function loadProfessionals() {
        const profs = await api.get('/professionals/');
        const tbody = document.querySelector('#prof-table tbody');
        tbody.innerHTML = profs.map(p => `
            <tr>
                <td>${p.name}</td>
                <td>${p.role}</td>
                <td>${p.level}</td>
                <td>${p.is_vacancy ? 'Vaga' : 'Pessoa'}</td>
                <td>${formatCurrency(p.hourly_cost)}</td>
                <td>
                    <button class="btn btn-sm" onclick="editProfessional(${p.id})">Editar</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProfessional(${p.id}, '${p.name}')">Excluir</button>
                </td>
            </tr>
        `).join('');
    }

    // Make functions available globally for onclick handlers
    window.editProfessional = async (id) => {
        const profs = await api.get('/professionals/');
        const prof = profs.find(p => p.id === id);
        if (prof) {
            editingId = id;
            document.getElementById('modal-prof-title').textContent = 'Editar Profissional';
            document.getElementById('btn-save-prof').textContent = 'Atualizar';

            document.getElementById('prof-name').value = prof.name;
            document.getElementById('prof-role').value = prof.role;
            document.getElementById('prof-level').value = prof.level;
            document.getElementById('prof-type').value = prof.is_vacancy.toString();
            document.getElementById('prof-cost').value = prof.hourly_cost;

            modal.classList.add('active');
        }
    };

    window.deleteProfessional = async (id, name) => {
        if (confirm(`Tem certeza que deseja excluir "${name}"?`)) {
            await api.delete(`/professionals/${id}`);
            loadProfessionals();
        }
    };
}
