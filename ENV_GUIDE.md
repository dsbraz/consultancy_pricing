# 📁 Guia de Arquivos .env

Este projeto possui **3 arquivos `.env.example`** diferentes, cada um para um cenário específico de deployment:

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

### 2. **`.env.supabase.example`**
**Uso:** Produção em servidor próprio (VPS, EC2, etc.) com Supabase

```bash
cp .env.supabase.example .env
# Editar .env com credenciais do Supabase
docker-compose -f docker-compose.prod.yml up -d
```

**Características:**
- ✅ Supabase como banco de dados PostgreSQL
- ✅ Deploy em servidor genérico com Docker
- ✅ CORS configurável para domínios específicos
- ✅ Conexão SSL automática

**Quando usar:** 
- Deploy em servidor próprio (DigitalOcean, AWS EC2, Linode, etc.)
- Executando com `docker-compose.prod.yml`

**Documentação:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

### 3. **`.env.cloudrun.example`**
**Uso:** Google Cloud Run com Supabase

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

**Documentação:** [CLOUDRUN_DEPLOYMENT.md](CLOUDRUN_DEPLOYMENT.md)

---

## 🎯 Qual arquivo usar?

| Cenário | Arquivo | Comando |
|---------|---------|---------|
| **Desenvolvimento no seu PC** | `.env.example` | `docker-compose up` |
| **VPS/Servidor próprio + Supabase** | `.env.supabase.example` | `docker-compose -f docker-compose.prod.yml up` |
| **Google Cloud Run + Supabase** | `.env.cloudrun.example` | `./deploy-cloudrun.sh` |

## 🔒 Segurança

**NUNCA commite arquivos `.env` com credenciais reais!**

Os seguintes arquivos estão no `.gitignore`:
- ✅ `.env`
- ✅ `.env.supabase`
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
| `CORS_ORIGINS` | Domínios permitidos (CORS) | `https://seuapp.com` |

## 🆘 Ajuda

Se tiver dúvidas sobre qual arquivo usar, veja:
- [README.md](README.md) - Visão geral do projeto
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy com Supabase em servidor próprio
- [CLOUDRUN_DEPLOYMENT.md](CLOUDRUN_DEPLOYMENT.md) - Deploy no Google Cloud Run
