"""
Script to translate UI text in JavaScript files to PT-BR
"""

translations = {
    # Common UI elements
    "Name": "Nome",
    "Role": "Função",
    "Level": "Nível",
    "Cost": "Custo",
    "Hourly Cost": "Custo Horário",
    "Is Vacancy": "É Vaga",
    "Vacancy": "Vaga",
    "Actions": "Ações",
    "Edit": "Editar",
    "Delete": "Excluir",
    "Save": "Salvar",
    "Cancel": "Cancelar",
    "Add": "Adicionar",
    "Create": "Criar",
    "Update": "Atualizar",
    "Remove": "Remover",
    "Apply": "Aplicar",
    "Calculate": "Calcular",
    
    # Professionals
    "New Professional": "Novo Profissional",
    "Professionals List": "Lista de Profissionais",
    "Create Professional": "Criar Profissional",
    "Update Professional": "Atualizar Profissional",
    "Professional": "Profissional",
    "Professionals": "Profissionais",
    "No professionals created yet": "Nenhum profissional criado ainda",
    
    # Templates
    "New Template": "Novo Template",
    "Templates List": "Lista de Templates",
    "Create Template": "Criar Template",
    "Update Template": "Atualizar Template",
    "Template": "Template",
    "Templates": "Templates",
    "Add Item": "Adicionar Item",
    "Quantity": "Quantidade",
    "Qty": "Qtd",
    "Alloc %": "Aloc %",
    "Allocation %": "Alocação %",
    "No templates created yet": "Nenhum template criado ainda",
    "No items added yet": "Nenhum item adicionado ainda",
    "If professional is selected, Role/Level are auto-filled.": "Se o profissional for selecionado, Função/Nível são preenchidos automaticamente.",
    "-- Select Specific Professional (Optional) --": "-- Selecionar Profissional Específico (Opcional) --",
    
    # Projects
    "New Project": "Novo Projeto",
    "Projects List": "Lista de Projetos",
    "Create Project": "Criar Projeto",
    "Update Project": "Atualizar Projeto",
    "Project": "Projeto",
    "Projects": "Projetos",
    "Project Details": "Detalhes do Projeto",
    "Start Date": "Data de Início",
    "Duration (Months)": "Duração (Meses)",
    "Tax Rate (%)": "Taxa de Imposto (%)",
    "Margin Rate (%)": "Taxa de Margem (%)",
    "Apply Template": "Aplicar Template",
    "Allocation Table": "Tabela de Alocação",
    "Add Professional": "Adicionar Profissional",
    "Save & Calculate": "Salvar e Calcular",
    "Pricing Result": "Resultado da Precificação",
    "Total Cost": "Custo Total",
    "Total Selling": "Venda Total",
    "Total Margin": "Margem Total",
    "Total Tax": "Imposto Total",
    "Final Price": "Preço Final",
    "Final Margin": "Margem Final",
    "Selling Rate (Optional)": "Taxa de Venda (Opcional)",
    "Leave empty for auto-calc": "Deixe vazio para cálculo automático",
    "If empty, calculated from cost + margin": "Se vazio, calculado a partir de custo + margem",
    "Select Professional": "Selecionar Profissional",
    "-- Select --": "-- Selecionar --",
    "No allocations yet. Apply a template or create allocations manually.": "Nenhuma alocação ainda. Aplique um template ou crie alocações manualmente.",
    "No allocations yet.": "Nenhuma alocação ainda.",
    "No projects created yet": "Nenhum projeto criado ainda",
    
    # Table headers
    "Role/Level": "Função/Nível",
    "Selling Rate": "Taxa de Venda",
    "Total Hours": "Total de Horas",
    "Available": "Disponível",
    
    # Messages
    "Please fill all required fields": "Por favor, preencha todos os campos obrigatórios",
    "Please fill role, level and quantity": "Por favor, preencha função, nível e quantidade",
    "Please enter a template name": "Por favor, insira um nome para o template",
    "Please add at least one item to the template": "Por favor, adicione pelo menos um item ao template",
    "Are you sure you want to delete": "Tem certeza que deseja excluir",
    "Are you sure you want to remove": "Tem certeza que deseja remover",
    "from this project": "deste projeto",
    "Professional added successfully!": "Profissional adicionado com sucesso!",
    "Professional removed.": "Profissional removido.",
    "Template applied": "Template aplicado",
    "Error": "Erro",
    "Error adding professional": "Erro ao adicionar profissional",
    "Error removing professional": "Erro ao remover profissional",
    "Successfully updated": "Atualizado com sucesso",
    "Saved": "Salvo",
    "items and calculated price": "itens e preço calculado",
    "Error saving/calculating": "Erro ao salvar/calcular",
    "Please select a professional.": "Por favor, selecione um profissional.",
    "Professional already allocated to this project": "Profissional já alocado neste projeto",
    
    # Time units
    "Week": "Semana",
    "weeks": "semanas",
    "months": "meses",
    "Duration": "Duração",
    "Start": "Início",
    "Tax": "Imposto",
    "Margin": "Margem",
    
    # Buttons
    "View": "Visualizar",
    "Close": "Fechar",
    "Confirm": "Confirmar",
}

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.content()
    
    original_content = content
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
    
    for english, portuguese in sorted_translations:
        # Replace in strings (both single and double quotes)
        content = content.replace(f'"{english}"', f'"{portuguese}"')
        content = content.replace(f"'{english}'", f"'{portuguese}'")
        content = content.replace(f'>{english}<', f'>{portuguese}<')
        content = content.replace(f'`{english}`', f'`{portuguese}`')
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Translated: {filepath}")
        return True
    else:
        print(f"- No changes: {filepath}")
        return False

if __name__ == "__main__":
    files = [
        "frontend/js/views/professionals.js",
        "frontend/js/views/templates.js",
        "frontend/js/views/projects.js",
    ]
    
    for file in files:
        translate_file(file)
    
    print("\n✅ Translation complete!")
