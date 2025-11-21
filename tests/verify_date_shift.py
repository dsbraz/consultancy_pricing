#!/usr/bin/env python3
"""
Verification script for date shift functionality.
Tests that when a project's start date is edited, the allocation table dates are shifted accordingly.
"""

import requests
import datetime
import sys

BASE_URL = "http://localhost:8000"

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    if method == 'GET':
        resp = requests.get(url)
    elif method == 'POST':
        resp = requests.post(url, json=data)
    elif method == 'PUT':
        resp = requests.put(url, json=data)
    elif method == 'DELETE':
        resp = requests.delete(url)
    
    if resp.status_code not in [200, 201]:
        print(f"Error: {method} {endpoint} returned {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    
    return resp.json() if resp.text else {}

def verify_date_shift():
    print("=" * 60)
    print("VERIFICAÇÃO DE DESLOCAMENTO DE DATAS")
    print("=" * 60)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 1. Create a professional
    print("\n1. Criando profissional...")
    prof_data = {
        "name": f"Test Prof Date Shift {timestamp}",
        "role": "Developer",
        "level": "Senior",
        "hourly_cost": 100.0,
        "pid": f"SHIFT{timestamp}"
    }
    prof = make_request('POST', '/professionals/', data=prof_data)
    prof_id = prof["id"]
    print(f"   ✓ Profissional criado: ID {prof_id}")
    
    # 2. Create an offer
    print("\n2. Criando oferta...")
    offer_data = {
        "name": f"Test Offer Date Shift {timestamp}",
        "items": [
            {
                "role": "Developer",
                "level": "Senior",
                "quantity": 1,
                "allocation_percentage": 100.0,
                "professional_id": prof_id
            }
        ]
    }
    offer = make_request('POST', '/offers/', data=offer_data)
    offer_id = offer["id"]
    print(f"   ✓ Oferta criada: ID {offer_id}")
    
    # 3. Create a project with start date = today
    print("\n3. Criando projeto...")
    today = datetime.date.today()
    proj_data = {
        "name": f"Test Project Date Shift {timestamp}",
        "start_date": today.isoformat(),
        "duration_months": 3,
        "tax_rate": 11.0,
        "margin_rate": 40.0
    }
    proj = make_request('POST', '/projects/', data=proj_data)
    proj_id = proj["id"]
    print(f"   ✓ Projeto criado: ID {proj_id}")
    print(f"   ✓ Data de início: {today.isoformat()}")
    
    # 4. Apply offer to create allocations
    print("\n4. Aplicando oferta ao projeto...")
    result = make_request('POST', f'/projects/{proj_id}/apply_offer/{offer_id}', data={})
    print(f"   ✓ Oferta aplicada: {result['weeks_count']} semanas criadas")
    
    # 5. Get allocation table and verify initial dates
    print("\n5. Verificando tabela de alocação inicial...")
    table = make_request('GET', f'/projects/{proj_id}/allocation_table')
    
    initial_weeks = table['weeks']
    print(f"   ✓ Total de semanas: {len(initial_weeks)}")
    
    if len(initial_weeks) > 0:
        first_week = initial_weeks[0]
        print(f"   ✓ Primeira semana inicia em: {first_week['week_start']}")
        
    # Store initial allocation data
    initial_allocations = table['allocations']
    if len(initial_allocations) > 0:
        initial_alloc = initial_allocations[0]
        initial_weekly_hours = initial_alloc['weekly_hours']
        print(f"   ✓ Profissional alocado: {initial_alloc['professional']['name']}")
        print(f"   ✓ Semanas com alocação: {len(initial_weekly_hours)}")
        
        # Show first few weeks
        for week_num in sorted(initial_weekly_hours.keys(), key=int)[:3]:
            week_data = initial_weekly_hours[week_num]
            print(f"      Semana {week_num}: {week_data['hours_allocated']}h alocadas")
    
    # 6. Edit project to shift start date by +7 days
    print("\n6. Editando projeto: deslocando data de início +7 dias...")
    new_start_date = today + datetime.timedelta(days=7)
    update_data = {
        "start_date": new_start_date.isoformat()
    }
    make_request('PUT', f'/projects/{proj_id}', data=update_data)
    print(f"   ✓ Nova data de início: {new_start_date.isoformat()}")
    
    # 7. Get allocation table again and verify dates shifted
    print("\n7. Verificando tabela de alocação após deslocamento...")
    table_after = make_request('GET', f'/projects/{proj_id}/allocation_table')
    
    new_weeks = table_after['weeks']
    print(f"   ✓ Total de semanas: {len(new_weeks)}")
    
    if len(new_weeks) > 0:
        first_week_after = new_weeks[0]
        print(f"   ✓ Primeira semana agora inicia em: {first_week_after['week_start']}")
        
        # Verify the shift
        initial_first_week_date = datetime.date.fromisoformat(initial_weeks[0]['week_start'])
        new_first_week_date = datetime.date.fromisoformat(first_week_after['week_start'])
        actual_shift = (new_first_week_date - initial_first_week_date).days
        
        print(f"\n   📊 ANÁLISE DO DESLOCAMENTO:")
        print(f"      Deslocamento esperado: 7 dias")
        print(f"      Deslocamento real: {actual_shift} dias")
        
        if actual_shift == 7:
            print(f"      ✅ Deslocamento correto!")
        else:
            print(f"      ❌ ERRO: Deslocamento incorreto!")
            sys.exit(1)
    
    # 8. Verify hours were preserved
    print("\n8. Verificando preservação das horas alocadas...")
    new_allocations = table_after['allocations']
    
    if len(new_allocations) > 0:
        new_alloc = new_allocations[0]
        new_weekly_hours = new_alloc['weekly_hours']
        
        print(f"   ✓ Semanas com alocação após shift: {len(new_weekly_hours)}")
        
        # Compare hours for each week
        hours_preserved = True
        for week_num in sorted(initial_weekly_hours.keys(), key=int):
            if week_num in new_weekly_hours:
                initial_hours = initial_weekly_hours[week_num]['hours_allocated']
                new_hours = new_weekly_hours[week_num]['hours_allocated']
                
                if initial_hours != new_hours:
                    print(f"      ❌ Semana {week_num}: horas mudaram de {initial_hours} para {new_hours}")
                    hours_preserved = False
        
        if hours_preserved:
            print(f"      ✅ Todas as horas foram preservadas!")
        else:
            print(f"      ❌ ERRO: Algumas horas não foram preservadas!")
            sys.exit(1)
    
    # 9. Test duration change
    print("\n9. Testando mudança de duração (3 → 4 meses)...")
    update_data = {
        "duration_months": 4
    }
    make_request('PUT', f'/projects/{proj_id}', data=update_data)
    
    table_after_duration = make_request('GET', f'/projects/{proj_id}/allocation_table')
    weeks_after_duration = table_after_duration['weeks']
    
    print(f"   ✓ Total de semanas após aumento de duração: {len(weeks_after_duration)}")
    print(f"   ✓ Semanas adicionadas: {len(weeks_after_duration) - len(new_weeks)}")
    
    if len(weeks_after_duration) > len(new_weeks):
        print(f"      ✅ Novas semanas foram adicionadas!")
    else:
        print(f"      ❌ ERRO: Nenhuma semana foi adicionada!")
        sys.exit(1)
    
    # Cleanup
    print("\n10. Limpando dados de teste...")
    make_request('DELETE', f'/projects/{proj_id}')
    make_request('DELETE', f'/offers/{offer_id}')
    make_request('DELETE', f'/professionals/{prof_id}')
    print(f"   ✓ Dados removidos")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        verify_date_shift()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
