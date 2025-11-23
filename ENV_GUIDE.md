# 📁 Guia de Arquivos .env

Este projeto possui **2 arquivos `.env.example`** diferentes, cada um para um cenário específico:

## 📚 Arquivos Disponíveis

### 1. **`.env.example`** 
**Uso:** Desenvolvimento local com Docker Compose

```bash
cp .env.example .env
docker-compose up --build
```

**Características:**
- ✅ PostgreSQL em container Docker local
- ✅ CORS permissivo (`*`)
- ✅ Credenciais padrão de desenvolvimento
- ✅ Dados persistidos em volume Docker

**Quando usar:** Desenvolvimento local no seu computador

---

### 2. **`.env.cloudrun.example`**
**Uso:** Produção no Google Cloud Run com Supabase **(configuração oficial)**

```bash
cp .env.cloudrun.example .env.cloudrun
# Editar .env.cloudrun com credenciais do Supabase
./deploy-cloudrun.sh
```

**Características:**
- ✅ Otimizado para Google Cloud Run (serverless)
- ✅ Supabase como banco de dados
- ✅ CORS ajustável (usar `*` no primeiro deploy)
- ✅ Script de deploy automatizado

**Quando usar:**
- Deploy serverless no Google Cloud Run
- Aplicação escalável e pay-per-use

**Documentação:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🎯 Qual arquivo usar?

| Cenário | Arquivo | Comando |
|---------|---------|---------|
| **Desenvolvimento local** | `.env.example` | `docker-compose up` |
| **Produção (Cloud Run + Supabase)** | `.env.cloudrun.example` | `./deploy-cloudrun.sh` |

## 🔒 Segurança

**NUNCA commite arquivos `.env` com credenciais reais!**

Os seguintes arquivos estão no `.gitignore`:
- ✅ `.env`
- ✅ `.env.cloudrun`

Apenas os arquivos `.example` são versionados no Git.

## 📖 Variáveis de Ambiente

Todas as configurações usam as mesmas variáveis:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `ENVIRONMENT` | Ambiente (development/production) | `production` |
| `INSTANCE_CONNECTION_NAME` | Host do banco de dados | `db.xxxxx.supabase.co:5432` |
| `DB_USER` | Usuário do banco | `postgres` |
| `DB_PASS` | Senha do banco | `sua_senha_segura` |
| `DB_NAME` | Nome do banco | `postgres` |
| `CORS_ORIGINS` | Domínios permitidos (CORS) | `https://seuapp.com` ou `*` |

## 🆘 Ajuda

Se tiver dúvidas sobre configuração:
- [README.md](README.md) - Visão geral do projeto
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guia completo de deployment
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Checklist passo a passo
