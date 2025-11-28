import { api } from '../api.js';
import { formatCurrency } from '../utils.js';
import { escapeHtml } from '../sanitize.js';



export async function renderProfessionals(container) {
    let editingId = null;
    let currentSortColumn = 'name';
    let currentSortDirection = 'asc';
    let professionalsData = [];

    // Initial HTML Structure
    container.innerHTML = `
    <div class="card">
      <div class="header-actions">
        <h3>Lista de Profissionais</h3>
        <div style="display: flex; gap: 0.5rem;">
          <button id="btn-import-csv" class="btn" style="background: var(--color-secondary);">
            <span class="material-icons" style="margin-right: 0.5rem;">upload_file</span>
            Importar CSV
          </button>
          <button id="btn-new-prof" class="btn btn-primary">
            <span class="material-icons" style="margin-right: 0.5rem;">add</span>
            Novo Profissional
          </button>
        </div>
      </div>
      <table class="table" id="prof-table">
        <thead>
          <tr>
            <th class="sortable" data-column="pid">ID <span class="material-icons sort-icon">arrow_upward</span></th>
            <th class="sortable" data-column="name">Nome <span class="material-icons sort-icon">arrow_upward</span></th>
            <th class="sortable" data-column="role">Função <span class="material-icons sort-icon">arrow_upward</span></th>
            <th class="sortable" data-column="level">Nível <span class="material-icons sort-icon">arrow_upward</span></th>
            <th class="sortable" data-column="is_template">Tipo <span class="material-icons sort-icon">arrow_upward</span></th>
            <th class="sortable" data-column="hourly_cost">Custo Horário <span class="material-icons sort-icon">arrow_upward</span></th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr><td colspan="7" style="text-align:center; padding: 2rem;">Carregando dados...</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Modal for CSV Import -->
    <div id="modal-import-csv" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Importar Profissionais via CSV</h3>
          <button class="modal-close" id="btn-close-modal-import">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Arquivo CSV</label>
            <input type="file" id="csv-file-input" accept=".csv">
            <small style="display: block; margin-top: 0.5rem; color: var(--color-text-secondary);">
              Formato esperado: pid,name,role,level,is_template,hourly_cost
              <br>
              <a href="professionals_example.csv" download style="color: var(--color-primary);">
                📥 Baixar arquivo de exemplo
              </a>
            </small>
          </div>
          <div id="import-results" style="display: none; margin-top: 1rem; padding: 1rem; border-radius: 8px; background: var(--color-surface-variant);">
            <h4 style="margin-top: 0;">Resultados da Importação</h4>
            <div id="import-stats"></div>
            <div id="import-errors" style="margin-top: 0.5rem;"></div>
          </div>
        </div>
        <div class="modal-footer">
          <button id="btn-cancel-import" class="btn">Cancelar</button>
          <button id="btn-upload-csv" class="btn btn-primary">Importar</button>
        </div>
      </div>
    </div>

    <!-- Modal for Create/Edit Professional -->
    <div id="modal-prof" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3 id="modal-prof-title">Novo Profissional / Template</h3>
          <button class="modal-close" id="btn-close-modal-prof">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>ID</label>
            <input type="text" id="prof-id" placeholder="ex: PROF001">
          </div>
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
              <option value="true">Template</option>
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

    // Fetch Data
    await loadProfessionals();

    // --- Sorting Logic ---
    container.querySelectorAll('th.sortable').forEach((th) => {
        th.addEventListener('click', () => {
            const column = th.dataset.column;
            if (currentSortColumn === column) {
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortColumn = column;
                currentSortDirection = 'asc';
            }
            renderTableBody();
            updateHeaderStyles();
        });
    });

    function updateHeaderStyles() {
        container.querySelectorAll('th.sortable').forEach((th) => {
            th.classList.remove('sorted-asc', 'sorted-desc');
            if (th.dataset.column === currentSortColumn) {
                th.classList.add(
                    currentSortDirection === 'asc' ? 'sorted-asc' : 'sorted-desc'
                );
            }
        });
    }

    function sortData(data) {
        return [...data].sort((a, b) => {
            let valA = a[currentSortColumn];
            let valB = b[currentSortColumn];

            if (valA === null || valA === undefined) valA = '';
            if (valB === null || valB === undefined) valB = '';

            if (typeof valA === 'string') valA = valA.toLowerCase();
            if (typeof valB === 'string') valB = valB.toLowerCase();

            if (valA < valB) return currentSortDirection === 'asc' ? -1 : 1;
            if (valA > valB) return currentSortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }

    // --- Modal Logic (Create/Edit) ---
    const modal = document.getElementById('modal-prof');

    function openModal(title, saveText) {
        document.getElementById('modal-prof-title').textContent = title;
        document.getElementById('btn-save-prof').textContent = saveText;
        modal.classList.add('active');
    }

    function closeModal() {
        modal.classList.remove('active');
        clearForm();
    }

    document.getElementById('btn-new-prof').onclick = () => {
        editingId = null;
        clearForm();
        openModal('Novo Profissional / Template', 'Criar');
    };

    document.getElementById('btn-close-modal-prof').onclick = closeModal;
    document.getElementById('btn-cancel-prof').onclick = closeModal;
    modal.onclick = (e) => {
        if (e.target === modal) closeModal();
    };

    // --- CSV Import Logic ---
    const importModal = document.getElementById('modal-import-csv');
    const importResults = document.getElementById('import-results');
    const csvFileInput = document.getElementById('csv-file-input');

    document.getElementById('btn-import-csv').onclick = () => {
        importModal.classList.add('active');
        importResults.style.display = 'none';
        csvFileInput.value = '';
    };

    const closeImportModal = () => importModal.classList.remove('active');
    document.getElementById('btn-close-modal-import').onclick = closeImportModal;
    document.getElementById('btn-cancel-import').onclick = closeImportModal;
    importModal.onclick = (e) => {
        if (e.target === importModal) closeImportModal();
    };

    document.getElementById('btn-upload-csv').onclick = async () => {
        const file = csvFileInput.files[0];
        if (!file || !file.name.endsWith('.csv')) {
            alert('Por favor, selecione um arquivo CSV válido');
            return;
        }

        const btn = document.getElementById('btn-upload-csv');
        setLoading(btn, true, 'Importando...');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/professionals/import-csv', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Erro ao importar CSV');
            }

            btn.innerHTML = '<span class="material-icons" style="font-size: 1.25rem;">check</span> Importado!';
            btn.classList.add('btn-success');

            importResults.style.display = 'block';
            document.getElementById('import-stats').innerHTML = `
        <p style="margin: 0.25rem 0;">✅ <strong>${result.created}</strong> profissionais criados</p>
        <p style="margin: 0.25rem 0;">🔄 <strong>${result.updated}</strong> profissionais atualizados</p>
        ${result.errors > 0 ? `<p style="margin: 0.25rem 0; color: var(--color-error);">❌ <strong>${result.errors}</strong> erros</p>` : ''}
      `;

            const errorsDiv = document.getElementById('import-errors');
            if (result.error_details?.length > 0) {
                errorsDiv.innerHTML = `
          <details style="margin-top: 0.5rem;">
            <summary style="cursor: pointer; color: var(--color-error);">Ver detalhes dos erros</summary>
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
              ${result.error_details.map((err) => `<li>${escapeHtml(err)}</li>`).join('')}
            </ul>
          </details>
        `;
            } else {
                errorsDiv.innerHTML = '';
            }

            await loadProfessionals();

            setTimeout(() => {
                setLoading(btn, false);
                btn.classList.remove('btn-success');
            }, 2000);
        } catch (error) {
            alert(`Erro ao importar CSV: ${error.message}`);
            setLoading(btn, false);
        }
    };

    // --- CRUD Operations ---

    document.getElementById('btn-save-prof').onclick = async () => {
        const pid = document.getElementById('prof-id').value;
        const name = document.getElementById('prof-name').value;
        const role = document.getElementById('prof-role').value;
        const level = document.getElementById('prof-level').value;
        const is_template = document.getElementById('prof-type').value === 'true';
        const hourly_cost = parseFloat(document.getElementById('prof-cost').value);

        if (pid && name && role && level) {
            const payload = {
                id: editingId ? parseInt(editingId) : null,
                pid,
                name,
                role,
                level,
                is_template,
                hourly_cost
            };

            const btn = document.getElementById('btn-save-prof');
            setLoading(btn, true, 'Salvando...');

            try {
                if (editingId) {
                    await api.put(`/professionals/${editingId}`, payload);
                    editingId = null;
                } else {
                    await api.post('/professionals/', payload);
                }
                closeModal();
                await loadProfessionals();
            } catch (error) {
                alert('Erro ao salvar: ' + getApiErrorMessage(error));
            } finally {
                setLoading(btn, false);
            }
        } else {
            alert('Preencha os campos obrigatórios.');
        }
    };

    function clearForm() {
        document.getElementById('prof-id').value = '';
        document.getElementById('prof-name').value = '';
        document.getElementById('prof-role').value = '';
        document.getElementById('prof-level').value = '';
        document.getElementById('prof-cost').value = '0.0';
        document.getElementById('prof-type').value = 'false';
    }

    async function loadProfessionals() {
        try {
            professionalsData = await api.get('/professionals/');
            renderTableBody();
            updateHeaderStyles();
        } catch (error) {
            console.error('Failed to load professionals', error);
            document.querySelector('#prof-table tbody').innerHTML =
                '<tr><td colspan="7" style="color:red; text-align:center;">Erro ao carregar dados.</td></tr>';
        }
    }

    function renderTableBody() {
        const sortedProfs = sortData(professionalsData);
        const tbody = document.querySelector('#prof-table tbody');

        if (sortedProfs.length === 0) {
            tbody.innerHTML =
                '<tr><td colspan="7" style="text-align:center; padding: 1rem;">Nenhum profissional encontrado.</td></tr>';
            return;
        }

        tbody.innerHTML = sortedProfs
            .map(
                (p) => `
      <tr>
        <td>${escapeHtml(p.pid || '-')}</td>
        <td>${escapeHtml(p.name)}</td>
        <td>${escapeHtml(p.role)}</td>
        <td>${escapeHtml(p.level)}</td>
        <td>${p.is_template ? 'Template' : 'Pessoa'}</td>
        <td>${formatCurrency(p.hourly_cost)}</td>
        <td>
          <button class="btn btn-sm" data-action="edit" data-id="${p.id
                    }">Editar</button>
          <button class="btn btn-sm btn-danger" data-action="delete" data-id="${p.id
                    }" data-name="${escapeHtml(p.name)}">Excluir</button>
        </td>
      </tr>
    `
            )
            .join('');

        // Event Delegation for action buttons
        tbody.querySelectorAll('button[data-action]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                const id = parseInt(btn.dataset.id);

                if (action === 'edit') {
                    handleEditProfessional(id, btn);
                } else if (action === 'delete') {
                    handleDeleteProfessional(id, btn.dataset.name, btn);
                }
            });
        });
    }

    // --- Internal Handlers (Scoped) ---

    async function handleEditProfessional(id, btnElement) {
        setLoading(btnElement, true, '...');

        try {
            // Fetch only specific ID to save bandwidth
            const prof = await api.get(`/professionals/${id}`);

            if (prof) {
                editingId = id;
                document.getElementById('prof-id').value = prof.pid || '';
                document.getElementById('prof-name').value = prof.name;
                document.getElementById('prof-role').value = prof.role;
                document.getElementById('prof-level').value = prof.level;
                document.getElementById('prof-type').value =
                    prof.is_template.toString();
                document.getElementById('prof-cost').value = prof.hourly_cost;

                openModal('Editar Profissional', 'Atualizar');
            }
        } catch (e) {
            console.error(e);
            alert('Erro ao carregar dados do profissional.');
        } finally {
            setLoading(btnElement, false);
        }
    }

    async function handleDeleteProfessional(id, name, btnElement) {
        if (confirm(`Tem certeza que deseja excluir "${name}"?`)) {
            setLoading(btnElement, true, '');

            try {
                await api.delete(`/professionals/${id}`);
                await loadProfessionals();
            } catch (error) {
                console.error("Delete Error:", error);
                alert(`Não foi possível excluir "${name}".\n\n${getApiErrorMessage(error)}`);
                setLoading(btnElement, false);
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