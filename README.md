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
- **PostgreSQL**: Banco de dados relacional
- **Pydantic**: Validação de dados e schemas
- **Uvicorn**: Servidor ASGI para desenvolvimento
- **Gunicorn**: Servidor WSGI para produção

### Frontend
- **HTML5/CSS3**: Interface responsiva com Material Design 3
- **JavaScript (Vanilla)**: Lógica de interface sem frameworks
- **Fetch API**: Comunicação com a API REST

### Infraestrutura
- **Docker**: Containerização para deploy local e em nuvem
- **PostgreSQL**: Banco de dados em container
- **Python 3.12**: Linguagem de programação principal

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
├── Dockerfile           # Configuração Docker
├── docker-compose.yml   # Orquestração de containers
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

## ❤️‍🩹 Monitoramento e Health Checks

### Endpoint de Health Check

A aplicação fornece um endpoint `/health` que verifica:
- Status da API
- Conectividade com o banco de dados PostgreSQL

**Acesso direto:**
```
GET http://localhost:8080/health
```

**Resposta (saudável):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Resposta (não saudável):**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "mensagem de erro"
}
```

### Health Checks no Docker

O Dockerfile e docker-compose.yml incluem configurações de health check:

**Dockerfile:**
- Intervalo: 30 segundos
- Timeout: 10 segundos
- Período de inicialização: 40 segundos
- Retries: 3

**Docker Compose:**
- App depende do PostgreSQL estar saudável antes de iniciar
- PostgreSQL usa `pg_isready` para verificar disponibilidade

**Ver status:**
```bash
docker-compose ps
# Mostra (healthy) ou (unhealthy) ao lado de cada serviço
```

## 🐳 Deploy com Docker

### Pré-requisitos
- Docker Desktop instalado e em execução
- Docker Compose (incluso no Docker Desktop)

### Configuração de Ambiente

#### 1. Criar arquivo `.env`

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

#### 2. Configurar variáveis de ambiente

Edite o arquivo `.env` conforme necessário:

```bash
# Ambiente (development ou production)
ENVIRONMENT=development

# CORS: use "*" para desenvolvimento, especifique domínios para produção
CORS_ORIGINS=*

# Credenciais do banco de dados
DB_USER=postgres
DB_PASS=postgres
DB_NAME=consultancy_pricing
```

> [!IMPORTANT]
> O arquivo `.env` não é versionado no Git por questões de segurança. Nunca commite credenciais ou dados sensíveis!

### Ambientes: Desenvolvimento vs Produção

O projeto oferece duas configurações Docker:

#### **Desenvolvimento** (`docker-compose.yml`)
- ✅ Hot-reload de código (volumes montados)
- ✅ CORS permissivo (`*`)
- ✅ Logs detalhados
- ✅ Ideal para Docker Desktop local

#### **Produção** (`docker-compose.prod.yml`)
- 🔒 Código fixo na imagem (sem volumes)
- 🔒 CORS restrito (domínios específicos)
- 🔒 Configurações de segurança
- 🔒 Pronto para deploy em nuvem

### Desenvolvimento Local com Docker

#### Opção 1: Usando Docker Compose (Recomendado)

1. **Build e iniciar os containers**:
```bash
docker-compose up --build
```

2. **Executar em background**:
```bash
docker-compose up -d
```

3. **Acessar a aplicação**:
```
http://localhost:8080/frontend/index.html
```

4. **Ver logs**:
```bash
docker-compose logs -f app
```

5. **Parar os containers**:
```bash
docker-compose down
```

#### Opção 2: Usando Docker diretamente

1. **Build da imagem**:
```bash
docker build -t consultancy-pricing .
```

2. **Executar o container**:
```bash
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  --name consultancy-pricing \
  consultancy-pricing
```

3. **Ver logs**:
```bash
docker logs -f consultancy-pricing
```

4. **Parar e remover o container**:
```bash
docker stop consultancy-pricing
docker rm consultancy-pricing
```

```

### Deploy em Produção

Para executar em ambiente de produção usando `docker-compose.prod.yml`:

