#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados Supabase antes do deployment.
Execute este script para verificar se as credenciais estão corretas.

Uso:
    python test_supabase_connection.py
"""

import os
import sys
from sqlalchemy import create_engine, text

def test_connection():
    """Testa a conexão com o Supabase usando as variáveis de ambiente."""
    
    print("🔍 Testando conexão com Supabase...\n")
    
    # Ler variáveis de ambiente
    db_host = os.environ.get("INSTANCE_CONNECTION_NAME")
    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASS")
    db_name = os.environ.get("DB_NAME", "postgres")
    
    # Validar variáveis obrigatórias
    if not all([db_host, db_user, db_pass, db_name]):
        print("❌ Erro: Variáveis de ambiente não configuradas!")
        print("\nConfigure as seguintes variáveis:")
        print("  - INSTANCE_CONNECTION_NAME (ex: db.xxxxx.supabase.co:5432)")
        print("  - DB_USER (padrão: postgres)")
        print("  - DB_PASS (sua senha do Supabase)")
        print("  - DB_NAME (padrão: postgres)")
        print("\nVocê pode:")
        print("  1. Criar um arquivo .env com as variáveis")
        print("  2. Exportar as variáveis: export INSTANCE_CONNECTION_NAME=...")
        print("  3. Executar: DB_USER=... DB_PASS=... python test_supabase_connection.py")
        return False
    
    print(f"📊 Configuração:")
    print(f"  Host: {db_host}")
    print(f"  User: {db_user}")
    print(f"  Database: {db_name}")
    print(f"  Password: {'*' * len(db_pass)}\n")
    
    # Construir URL de conexão
    connection_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}"
    
    try:
        print("🔌 Tentando conectar...")
        engine = create_engine(connection_url, connect_args={"connect_timeout": 10})
        
        # Testar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            
            print("✅ Conexão bem-sucedida!\n")
            print(f"📦 Versão do PostgreSQL:")
            print(f"  {version}\n")
            
            # Listar tabelas existentes
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename;
            """))
            tables = result.fetchall()
            
            if tables:
                print("📋 Tabelas existentes:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("ℹ️  Nenhuma tabela encontrada (banco novo)")
                print("   As tabelas serão criadas automaticamente no primeiro deploy")
            
            print("\n✨ Tudo pronto para o deploy!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {str(e)}\n")
        print("💡 Verifique:")
        print("  1. As credenciais estão corretas?")
        print("  2. O projeto Supabase está ativo?")
        print("  3. Você copiou o host correto (db.xxxxx.supabase.co:5432)?")
        print("  4. A senha foi copiada corretamente?")
        print("\n🔗 Onde encontrar as credenciais:")
        print("  1. Acesse https://app.supabase.com")
        print("  2. Selecione seu projeto")
        print("  3. Vá em Settings > Database")
        print("  4. Procure por 'Connection string' > 'URI'")
        return False

if __name__ == "__main__":
    # Tentar carregar .env se existir
    try:
        from dotenv import load_dotenv
        if os.path.exists(".env"):
            load_dotenv()
            print("📄 Arquivo .env carregado\n")
    except ImportError:
        pass
    
    success = test_connection()
    sys.exit(0 if success else 1)
