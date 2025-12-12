import { api } from '../api.js';
import { formatCurrency, normalizeText } from '../utils.js';
import { escapeHtml } from '../sanitize.js';



export async function renderProfessionals(container) {
    let editingId = null;
    let currentSortColumn = 'name';
    let currentSortDirection = 'asc';
    let professionalsData = [];
    let currentPage = 1;
    let searchQuery = '';
    let adjustmentsEnabled = false;

    // Initial HTML Structure
    container.innerHTML = `
    <div class="card">
      <div class="header-actions">
        <h3>Lista de Profissionais</h3>
        <div style="display: flex; gap: 1rem; align-items: center; flex: 1; max-width: 400px; margin: 0 1rem;">
          <div style="position: relative; flex: 1;">
            <span class="material-icons" style="position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--md-sys-color-on-surface-variant); font-size: 1.25rem; pointer-events: none;">search</span>
            <input type="text" id="search-professionals" placeholder="Buscar profissionais..." style="width: 100%; padding: 0.5rem 0.5rem 0.5rem 2.75rem; border: 1px solid var(--md-sys-color-outline-variant, #C4C7C5); border-radius: var(--md-sys-shape-corner-medium, 0.5rem); font-size: 0.875rem; background: var(--md-sys-color-surface-container-high, #f5f5f5);">
          </div>
        </div>
        <div style="display: flex; gap: 0.5rem;">
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
      <div id="pagination-controls" style="display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1rem; padding: 1rem;">
        <button id="btn-prev-page" class="btn btn-sm" disabled>Anterior</button>
        <span id="page-indicator" style="color: var(--md-sys-color-on-surface); font-size: 0.875rem;">Página 1 de 1</span>
        <button id="btn-next-page" class="btn btn-sm" disabled>Próxima</button>
      </div>
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

    const toggleAdjustments = document.getElementById('toggle-adjustments');
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

    // Fetch Data
    applyLockState();
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
            currentPage = 1; // Resetar para primeira página ao mudar ordenação
            loadProfessionals();
        });
    });

    // Event listeners para paginação
    document.getElementById('btn-prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadProfessionals();
        }
    });

    document.getElementById('btn-next-page').addEventListener('click', () => {
        currentPage++;
        loadProfessionals();
    });

    // Event listener para busca
    let searchTimeout = null;
    const searchInput = document.getElementById('search-professionals');
    searchInput.addEventListener('input', (e) => {
        // Limpar timeout anterior
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Debounce: aguardar 300ms após o usuário parar de digitar
        searchTimeout = setTimeout(() => {
            searchQuery = e.target.value;
            currentPage = 1; // Resetar para primeira página ao buscar
            loadProfessionals();
        }, 300);
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
        if (!adjustmentsEnabled) return;
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
        if (!adjustmentsEnabled) return;
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
        if (!adjustmentsEnabled) return;
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
        if (!adjustmentsEnabled) return;
        const pid = normalizeText(document.getElementById('prof-id').value);
        const name = normalizeText(document.getElementById('prof-name').value);
        const role = normalizeText(document.getElementById('prof-role').value);
        const level = normalizeText(document.getElementById('prof-level').value);
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
                    await api.patch(`/professionals/${editingId}`, payload);
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

    function updatePaginationControls(page, totalPages) {
        const prevBtn = document.getElementById('btn-prev-page');
        const nextBtn = document.getElementById('btn-next-page');
        const indicator = document.getElementById('page-indicator');

        if (!prevBtn || !nextBtn || !indicator) return;

        prevBtn.disabled = page <= 1;
        nextBtn.disabled = page >= totalPages;
        indicator.textContent = `Página ${page} de ${totalPages || 1}`;
    }

    async function loadProfessionals() {
        try {
            const skip = (currentPage - 1) * 50;
            let url = `/professionals/?skip=${skip}&limit=50`;
            if (searchQuery && searchQuery.trim()) {
                url += `&search=${encodeURIComponent(searchQuery.trim())}`;
            }
            const response = await api.get(url);
            professionalsData = response.items;
            const total = response.total;
            
            renderTableBody();
            updateHeaderStyles();
            applyLockState();
            
            // Atualizar controles de paginação
            const totalPages = Math.ceil(total / 50);
            updatePaginationControls(currentPage, totalPages);
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
            const message = searchQuery && searchQuery.trim() 
                ? `Nenhum profissional encontrado para "${escapeHtml(searchQuery.trim())}"`
                : 'Nenhum profissional encontrado.';
            tbody.innerHTML =
                `<tr><td colspan="7" style="text-align:center; padding: 1rem; color: #6b7280;">${message}</td></tr>`;
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
          <button class="btn btn-sm" data-action="edit" data-id="${p.id}" ${adjustmentsEnabled ? '' : 'disabled'}>Editar</button>
          <button class="btn btn-sm btn-danger" data-action="delete" data-id="${p.id}" data-name="${escapeHtml(p.name)}" ${adjustmentsEnabled ? '' : 'disabled'}>Excluir</button>
        </td>
      </tr>
    `
            )
            .join('');

        // Event Delegation for action buttons
        tbody.querySelectorAll('button[data-action]').forEach((btn) => {
            btn.addEventListener('click', () => {
                if (!adjustmentsEnabled) return;
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
        if (!adjustmentsEnabled) return;
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
        if (!adjustmentsEnabled) return;
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
    function setAdjustmentsEnabled(enabled) {
        adjustmentsEnabled = enabled;

        const toggle = document.getElementById('toggle-adjustments');
        if (toggle) toggle.checked = enabled;

        if (!enabled) {
            const modalProf = document.getElementById('modal-prof');
            if (modalProf) modalProf.classList.remove('active');
            clearForm();

            const modalImport = document.getElementById('modal-import-csv');
            if (modalImport) modalImport.classList.remove('active');

            const importResults = document.getElementById('import-results');
            if (importResults) importResults.style.display = 'none';

            const csvFileInput = document.getElementById('csv-file-input');
            if (csvFileInput) csvFileInput.value = '';
        }

        applyLockState();
    }

    function applyLockState() {
        const locked = !adjustmentsEnabled;

        const toggleWrap = container.querySelector('.adjustments-toggle');
        if (toggleWrap) {
            toggleWrap.classList.toggle('is-unlocked', !locked);
        }

        const indicator = document.getElementById('adjustments-indicator');
        if (indicator) {
            const icon = indicator.querySelector('.material-icons');
            if (icon) icon.textContent = locked ? 'lock' : 'lock_open';
            indicator.title = locked ? 'Bloqueado' : 'Ajustes habilitados';
            indicator.classList.toggle('is-unlocked', !locked);
        }

        // Header actions
        const btnNew = document.getElementById('btn-new-prof');
        const btnImport = document.getElementById('btn-import-csv');
        if (btnNew) btnNew.disabled = locked;
        if (btnImport) btnImport.disabled = locked;

        // Modal actions
        const btnSave = document.getElementById('btn-save-prof');
        const btnUpload = document.getElementById('btn-upload-csv');
        if (btnSave) btnSave.disabled = locked;
        if (btnUpload) btnUpload.disabled = locked;

        const fileInput = document.getElementById('csv-file-input');
        if (fileInput) fileInput.disabled = locked;

        // Disable modal form fields (close/cancel remain enabled)
        document
            .querySelectorAll('#modal-prof .modal-body input, #modal-prof .modal-body select')
            .forEach((el) => {
                el.disabled = locked;
            });
        document
            .querySelectorAll('#modal-import-csv .modal-body input, #modal-import-csv .modal-body select')
            .forEach((el) => {
                el.disabled = locked;
            });

        // Table action buttons (may be re-rendered)
        document.querySelectorAll('#prof-table tbody button[data-action]').forEach((btn) => {
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
