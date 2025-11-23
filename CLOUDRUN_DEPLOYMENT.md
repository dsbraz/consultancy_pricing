# Deploy no Google Cloud Run com Supabase

Guia completo para fazer deploy da aplicação **Consultancy Pricing** no Google Cloud Run usando Supabase como banco de dados.

## 📋 Visão Geral da Arquitetura

```
Internet
   ↓
Google Cloud Run (sua aplicação FastAPI)
   ↓
Supabase (banco de dados PostgreSQL)
```

**Vantagens:**
- ✅ **Serverless**: Escala automaticamente de 0 a milhares de instâncias
- ✅ **Pay-per-use**: Paga apenas quando recebe requisições
- ✅ **Fácil deploy**: Um comando para publicar
- ✅ **HTTPS gratuito**: SSL/TLS automático
- ✅ **Global**: CDN e edge locations do Google

## 🎯 Pré-requisitos

### 1. Conta Google Cloud

1. Crie uma conta em [cloud.google.com](https://cloud.google.com)
2. Ative a **conta de faturamento** (crédito gratuito de $300 para novos usuários)
3. Crie um novo projeto ou use um existente

### 2. Conta Supabase

1. Crie uma conta em [supabase.com](https://supabase.com)
2. Crie um novo projeto
3. Anote as credenciais de conexão

### 3. Ferramentas Locais

Instale o Google Cloud SDK:

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Baixe o instalador em [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

## 🚀 Passo a Passo

### Passo 1: Configurar Supabase

1. Acesse [app.supabase.com](https://app.supabase.com)
2. Clique em **New Project**
3. Preencha:
   - Name: `consultancy-pricing`
   - Database Password: (escolha uma senha forte)
   - Region: escolha a mais próxima (ex: `South America (São Paulo)`)

4. Aguarde a criação (~2 minutos)

5. Vá em **Settings** > **Database** > **Connection string** > **URI**

6. Copie a URI que terá este formato:
   ```
   postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```

7. Extraia as informações:
   - **Host**: `db.xxxxxxxxxxxxx.supabase.co:5432`
   - **User**: `postgres`
   - **Password**: sua senha
   - **Database**: `postgres`

### Passo 2: Configurar Google Cloud

#### 2.1. Fazer login no Google Cloud

```bash
gcloud auth login
```

Isso abrirá o navegador para você fazer login.

#### 2.2. Configurar o projeto

Liste seus projetos:
```bash
gcloud projects list
```

Defina o projeto ativo (substitua `MEU-PROJETO-ID`):
```bash
gcloud config set project MEU-PROJETO-ID
```

Ou crie um novo projeto:
```bash
gcloud projects create consultancy-pricing-prod --name="Consultancy Pricing"
gcloud config set project consultancy-pricing-prod
```

#### 2.3. Habilitar APIs necessárias

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com
```

Isso pode levar alguns minutos na primeira vez.

#### 2.4. Configurar região padrão

```bash
# Para Brasil (São Paulo)
gcloud config set run/region southamerica-east1

# Ou US (Iowa) - mais barato
# gcloud config set run/region us-central1
```

Veja todas as regiões disponíveis:
```bash
gcloud run regions list
```

### Passo 3: Preparar Variáveis de Ambiente

Crie um arquivo `.env.cloudrun` na raiz do projeto:

```bash
# Configuração do Supabase
INSTANCE_CONNECTION_NAME=db.xxxxxxxxxxxxx.supabase.co:5432
DB_USER=postgres
DB_PASS=sua_senha_do_supabase
DB_NAME=postgres

# CORS (seu domínio final do Cloud Run será gerado automaticamente)
CORS_ORIGINS=*

# Ambiente
ENVIRONMENT=production
```

> **⚠️ Importante:** Não commite este arquivo! Ele é apenas para referência local.

### Passo 4: Deploy da Aplicação

#### 4.1. Deploy com um único comando

Execute o script de deploy fornecido:

```bash
bash deploy-cloudrun.sh
```

Ou manualmente:

```bash
# Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="consultancy-pricing"
REGION=$(gcloud config get-value run/region)

# Build e deploy
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "INSTANCE_CONNECTION_NAME=db.xxxxxxxxxxxxx.supabase.co:5432" \
  --set-env-vars "DB_USER=postgres" \
  --set-env-vars "DB_PASS=sua_senha_aqui" \
  --set-env-vars "DB_NAME=postgres" \
  --set-env-vars "CORS_ORIGINS=*" \
  --port 8080 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300s
```

**O que esse comando faz:**
1. Faz build da imagem Docker
2. Envia para Google Container Registry
3. Cria/atualiza o serviço no Cloud Run
4. Configura todas as variáveis de ambiente
5. Retorna a URL pública da aplicação

#### 4.2. Aguardar o deploy

O processo leva ~3-5 minutos na primeira vez.

Você verá uma saída como:
```
Building using Dockerfile and deploying to Cloud Run service...
✓ Building and deploying... Done.
✓ Deploying new service... Done.
  https://consultancy-pricing-xxxx-uc.a.run.app
```

### Passo 5: Configurar CORS Correto

Após o primeiro deploy, você receberá a URL final (ex: `https://consultancy-pricing-xxxx-uc.a.run.app`).

Atualize o CORS para aceitar apenas esse domínio:

```bash
gcloud run services update consultancy-pricing \
  --update-env-vars "CORS_ORIGINS=https://consultancy-pricing-xxxx-uc.a.run.app" \
  --region $(gcloud config get-value run/region)
```

### Passo 6: Testar a Aplicação

```bash
# Obter a URL do serviço
SERVICE_URL=$(gcloud run services describe consultancy-pricing \
  --region $(gcloud config get-value run/region) \
  --format 'value(status.url)')

echo "Aplicação disponível em: $SERVICE_URL"

# Testar health check
curl $SERVICE_URL/health

# Abrir no navegador
open $SERVICE_URL/frontend/index.html  # macOS
# ou
xdg-open $SERVICE_URL/frontend/index.html  # Linux
```

## 🔧 Configurações Avançadas

### Usar Domínio Personalizado

1. Vá no [Console do Cloud Run](https://console.cloud.google.com/run)
2. Clique no seu serviço
3. Vá em **Manage Custom Domains**
4. Clique em **Add Mapping**
5. Selecione ou adicione seu domínio
6. Configure os registros DNS conforme instruído

### Configurar Secrets (Recomendado para Produção)

Em vez de variáveis de ambiente, use Google Secret Manager:

```bash
# Criar secret para a senha do banco
echo -n "sua_senha_do_supabase" | gcloud secrets create db-password --data-file=-

# Dar permissão ao Cloud Run para acessar o secret
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:$(gcloud config get-value project)@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy usando secret
gcloud run deploy consultancy-pricing \
  --source . \
  --set-secrets="DB_PASS=db-password:latest" \
  --set-env-vars="INSTANCE_CONNECTION_NAME=db.xxxx.supabase.co:5432,DB_USER=postgres,DB_NAME=postgres"
```

### Ajustar Recursos

```bash
# Aumentar memória e CPU
gcloud run services update consultancy-pricing \
  --memory 1Gi \
  --cpu 2 \
  --region $(gcloud config get-value run/region)

# Configurar autoscaling
gcloud run services update consultancy-pricing \
  --min-instances 0 \
  --max-instances 20 \
  --region $(gcloud config get-value run/region)
```

### Configurar Minimum Instances (reduzir cold start)

```bash
# Manter sempre 1 instância rodando
gcloud run services update consultancy-pricing \
  --min-instances 1 \
  --region $(gcloud config get-value run/region)
```

> **💡 Nota:** Isso aumenta o custo, pois você paga pela instância mesmo sem tráfego.

## 📊 Monitoramento

### Ver Logs

```bash
# Logs em tempo real
gcloud run services logs tail consultancy-pricing \
  --region $(gcloud config get-value run/region)

# Últimos 50 logs
gcloud run services logs read consultancy-pricing \
  --region $(gcloud config get-value run/region) \
  --limit 50
```

### Dashboard no Console

1. Acesse [console.cloud.google.com/run](https://console.cloud.google.com/run)
2. Clique no serviço `consultancy-pricing`
3. Veja métricas de:
   - Requisições por segundo
   - Latência
   - Uso de memória e CPU
   - Erros
   - Instâncias ativas

### Métricas Avançadas (Cloud Monitoring)

Acesse [console.cloud.google.com/monitoring](https://console.cloud.google.com/monitoring) para:
- Criar alertas
- Dashboards customizados
- Logs estruturados
- Tracing distribuído

## 💰 Custos Estimados

**Cloud Run** (pay-per-use):
- **Requests**: $0.40 por 1 milhão de requests
- **CPU Time**: $0.00002400 por vCPU-segundo
- **Memory**: $0.00000250 por GiB-segundo
- **Free tier**: 2 milhões de requests/mês

**Supabase** (plano gratuito):
- 500 MB de banco de dados
- 1 GB de transferência
- Ilimitado para desenvolvimento

**Exemplo de custo mensal:**
- 100k requests/mês
- 100ms de latência média
- 512MB de memória
- **Custo total: ~$1-2/mês** (praticamente gratuito!)

## 🔄 Atualizações Contínuas

### Deploy Manual

Após fazer alterações no código:

```bash
# Simplesmente rode o deploy novamente
bash deploy-cloudrun.sh
```

O Cloud Run fará:
1. Build da nova imagem
2. Deploy gradual (sem downtime)
3. Rollback automático se houver erros

### CI/CD com GitHub Actions

Crie `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: consultancy-pricing
          region: southamerica-east1
          source: ./
          env_vars: |
            ENVIRONMENT=production
            INSTANCE_CONNECTION_NAME=${{ secrets.DB_HOST }}
            DB_USER=postgres
            DB_NAME=postgres
          secrets: |
            DB_PASS=db-password:latest
```

## ❌ Troubleshooting

### Erro: "Permission denied"

```bash
# Verificar autenticação
gcloud auth list

# Fazer login novamente se necessário
gcloud auth login
```

### Erro: "Service not found"

```bash
# Verificar se está no projeto correto
gcloud config get-value project

# Listar serviços existentes
gcloud run services list
```

### Erro de Conexão com Supabase

```bash
# Testar conexão localmente primeiro
python test_supabase_connection.py

# Ver logs do Cloud Run
gcloud run services logs tail consultancy-pricing
```

### Container não inicia

```bash
# Testar build local
docker build -t test-image .
docker run -p 8080:8080 --env-file .env.cloudrun test-image

# Verificar se inicia sem erros
curl http://localhost:8080/health
```

### Erro 503 (Service Unavailable)

Possíveis causas:
1. Container demora muito para iniciar (timeout)
   - Solução: Aumentar `--timeout` no deploy
2. Health check falhando
   - Solução: Ver logs e verificar endpoint `/health`
3. Memória insuficiente
   - Solução: Aumentar `--memory`

## 🔐 Checklist de Segurança

- [ ] Usar Google Secret Manager para senhas
- [ ] Configurar CORS apenas para domínios específicos
- [ ] Ativar Cloud Armor (proteção DDoS)
- [ ] Habilitar 2FA na conta Google
- [ ] Usar IAM roles com menor privilégio
- [ ] Revisar logs de segurança regularmente
- [ ] Manter dependências atualizadas

## 📚 Recursos Úteis

- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Calculadora de Preços](https://cloud.google.com/products/calculator)
- [Cloud Run Quotas](https://cloud.google.com/run/quotas)
- [Supabase Docs](https://supabase.com/docs)
- [Cloud Run Samples](https://github.com/GoogleCloudPlatform/cloud-run-samples)

## 🆘 Suporte

- **Cloud Run**: [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-run)
- **Supabase**: [Discord](https://discord.supabase.com)
- **Issues**: Abra uma issue no repositório do projeto
