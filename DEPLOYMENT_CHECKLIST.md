# ✅ Checklist de Deploy em Produção

## 📦 Configuração do Supabase

- [ ] Criar conta no [Supabase](https://supabase.com)
- [ ] Criar novo projeto (escolher região próxima)
- [ ] Anotar senha do banco de dados
- [ ] Ir em Settings > Database > Connection string > URI
- [ ] Copiar e extrair da URI:
  - [ ] Host: `db.xxxxx.supabase.co:5432`
  - [ ] User: `postgres`
  - [ ] Password: (sua senha)
  - [ ] Database: `postgres`

## ☁️ Configuração do Google Cloud

- [ ] Criar conta no [Google Cloud](https://cloud.google.com)
- [ ] Ativar faturamento (crédito gratuito de $300)
- [ ] Criar projeto ou usar existente
- [ ] Instalar Google Cloud SDK:
  ```bash
  # macOS
  brew install google-cloud-sdk
  
  # Ou baixar em: https://cloud.google.com/sdk/docs/install
  ```
- [ ] Fazer login:
  ```bash
  gcloud auth login
  ```
- [ ] Configurar projeto:
  ```bash
  gcloud config set project SEU-PROJETO-ID
  ```
- [ ] Configurar região (Brasil = southamerica-east1):
  ```bash
  gcloud config set run/region southamerica-east1
  ```

## 🔧 Preparação Local

- [ ] Copiar arquivo de exemplo:
  ```bash
  cp .env.cloudrun.example .env.cloudrun
  ```
- [ ] Editar `.env.cloudrun` com suas credenciais:
  - [ ] INSTANCE_CONNECTION_NAME
  - [ ] DB_USER
  - [ ] DB_PASS
  - [ ] DB_NAME
- [ ] Testar conexão com Supabase (opcional):
  ```bash
  python test_supabase_connection.py
  ```

## 🚀 Deploy

- [ ] Executar script de deploy:
  ```bash
  ./deploy-cloudrun.sh
  ```
  
  Ou manualmente:
  ```bash
  gcloud run deploy consultancy-pricing \
    --source . \
    --region $(gcloud config get-value run/region) \
    --allow-unauthenticated \
    --set-env-vars "$(cat .env.cloudrun | grep -v '^#' | tr '\n' ',')"
  ```

- [ ] Aguardar build e deploy (~3-5 minutos)
- [ ] Anotar URL fornecida (ex: `https://consultancy-pricing-xxxx.run.app`)

## ✓ Verificação

- [ ] Testar health check:
  ```bash
  curl https://sua-url.run.app/health
  ```
- [ ] Abrir aplicação no navegador:
  ```
  https://sua-url.run.app/frontend/index.html
  ```
- [ ] Criar um profissional de teste
- [ ] Criar um projeto de teste
- [ ] Verificar dados no Supabase:
  - Ir em Table Editor
  - Ver tabelas criadas automaticamente
  - Confirmar que os dados foram salvos

## 🔒 Pós-Deploy: Segurança

- [ ] Atualizar CORS para usar apenas a URL do Cloud Run:
  ```bash
  gcloud run services update consultancy-pricing \
    --update-env-vars "CORS_ORIGINS=https://sua-url.run.app"
  ```
- [ ] Considerar usar Google Secret Manager para senhas
- [ ] Habilitar 2FA na conta Google
- [ ] Habilitar 2FA na conta Supabase
- [ ] Verificar que `.env.cloudrun` está no `.gitignore`

## 📊 Monitoramento (Opcional)

- [ ] Ver logs em tempo real:
  ```bash
  gcloud run services logs tail consultancy-pricing
  ```
- [ ] Acessar [Cloud Console](https://console.cloud.google.com/run)
- [ ] Configurar alertas no Cloud Monitoring
- [ ] Verificar métricas no dashboard do Supabase

## 🌐 Domínio Personalizado (Opcional)

- [ ] Ir em Cloud Console > Cloud Run > seu serviço
- [ ] Clicar em "Manage Custom Domains"
- [ ] Adicionar seu domínio
- [ ] Configurar DNS conforme instruído
- [ ] Atualizar CORS com novo domínio

## 💡 Comandos Úteis

Ver informações do serviço:
```bash
gcloud run services describe consultancy-pricing
```

Ver URL do serviço:
```bash
gcloud run services describe consultancy-pricing \
  --format 'value(status.url)'
```

Atualizar variáveis de ambiente:
```bash
gcloud run services update consultancy-pricing \
  --update-env-vars "KEY=VALUE"
```

Ver logs:
```bash
gcloud run services logs tail consultancy-pricing
```

## 📚 Documentação

- 📖 [Guia completo de deployment](CLOUDRUN_DEPLOYMENT.md)
- 🔧 [Configuração do Supabase](DEPLOYMENT.md)
- 📘 [README do projeto](README.md)

## 💰 Custos Esperados

- **Cloud Run**: ~$1-2/mês para baixo tráfego (free tier generoso)
- **Supabase**: Gratuito até 500MB
- **Total**: Praticamente gratuito para desenvolvimento/pequenos projetos! 🎉
