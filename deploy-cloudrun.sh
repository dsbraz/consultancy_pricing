#!/bin/bash

###############################################################################
# Deploy Script for Google Cloud Run
# 
# Este script automatiza o deploy da aplicação Consultancy Pricing no
# Google Cloud Run usando Supabase como banco de dados.
#
# Uso:
#   ./deploy-cloudrun.sh
#
# Pré-requisitos:
#   - Google Cloud SDK instalado e configurado (gcloud)
#   - Arquivo .env.cloudrun com as variáveis de ambiente
###############################################################################

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"
}

###############################################################################
# Configuração
###############################################################################

SERVICE_NAME="consultancy-pricing"
ENV_FILE=".env.cloudrun"

print_header "🚀 Deploy para Google Cloud Run"

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK não está instalado!"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

print_success "Google Cloud SDK encontrado"

# Verificar autenticação
print_info "Verificando autenticação..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    print_error "Você não está autenticado no Google Cloud"
    print_info "Execute: gcloud auth login"
    exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
print_success "Autenticado como: $ACTIVE_ACCOUNT"

# Verificar projeto configurado
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    print_error "Nenhum projeto Google Cloud configurado"
    print_info "Execute: gcloud config set project SEU-PROJETO-ID"
    exit 1
fi

print_success "Projeto: $PROJECT_ID"

# Verificar região configurada
REGION=$(gcloud config get-value run/region 2>/dev/null)
if [ -z "$REGION" ]; then
    print_warning "Nenhuma região configurada, usando us-central1"
    REGION="us-central1"
    gcloud config set run/region $REGION
else
    print_success "Região: $REGION"
fi

# Carregar variáveis de ambiente
if [ ! -f "$ENV_FILE" ]; then
    print_error "Arquivo $ENV_FILE não encontrado!"
    print_info "Crie o arquivo com as variáveis de ambiente necessárias"
    print_info "Veja CLOUDRUN_DEPLOYMENT.md para instruções"
    exit 1
fi

print_success "Arquivo de configuração encontrado"

# Ler variáveis do arquivo
print_info "Carregando variáveis de ambiente..."
export $(cat $ENV_FILE | grep -v '^#' | xargs)

# Validar variáveis obrigatórias
REQUIRED_VARS=("INSTANCE_CONNECTION_NAME" "DB_USER" "DB_PASS" "DB_NAME")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Variável $var não está definida em $ENV_FILE"
        exit 1
    fi
done

print_success "Todas as variáveis obrigatórias estão definidas"

###############################################################################
# Confirmar deploy
###############################################################################

print_header "📋 Resumo do Deploy"
echo "Serviço:      $SERVICE_NAME"
echo "Projeto:      $PROJECT_ID"
echo "Região:       $REGION"
echo "DB Host:      $INSTANCE_CONNECTION_NAME"
echo "DB User:      $DB_USER"
echo "DB Name:      $DB_NAME"
echo ""

read -p "Continuar com o deploy? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deploy cancelado pelo usuário"
    exit 0
fi

###############################################################################
# Habilitar APIs necessárias
###############################################################################

print_header "🔧 Habilitando APIs do Google Cloud"

APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "containerregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    print_info "Habilitando $api..."
    gcloud services enable $api --project=$PROJECT_ID 2>/dev/null || true
done

print_success "APIs habilitadas"

###############################################################################
# Deploy
###############################################################################

print_header "🚀 Iniciando Deploy no Cloud Run"

print_info "Fazendo build e deploy (isso pode levar alguns minutos)..."

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "ENVIRONMENT=${ENVIRONMENT:-production}" \
    --set-env-vars "INSTANCE_CONNECTION_NAME=$INSTANCE_CONNECTION_NAME" \
    --set-env-vars "DB_USER=$DB_USER" \
    --set-env-vars "DB_PASS=$DB_PASS" \
    --set-env-vars "DB_NAME=$DB_NAME" \
    --set-env-vars "CORS_ORIGINS=${CORS_ORIGINS:-*}" \
    --port 8080 \
    --max-instances 10 \
    --min-instances 0 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300s \
    --quiet

###############################################################################
# Obter informações do deploy
###############################################################################

print_header "📊 Informações do Deploy"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)')

print_success "Deploy concluído!"
echo ""
echo "🌐 URL do serviço: $SERVICE_URL"
echo "📱 Aplicação:      $SERVICE_URL/frontend/index.html"
echo "❤️  Health check:  $SERVICE_URL/health"
echo ""

###############################################################################
# Testar health check
###############################################################################

print_info "Testando health check..."
sleep 5  # Aguardar alguns segundos

if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    print_success "Health check passou!"
    HEALTH_STATUS=$(curl -s "$SERVICE_URL/health")
    echo "Response: $HEALTH_STATUS"
else
    print_warning "Health check falhou. Verifique os logs:"
    echo "  gcloud run services logs tail $SERVICE_NAME --region $REGION"
fi

###############################################################################
# Comandos úteis
###############################################################################

print_header "📝 Comandos Úteis"

echo "Ver logs em tempo real:"
echo "  gcloud run services logs tail $SERVICE_NAME --region $REGION"
echo ""
echo "Ver informações do serviço:"
echo "  gcloud run services describe $SERVICE_NAME --region $REGION"
echo ""
echo "Atualizar variáveis de ambiente:"
echo "  gcloud run services update $SERVICE_NAME --update-env-vars KEY=VALUE --region $REGION"
echo ""
echo "Deletar o serviço:"
echo "  gcloud run services delete $SERVICE_NAME --region $REGION"
echo ""

print_success "Deploy finalizado com sucesso! 🎉"
