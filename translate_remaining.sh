#!/bin/bash

# Translation script for templates.js and projects.js

# Templates.js translations
sed -i '' \
  -e 's/"New Template"/"Novo Template"/g' \
  -e 's/"Templates List"/"Lista de Templates"/g' \
  -e 's/"Template Name"/"Nome do Template"/g' \
  -e 's/"Name"/"Nome"/g' \
  -e 's/"Role"/"Função"/g' \
  -e 's/"Level"/"Nível"/g' \
  -e 's/"Quantity"/"Quantidade"/g' \
  -e 's/"Qty"/"Qtd"/g' \
  -e 's/"Alloc %"/"Aloc %"/g' \
  -e 's/"Add Item"/"Adicionar Item"/g' \
  -e 's/"Add"/"Adicionar"/g' \
  -e 's/"Remove"/"Remover"/g' \
  -e 's/"Create Template"/"Criar Template"/g' \
  -e 's/"Update Template"/"Atualizar Template"/g' \
  -e 's/"Create"/"Criar"/g' \
  -e 's/"Update"/"Atualizar"/g' \
  -e 's/"Cancel"/"Cancelar"/g' \
  -e 's/"Edit"/"Editar"/g' \
  -e 's/"Delete"/"Excluir"/g' \
  -e 's/"Save"/"Salvar"/g' \
  -e 's/"Actions"/"Ações"/g' \
  -e 's/"Items"/"Itens"/g' \
  -e 's/"No templates created yet"/"Nenhum template criado ainda"/g' \
  -e 's/"No items added yet"/"Nenhum item adicionado ainda"/g' \
  -e 's/"Please enter a template name"/"Por favor, insira um nome para o template"/g' \
  -e 's/"Please add at least one item to the template"/"Por favor, adicione pelo menos um item ao template"/g' \
  -e 's/"Are you sure you want to delete"/"Tem certeza que deseja excluir"/g' \
  -e 's/"Edit Template"/"Editar Template"/g' \
  -e 's/"Failed to load professionals"/"Falha ao carregar profissionais"/g' \
  -e 's/placeholder="Role (e.g. Developer)"/placeholder="Função (ex: Desenvolvedor)"/g' \
  -e 's/placeholder="Level (e.g. Senior)"/placeholder="Nível (ex: Sênior)"/g' \
  -e 's/"If professional is selected, Role\/Level are auto-filled."/"Se o profissional for selecionado, Função\/Nível são preenchidos automaticamente."/g' \
  -e 's/"-- Select Specific Professional (Optional) --"/"-- Selecionar Profissional Específico (Opcional) --"/g' \
  frontend/js/views/templates.js

# Projects.js translations
sed -i '' \
  -e 's/"New Project"/"Novo Projeto"/g' \
  -e 's/"Projects List"/"Lista de Projetos"/g' \
  -e 's/"Project Details"/"Detalhes do Projeto"/g' \
  -e 's/"Start Date"/"Data de Início"/g' \
  -e 's/"Duration (Months)"/"Duração (Meses)"/g' \
  -e 's/"Tax Rate (%)"/"Taxa de Imposto (%)"/' \
  -e 's/"Margin Rate (%)"/"Taxa de Margem (%)"/' \
  -e 's/"Apply Template"/"Aplicar Template"/g' \
  -e 's/"Allocation Table"/"Tabela de Alocação"/g' \
  -e 's/"Add Professional"/"Adicionar Profissional"/g' \
  -e 's/"Save & Calculate"/"Salvar e Calcular"/g' \
  -e 's/"Pricing Result"/"Resultado da Precificação"/g' \
  -e 's/"Total Cost"/"Custo Total"/g' \
  -e 's/"Total Selling"/"Venda Total"/g' \
  -e 's/"Total Margin"/"Margem Total"/g' \
  -e 's/"Total Tax"/"Imposto Total"/g' \
  -e 's/"Final Price"/"Preço Final"/g' \
  -e 's/"Final Margin"/"Margem Final"/g' \
  -e 's/"Select Professional"/"Selecionar Profissional"/g' \
  -e 's/"Selling Rate (Optional)"/"Taxa de Venda (Opcional)"/g' \
  -e 's/"Leave empty for auto-calc"/"Deixe vazio para cálculo automático"/g' \
  -e 's/"If empty, calculated from cost + margin"/"Se vazio, calculado a partir de custo + margem"/g' \
  -e 's/"-- Select --"/"-- Selecionar --"/g' \
  -e 's/"Professional"/"Profissional"/g' \
  -e 's/"Role\/Level"/"Função\/Nível"/g' \
  -e 's/"Cost"/"Custo"/g' \
  -e 's/"Selling Rate"/"Taxa de Venda"/g' \
  -e 's/"Total Hours"/"Total de Horas"/g' \
  -e 's/"No allocations yet. Apply a template or create allocations manually."/"Nenhuma alocação ainda. Aplique um template ou crie alocações manualmente."/g' \
  -e 's/"No allocations yet."/"Nenhuma alocação ainda."/g' \
  -e 's/"No projects created yet"/"Nenhum projeto criado ainda"/g' \
  -e 's/"Please fill all required fields (Name and Start Date)."/"Por favor, preencha todos os campos obrigatórios (Nome e Data de Início)."/g' \
  -e 's/"Create Project"/"Criar Projeto"/g' \
  -e 's/"Update Project"/"Atualizar Projeto"/g' \
  -e 's/"Edit Project"/"Editar Projeto"/g' \
  -e 's/"View"/"Visualizar"/g' \
  -e 's/"Start"/"Início"/g' \
  -e 's/"Duration"/"Duração"/g' \
  -e 's/"months"/"meses"/g' \
  -e 's/"Tax"/"Imposto"/g' \
  -e 's/"Margin"/"Margem"/g' \
  -e 's/"Professional added successfully!"/"Profissional adicionado com sucesso!"/g' \
  -e 's/"Professional removed."/"Profissional removido."/g' \
  -e 's/"Please select a professional."/"Por favor, selecione um profissional."/g' \
  -e 's/"Error adding professional"/"Erro ao adicionar profissional"/g' \
  -e 's/"Error removing professional"/"Erro ao remover profissional"/g' \
  -e 's/"Are you sure you want to remove"/"Tem certeza que deseja remover"/g' \
  -e 's/"from this project"/"deste projeto"/g' \
  -e 's/"Template applied"/"Template aplicado"/g' \
  -e 's/"Saved"/"Salvo"/g' \
  -e 's/"items and calculated price"/"itens e preço calculado"/g' \
  -e 's/"Error saving\/calculating"/"Erro ao salvar\/calcular"/g' \
  frontend/js/views/projects.js

echo "Translation complete!"
