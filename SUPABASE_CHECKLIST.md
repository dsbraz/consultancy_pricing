# ✅ Checklist de Deploy com Supabase

## 🔧 Configuração do Supabase

- [ ] Criar conta no [Supabase](https://supabase.com)
- [ ] Criar novo projeto
- [ ] Anotar a senha do banco de dados
- [ ] Obter credenciais de conexão (Settings > Database > Connection String)
- [ ] Extrair informações da URI:
  - [ ] Host (db.xxxxx.supabase.co:5432)
  - [ ] Usuário (postgres)
  - [ ] Senha
  - [ ] Database (postgres)

## 📝 Configuração Local

- [ ] Copiar `.env.production.example` para `.env`
- [ ] Preencher variáveis no `.env`:
  - [ ] INSTANCE_CONNECTION_NAME
  - [ ] DB_USER
  - [ ] DB_PASS
  - [ ] DB_NAME
  - [ ] CORS_ORIGINS

## 🧪 Testes

- [ ] Testar conexão localmente:
  ```bash
  python test_supabase_connection.py
  ```
- [ ] Verificar se a conexão foi bem-sucedida
- [ ] Confirmar que não há erros de SSL

## 🚀 Deploy

- [ ] Fazer build da imagem Docker:
  ```bash
  docker-compose -f docker-compose.prod.yml build
  ```
- [ ] Iniciar a aplicação:
  ```bash
  docker-compose -f docker-compose.prod.yml up -d
  ```
- [ ] Verificar logs:
  ```bash
  docker-compose -f docker-compose.prod.yml logs -f
  ```
- [ ] Confirmar mensagens de sucesso:
  - [ ] "Database connected successfully"
  - [ ] "Tables created/updated"
  - [ ] "Application startup complete"

## ✓ Verificação

- [ ] Testar health check:
  ```bash
  curl http://localhost:8080/health
  ```
- [ ] Acessar aplicação no navegador
- [ ] Criar um profissional de teste
- [ ] Criar um projeto de teste
- [ ] Verificar se os dados foram salvos no Supabase

## 🔒 Segurança

- [ ] Revisar CORS_ORIGINS (apenas domínios necessários)
- [ ] Nunca commitar o arquivo `.env`
- [ ] Verificar que `.env` está no `.gitignore`
- [ ] Usar senha forte no Supabase
- [ ] Habilitar 2FA na conta Supabase (recomendado)

## 🌐 Produção (Opcional)

- [ ] Configurar domínio próprio
- [ ] Configurar proxy reverso (Nginx/Traefik)
- [ ] Configurar certificado SSL/TLS (Let's Encrypt)
- [ ] Configurar monitoramento
- [ ] Configurar backups automáticos (já incluído no Supabase)

## 📚 Recursos

- [Guia completo de deployment](DEPLOYMENT.md)
- [Documentação do Supabase](https://supabase.com/docs)
- [README do projeto](README.md)
