# Sistema de Precificação de Consultoria

Sistema web para gerenciamento e precificação de projetos de consultoria, com alocação semanal de profissionais e cálculo automático de custos e margens.

## ✨ Funcionalidades

- 👥 **Gestão de Profissionais**: Cadastro com cargo, nível e custo horário
- 📋 **Ofertas de Equipe**: Templates pré-configurados de equipes
- 📊 **Projetos**: Alocação semanal automática considerando feriados brasileiros
- 💰 **Cálculos Financeiros**: Custos, impostos, margem e preço de venda automáticos

## 🛠️ Stack Tecnológica

**Backend:** FastAPI + SQLAlchemy + PostgreSQL + Pydantic  
**Frontend:** HTML5/CSS3 + JavaScript Vanilla + Material Design 3  
**Infraestrutura:**
- **Dev**: Docker + PostgreSQL em container
- **Prod**: Google Cloud Run + Supabase (~$1-2/mês)

## 🚀 Quick Start

### Desenvolvimento Local

```bash
# Clone o repositório
git clone <url>
cd consultancy_pricing

# Inicie o ambiente (Docker necessário)
docker-compose up --build

# Acesse
http://localhost:8080/frontend/index.html
```

Pronto! PostgreSQL e aplicação rodam automaticamente com hot-reload.

### Deploy em Produção

```bash
# 1. Configure Supabase (crie projeto em supabase.com)
# 2. Configure credenciais
cp .env.cloudrun.example .env.cloudrun
# Edite .env.cloudrun com suas credenciais

# 3. Deploy (Google Cloud SDK necessário)
./deploy-cloudrun.sh
```

**Documentação completa:** [DEPLOYMENT.md](DEPLOYMENT.md) | [Checklist](DEPLOYMENT_CHECKLIST.md)

## 📁 Estrutura

```
app/                 # Backend FastAPI
  ├── models/        # SQLAlchemy models
  ├── routers/       # API endpoints
  ├── schemas/       # Pydantic schemas
  └── services/      # Lógica de negócio
frontend/            # HTML + CSS + JavaScript
  ├── css/           # Estilos
  └── js/views/      # Components
```

## 🗄️ Banco de Dados

**Dev**: PostgreSQL em Docker (porta 5432, dados em volume `postgres_data`)  
**Prod**: Supabase PostgreSQL gerenciado com backups automáticos

## 🔐 Segurança

- ✅ Sanitização XSS no frontend
- ✅ Validação Pydantic no backend
- ✅ CORS configurável
- ✅ SSL/TLS em produção

## 📝 Configuração

**Arquivos de ambiente:**
- `.env.example` - Desenvolvimento local
- `.env.cloudrun.example` - Produção (Cloud Run)

Veja [ENV_GUIDE.md](ENV_GUIDE.md) para detalhes.

## 🔧 Comandos Úteis

```bash
# Ver logs
docker-compose logs -f

# Parar ambiente
docker-compose down

# Resetar banco (APAGA DADOS!)
docker-compose down -v && docker-compose up --build

# Health check
curl http://localhost:8080/health
```

## 📚 Documentação

- [DEPLOYMENT.md](DEPLOYMENT.md) - Guia completo de deploy
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Checklist passo a passo
- [ENV_GUIDE.md](ENV_GUIDE.md) - Configuração de variáveis

## 🆘 Troubleshooting

**Porta 8080 em uso?**
```bash
lsof -i :8080  # Encontrar processo
# Ou mude a porta em docker-compose.yml
```

**Erro de conexão PostgreSQL?**
```bash
docker-compose ps              # Ver status
docker-compose logs postgres   # Ver logs
docker-compose restart postgres # Reiniciar
```

**Rebuild forçado:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

---

**Desenvolvido com ❤️ usando FastAPI e Material Design 3**
