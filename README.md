# Sistema de Precificação de Consultoria

Sistema web para gerenciamento e precificação de projetos de consultoria, desenvolvido com FastAPI e JavaScript vanilla.

## 📋 Descrição

O Sistema de Precificação de Consultoria é uma aplicação web que permite gerenciar profissionais, criar ofertas de equipe e calcular automaticamente os custos e margens de projetos de consultoria. O sistema oferece alocação semanal de profissionais, cálculo automático de preços de venda e gestão completa do ciclo de vida de projetos.

## ✨ Funcionalidades Principais

### Gestão de Profissionais
- Cadastro de profissionais com informações de cargo, nível e custo horário
- Suporte para vagas (profissionais ainda não contratados)
- Identificação única por ID personalizado (PID)
- Visualização e edição de dados profissionais

### Ofertas de Equipe
- Criação de ofertas pré-configuradas com profissionais específicos
- Definição de quantidade e percentual de alocação por profissional
- Aplicação rápida de ofertas a projetos

### Gestão de Projetos
- Criação de projetos com data de início e duração em meses
- Configuração de taxa de impostos e margem de lucro
- Alocação semanal automática de profissionais
- Cálculo de horas disponíveis considerando feriados brasileiros
- Ajuste manual de horas alocadas por semana
- Definição de taxa de venda horária por profissional

### Cálculos Financeiros
- Custo total do projeto baseado em alocações semanais
- Preço de venda calculado com margem configurável
- Aplicação de impostos sobre o preço de venda
- Cálculo de margem final do projeto
- Visualização detalhada de todos os valores financeiros

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e de alta performance
- **SQLAlchemy**: ORM para gerenciamento de banco de dados
- **SQLite**: Banco de dados relacional
- **Pydantic**: Validação de dados e schemas
- **Uvicorn**: Servidor ASGI para desenvolvimento
- **Gunicorn**: Servidor WSGI para produção

### Frontend
- **HTML5/CSS3**: Interface responsiva com Material Design 3
- **JavaScript (Vanilla)**: Lógica de interface sem frameworks
- **Fetch API**: Comunicação com a API REST

### Infraestrutura
- **Google App Engine**: Plataforma de deploy em nuvem
- **Python 3.x**: Linguagem de programação principal

## 📁 Estrutura do Projeto

```
consultancy_pricing/
├── app/
│   ├── models/          # Modelos de dados SQLAlchemy
│   ├── schemas/         # Schemas Pydantic para validação
│   ├── routers/         # Endpoints da API REST
│   ├── services/        # Lógica de negócio
│   ├── database.py      # Configuração do banco de dados
│   └── main.py          # Aplicação FastAPI principal
├── frontend/
│   ├── css/             # Estilos CSS
│   ├── js/
│   │   ├── views/       # Componentes de visualização
│   │   ├── api.js       # Cliente da API
│   │   └── app.js       # Aplicação principal
│   └── index.html       # Página principal
├── tests/               # Testes automatizados
├── app.yaml             # Configuração do Google App Engine
├── requirements.txt     # Dependências Python
└── README.md            # Este arquivo
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd consultancy_pricing
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o servidor de desenvolvimento:
```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

4. Acesse a aplicação em seu navegador:
```
http://localhost:8000/frontend/index.html
```

## 📊 Modelo de Dados

### Professional (Profissional)
- `id`: Identificador único interno
- `pid`: ID personalizado do profissional
- `name`: Nome completo
- `role`: Cargo (ex: Desenvolvedor, Analista)
- `level`: Nível (ex: Júnior, Pleno, Sênior)
- `is_vacancy`: Indica se é uma vaga
- `hourly_cost`: Custo horário do profissional

### Offer (Oferta)
- `id`: Identificador único
- `name`: Nome da oferta
- `items`: Lista de itens da oferta (profissionais)

### OfferItem (Item de Oferta)
- `professional_id`: Referência ao profissional
- `role`: Cargo do profissional
- `level`: Nível do profissional
- `quantity`: Quantidade de profissionais
- `allocation_percentage`: Percentual de alocação

### Project (Projeto)
- `id`: Identificador único
- `name`: Nome do projeto
- `start_date`: Data de início
- `duration_months`: Duração em meses
- `tax_rate`: Taxa de impostos (%)
- `margin_rate`: Margem de lucro (%)
- `allocations`: Alocações de profissionais

### ProjectAllocation (Alocação de Projeto)
- `project_id`: Referência ao projeto
- `professional_id`: Referência ao profissional
- `selling_hourly_rate`: Taxa de venda horária fixa
- `weekly_allocations`: Alocações semanais

### WeeklyAllocation (Alocação Semanal)
- `week_number`: Número sequencial da semana
- `week_start_date`: Data de início da semana (segunda-feira)
- `hours_allocated`: Horas alocadas na semana
- `available_hours`: Horas disponíveis (considerando feriados)

## 🔐 Segurança

O sistema implementa proteção contra XSS (Cross-Site Scripting) através de sanitização de inputs no frontend, garantindo que scripts maliciosos não sejam executados.

## 🌐 Deploy

O projeto está configurado para deploy no Google App Engine. O arquivo `app.yaml` contém as configurações necessárias para o ambiente de produção.

Para fazer deploy:
```bash
gcloud app deploy
```

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato através do repositório do projeto.

---

**Desenvolvido com ❤️ usando FastAPI e Material Design 3**