> [!IMPORTANT]
> Em produção, a aplicação usa um **banco de dados gerenciado**. **Recomendamos o [Supabase](https://supabase.com)** para uma configuração rápida e gratuita.
> 
> 📖 **[Veja o guia completo de deployment com Supabase](DEPLOYMENT.md)**

<details>
<summary>Outras opções de banco de dados gerenciado</summary>

Você também pode usar:
- Google Cloud SQL
- AWS RDS
- Azure Database for PostgreSQL

</details>

#### 1. Provisionar banco de dados gerenciado

Escolha seu provedor e crie uma instância PostgreSQL:

**Google Cloud SQL:**
```bash
gcloud sql instances create consultancy-pricing-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

gcloud sql databases create consultancy_pricing \
  --instance=consultancy-pricing-db
```

**AWS RDS:**
```bash
aws rds create-db-instance \
  --db-instance-identifier consultancy-pricing-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --allocated-storage 20
```

**Azure Database:**
```bash
az postgres server create \
  --resource-group myResourceGroup \
  --name consultancy-pricing-db \
  --location eastus \
  --sku-name B_Gen5_1 \
  --version 15
```

#### 2. Configurar variáveis de produção

Edite o arquivo `.env` com valores de produção:

```bash
ENVIRONMENT=production
CORS_ORIGINS=https://seudominio.com,https://www.seudominio.com

# Exemplo para Cloud SQL (IP privado):
INSTANCE_CONNECTION_NAME=10.x.x.x:5432

# Exemplo para AWS RDS:
# INSTANCE_CONNECTION_NAME=mydb.abc123.us-east-1.rds.amazonaws.com:5432

# Exemplo para Azure:
# INSTANCE_CONNECTION_NAME=myserver.postgres.database.azure.com:5432

DB_USER=seu_usuario_prod
DB_PASS=senha_segura_aqui
DB_NAME=consultancy_pricing
```

#### 3. Configurar conectividade

**Opção A: VPC/Rede Privada** (Recomendado)
- Configure o container na mesma VPC que o banco de dados
- Use IP privado para conexão

**Opção B: Cloud SQL Proxy** (Google Cloud)
```bash
# Adicione ao Dockerfile se usar Cloud SQL Proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
RUN chmod +x cloud_sql_proxy
```

**Opção C: IP Público** (Menos seguro)
- Configure firewall do banco para aceitar IP do container
- Use SSL/TLS obrigatoriamente

#### 4. Executar com configuração de produção

```bash
# Build e iniciar com configuração de produção
docker compose -f docker-compose.prod.yml up --build -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Parar
docker compose -f docker-compose.prod.yml down
```

> [!WARNING]
> Em produção, use senhas fortes e nunca use as credenciais padrão do `.env.example`!

> [!TIP]
> Para deploy em nuvem (Cloud Run, ECS, etc.), considere usar secrets managers como Google Secret Manager ou AWS Secrets Manager ao invés de arquivos `.env`.

### Troubleshooting

### Banco de Dados

A aplicação usa PostgreSQL rodando em container Docker. Os dados são persistidos em um volume Docker chamado `postgres_data`.

**Credenciais padrão (desenvolvimento):**
- Host: `postgres:5432`
- Usuário: `postgres`
- Senha: `postgres`
- Database: `consultancy_pricing`

> [!CAUTION]
> Altere as credenciais padrão antes de fazer deploy em produção!

Para alterar as credenciais, edite as variáveis de ambiente em `docker-compose.yml`.

### Troubleshooting

**Porta 8080 já está em uso:**
```bash
# Encontrar o processo usando a porta
lsof -i :8080
# Ou alterar a porta no docker-compose.yml (ex: "8081:8080")
```

**Erro de conexão com PostgreSQL:**
```bash
# Verificar se o container do PostgreSQL está rodando
docker-compose ps

# Ver logs do PostgreSQL
docker-compose logs postgres
```

**Rebuild forçado:**
```bash
docker-compose down -v  # Remove volumes também
docker-compose build --no-cache
docker-compose up
```

**Resetar banco de dados:**
```bash
docker-compose down -v  # Remove volumes (apaga dados!)
docker-compose up --build
```

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato através do repositório do projeto.

---

**Desenvolvido com ❤️ usando FastAPI e Material Design 3**
