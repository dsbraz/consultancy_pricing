# Guia de Deploy em Produção com Supabase

Este guia descreve como fazer o deploy da aplicação **Consultancy Pricing** em produção utilizando o Supabase como banco de dados PostgreSQL gerenciado.

## 📋 Pré-requisitos

- Conta no [Supabase](https://supabase.com)
- Docker e Docker Compose instalados no servidor de produção
- Domínio configurado (opcional, mas recomendado)

## 🗄️ Configuração do Supabase

### 1. Criar Projeto no Supabase

1. Acesse [https://app.supabase.com](https://app.supabase.com)
2. Clique em **"New Project"**
3. Preencha:
   - **Name**: `consultancy-pricing` (ou nome de sua escolha)
   - **Database Password**: Uma senha forte (guarde-a!)
   - **Region**: Escolha a região mais próxima dos seus usuários
4. Aguarde a criação do projeto (~2 minutos)

### 2. Obter Credenciais de Conexão

1. No dashboard do projeto, vá em **Settings** > **Database**
2. Na seção **"Connection string"**, selecione **"URI"**
3. Você verá algo como:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```

4. Extraia as informações:
   - **Host**: `db.xxxxxxxxxxxxx.supabase.co:5432`
   - **User**: `postgres`
   - **Password**: A senha que você definiu
   - **Database**: `postgres`

### 3. Configurar Políticas de Acesso (Opcional)

Por padrão, o Supabase protege as tabelas com Row Level Security (RLS). Como esta aplicação usa a própria API FastAPI para controle de acesso, recomenda-se **desabilitar o RLS** para as tabelas:

1. Vá em **Table Editor**
2. Para cada tabela criada pela aplicação, clique em **RLS** e desabilite
3. Ou execute no **SQL Editor**:
   ```sql
   ALTER TABLE professionals DISABLE ROW LEVEL SECURITY;
   ALTER TABLE projects DISABLE ROW LEVEL SECURITY;
   ALTER TABLE offer DISABLE ROW LEVEL SECURITY;
   ALTER TABLE offer_profissional DISABLE ROW LEVEL SECURITY;
   ALTER TABLE allocation DISABLE ROW LEVEL SECURITY;
   ```

## 🚀 Deploy da Aplicação

### 1. Preparar Ambiente no Servidor

Clone o repositório no servidor:
```bash
git clone <seu-repositorio>
cd consultancy_pricing
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env.supabase` baseado no exemplo:
```bash
cp .env.supabase.example .env
```

Edite o arquivo `.env` com suas credenciais:
```bash
# Configuração do Supabase
INSTANCE_CONNECTION_NAME=db.xxxxxxxxxxxxx.supabase.co:5432
DB_USER=postgres
DB_PASS=sua_senha_do_supabase
DB_NAME=postgres

# CORS - domínios permitidos (separados por vírgula)
CORS_ORIGINS=https://seudominio.com,https://www.seudominio.com
```

> **⚠️ IMPORTANTE**: Mantenha o arquivo `.env` seguro e nunca o commite no Git!

### 3. Iniciar a Aplicação

Execute o Docker Compose em modo produção:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

Verifique os logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

Você deve ver:
```
✅ Database connected successfully
✅ Tables created/updated
🚀 Application startup complete
```

### 4. Verificar Funcionamento

Teste o health check:
```bash
curl http://localhost:8080/health
```

Resposta esperada:
```json
{"status": "healthy"}
```

## 🌐 Configuração de Proxy Reverso (Nginx)

Para expor a aplicação com HTTPS, configure um proxy reverso:

### Exemplo de configuração Nginx:

```nginx
server {
    listen 80;
    server_name seudominio.com;
    
    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seudominio.com;
    
    # Certificados SSL (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/seudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com/privkey.pem;
    
    # Proxy para a aplicação
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Reload do Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Monitoramento

### Logs da Aplicação
```bash
# Ver todos os logs
docker-compose -f docker-compose.prod.yml logs -f

# Logs apenas do app
docker logs consultancy_pricing_app_prod -f
```

### Monitoramento do Supabase

No dashboard do Supabase, você pode monitorar:
- **Database** > **Reports**: Uso de CPU, memória, conexões
- **Database** > **Backups**: Backups automáticos
- **Logs**: Query logs e erros

### Health Checks

O container possui health check automático. Verifique o status:
```bash
docker ps
```

A coluna `STATUS` deve mostrar `healthy`.

## 🔄 Atualização da Aplicação

Para atualizar a aplicação:

```bash
# 1. Baixar últimas mudanças
git pull

# 2. Reconstruir a imagem
docker-compose -f docker-compose.prod.yml build

# 3. Reiniciar com zero downtime (opcional: use docker swarm ou k8s)
docker-compose -f docker-compose.prod.yml up -d
```

> **💡 Dica**: As migrações do banco rodam automaticamente no startup.

## 🔐 Segurança

### Checklist de Segurança:

- [ ] Variáveis de ambiente configuradas corretamente
- [ ] CORS limitado apenas aos domínios necessários
- [ ] Senha forte no Supabase
- [ ] SSL/HTTPS configurado
- [ ] Firewall configurado (permitir apenas portas 80/443)
- [ ] Backups automáticos do Supabase verificados
- [ ] Logs sendo monitorados

### Backup Manual (via Supabase)

O Supabase faz backups automáticos, mas você pode fazer backup manual:

1. No dashboard: **Database** > **Backups**
2. Clique em **"Create backup"**
3. Para restaurar: **Database** > **Backups** > **"Restore"**

## ❌ Troubleshooting

### Erro: "Connection refused"

**Causa**: Aplicação não consegue conectar ao Supabase

**Solução**:
1. Verifique as credenciais no `.env`
2. Teste a conexão diretamente:
   ```bash
   docker exec -it consultancy_pricing_app_prod bash
   psql "postgresql://postgres:sua_senha@db.xxxxx.supabase.co:5432/postgres"
   ```

### Erro: "SSL connection required"

**Causa**: Supabase requer SSL

**Solução**: A aplicação já está configurada para usar SSL automaticamente. Se o erro persistir, verifique se está usando `psycopg2` nas dependências.

### Container não inicia

**Solução**:
```bash
# Ver logs detalhados
docker-compose -f docker-compose.prod.yml logs app

# Reconstruir sem cache
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Recursos do Supabase

Seu banco Supabase inclui automaticamente:

- ✅ **Backups automáticos** diários
- ✅ **Point-in-time recovery** (últimos 7 dias no plano gratuito)
- ✅ **Connection pooling** via PgBouncer
- ✅ **Métricas e monitoramento** integrados
- ✅ **SSL/TLS** por padrão
- ✅ **Escalabilidade** automática

### Limites do Plano Gratuito:

- 500 MB de armazenamento no banco
- 1 GB de transferência
- 50 MB de armazenamento de arquivos
- 2 GB de largura de banda

Para produção em larga escala, considere upgradar para o plano Pro.

## 🆘 Suporte

- **Documentação Supabase**: [https://supabase.com/docs](https://supabase.com/docs)
- **Status do Supabase**: [https://status.supabase.com](https://status.supabase.com)
- **Community**: [https://github.com/supabase/supabase/discussions](https://github.com/supabase/supabase/discussions)
