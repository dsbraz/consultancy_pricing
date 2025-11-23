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
- **Docker**: Containerização para desenvolvimento e produção
- **PostgreSQL**: Banco de dados relacional (local e produção)
- **Python 3.12**: Linguagem de programação
- **Google Cloud Run**: Hosting serverless para produção
- **Supabase**: PostgreSQL gerenciado para produção

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

### Desenvolvimento Local

**Pré-requisitos:**
- Docker Desktop instalado e em execução
- Git

**Passos:**

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd consultancy_pricing
```

2. Inicie o ambiente de desenvolvimento:
```bash
docker-compose up --build
```

3. Acesse a aplicação:
```
http://localhost:8080/frontend/index.html
```

O ambiente inclui:
- ✅ Aplicação FastAPI rodando na porta 8080
- ✅ PostgreSQL em container (dados persistidos)
- ✅ Hot-reload automático ao editar código
- ✅ Banco de dados criado automaticamente

**Parar o ambiente:**
```bash
docker-compose down
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

### Stack de Desenvolvimento e Produção

#### **Desenvolvimento Local** (`docker-compose.yml`)
- ✅ PostgreSQL em container Docker
- ✅ Hot-reload de código (volumes montados)
- ✅ CORS permissivo (`*`)
- ✅ Logs detalhados
- ✅ Dados persistidos em volume Docker

#### **Produção** (Google Cloud Run + Supabase)
- 🚀 Aplicação serverless no Cloud Run
- 🗄️ PostgreSQL gerenciado no Supabase
- 🔒 HTTPS automático
- 📈 Auto-scaling
- 💰 ~$1-2/mês (pay-per-use)

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

**Stack Oficial:** Google Cloud Run + Supabase

> [!TIP]
> **Vantagens desta stack:**
> - 🚀 **Serverless**: Zero configuração de servidor
> - 📈 **Auto-scaling**: De 0 a 1000+ instâncias automaticamente
> - 💰 **Econômico**: ~$1-2/mês para baixo/médio tráfego
> - 🔒 **Seguro**: HTTPS automático, backups inclusos
> - ⚡ **Rápido**: Deploy em ~5 minutos

**Documentação:**
- 🚀 **[Guia completo de deployment](DEPLOYMENT.md)** - Passo a passo detalhado
- ✅ **[Checklist](DEPLOYMENT_CHECKLIST.md)** - Não esqueça nenhum passo
- 📁 **[Guia de arquivos .env](ENV_GUIDE.md)** - Configuração de variáveis

**Deploy rápido:**
```bash
# 1. Configurar Supabase (5 min)
# 2. Copiar credenciais para .env.cloudrun
cp .env.cloudrun.example .env.cloudrun
# 3. Deploy!
./deploy-cloudrun.sh
```

---

### Desenvolvimento Sem Docker (Avançado)

<details>
<summary>Se você preferir rodar sem Docker (não recomendado)</summary>

**Pré-requisitos:**
- Python 3.12
- PostgreSQL instalado localmente

**Passos:**
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar PostgreSQL local
createdb consultancy_pricing

# Configurar variáveis de ambiente
export INSTANCE_CONNECTION_NAME=localhost:5432
export DB_USER=postgres
export DB_PASS=postgres
export DB_NAME=consultancy_pricing

# Executar
uvicorn app.main:app --reload --port 8080
```

Acesse: `http://localhost:8080/frontend/index.html`

</details>

---

## 🗄️ Banco de Dados

### Desenvolvimento Local

No ambiente de desenvolvimento (`docker-compose up`), o PostgreSQL roda em um container Docker:

**Credenciais padrão:**
- Host: `postgres:5432`
- Usuário: `postgres`
- Senha: `postgres`
- Database: `consultancy_pricing`

**Dados persistidos** em volume Docker (`postgres_data`). Para resetar o banco:
```bash
docker-compose down -v  # CUIDADO: Apaga todos os dados!
docker-compose up --build
```

### Produção

Em produção, usamos **Supabase** como banco de dados PostgreSQL gerenciado:

- ✅ Backups automáticos
- ✅ Point-in-time recovery
- ✅ SSL/TLS por padrão
- ✅ Connection pooling (PgBouncer)
- ✅ Monitoramento integrado
- ✅ Plano gratuito: 500MB

Veja o [Guia de Deployment](DEPLOYMENT.md) para configuração completa.

## 🔐 Segurança

O sistema implementa proteção contra XSS (Cross-Site Scripting) através de sanitização de inputs no frontend, garantindo que scripts maliciosos não sejam executados.

**Práticas de segurança implementadas:**
- ✅ Sanitização de inputs no frontend
- ✅ Validação de dados com Pydantic
- ✅ CORS configurável
- ✅ Ambiente de variáveis não versionadas
- ✅ SSL/TLS em produção (Cloud Run + Supabase)

## ❤️‍🩹 Monitoramento

**Porta 8080 já está em uso:**
```bash
# Encontrar o processo usando a porta
lsof -i :8080

# Ou alterar a porta no docker-compose.yml
# Mude de "8080:8080" para "8081:8080"
```

**Erro de conexão com PostgreSQL:**
```bash
# Verificar se o container do PostgreSQL está rodando
docker-compose ps

# Ver logs do PostgreSQL
docker-compose logs postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

**Rebuild forçado (resolve maioria dos problemas):**
```bash
docker-compose down -v  # Remove containers e volumes
docker-compose build --no-cache  # Build do zero
docker-compose up  # Iniciar novamente
```

**Resetar banco de dados (APAGA TODOS OS DADOS):**
```bash
docker-compose down -v
docker-compose up --build
```

**Ver logs em tempo real:**
```bash
# Todos os logs
docker-compose logs -f

# Apenas da aplicação
docker-compose logs -f app
```

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato através do repositório do projeto.

---

**Desenvolvido com ❤️ usando FastAPI e Material Design 3**
