import pandas as pd
import numpy as np
from collections import deque
from textwrap import shorten
from datetime import datetime, timedelta


anos = list(range(2006, 2021))  # 2006 até 2012
df_copa_brasil_list = []
df_libertadores_list = []
df_sudamericana_list = []
# ============================================================================
# 1. FUNÇÕES AUXILIARES E MOTOR DE CÁLCULO
# ============================================================================
for ano in anos:
    caminho_copa_brasil = f'dados/copadobrasil/copadobrasil{ano}.csv'
    caminho_libertadores = f'dados/libertadores/libertadores{ano}.csv'
    caminho_sudamericana = f'dados/sudamericana/sudamericana{ano}.csv'
    try:
        df_copa_brasil = pd.read_csv(caminho_copa_brasil)
        df_libertadores = pd.read_csv(caminho_libertadores)
        df_sudamericana = pd.read_csv(caminho_sudamericana)
        
        df_cb = pd.read_csv(caminho_copa_brasil)
        df_cb['Ano'] = ano
        df_copa_brasil_list.append(df_cb)
        
        df_lib = pd.read_csv(caminho_libertadores)
        df_lib['Ano'] = ano
        df_libertadores_list.append(df_lib)
        
        df_sud = pd.read_csv(caminho_sudamericana)
        df_sud['Ano'] = ano
        df_sudamericana_list.append(df_sud)
    except FileNotFoundError:
        continue

# Concatena todos os DataFrames
try:
    df_copa_brasil = pd.concat(df_copa_brasil_list, ignore_index=True)
    df_libertadores = pd.concat(df_libertadores_list, ignore_index=True)
    df_sudamericana = pd.concat(df_sudamericana_list, ignore_index=True)
    
except Exception as e:
    print(f"❌ Erro ao concatenar DataFrames: {e}")
    exit()

# --- ETAPA 2: PROCESSAMENTO DOS DADOS DE COPA ---
# --- FUNÇÃO PARA PROCESSAR JOGOS DE COPA ---
def processar_jogos_copa(df_copa, competicao):
    """Processa os jogos de copa e retorna um dicionário com informações por time"""
    jogos_por_time = {}
    
    # Verifica os nomes das colunas e ajusta conforme necessário
    coluna_mandante = None
    coluna_visitante = None
    coluna_data = None
    coluna_fase = None
    
    # Mapeia possíveis nomes de colunas
    possiveis_colunas = {
        'mandante': ['Time Mandante', 'Mandante', 'Time da Casa', 'Casa'],
        'visitante': ['Time Visitante', 'Visitante', 'Time de Fora', 'Fora'],
        'data': ['Data', 'Date', 'Dia'],
        'fase': ['Fase', 'Phase', 'Stage', 'Rodada']
    }
    
    for col in df_copa.columns:
        col_lower = col.lower()
        if any(x.lower() in col_lower for x in possiveis_colunas['mandante']):
            coluna_mandante = col
        elif any(x.lower() in col_lower for x in possiveis_colunas['visitante']):
            coluna_visitante = col
        elif any(x.lower() in col_lower for x in possiveis_colunas['data']):
            coluna_data = col
        elif any(x.lower() in col_lower for x in possiveis_colunas['fase']):
            coluna_fase = col
    
    if not all([coluna_mandante, coluna_visitante, coluna_data]):
        print(f"❌ Colunas não encontradas em {competicao}")
        return jogos_por_time
    
    for _, jogo in df_copa.iterrows():
        try:
            # Converte a data para formato datetime (tenta diferentes formatos)
            data_str = str(jogo[coluna_data])
            data_jogo = None
            
            # Tenta diferentes formatos de data
            formatos_data = ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
            for formato in formatos_data:
                try:
                    data_jogo = datetime.strptime(data_str, formato)
                    break
                except ValueError:
                    continue
            
            if data_jogo is None:
                continue
            
            # Adiciona informações para o time mandante
            mandante = str(jogo[coluna_mandante]).strip()
            if mandante and mandante != 'nan':
                if mandante not in jogos_por_time:
                    jogos_por_time[mandante] = []
                
                fase = str(jogo[coluna_fase]).strip() if coluna_fase else 'F'
                jogos_por_time[mandante].append({
                    'data': data_jogo,
                    'competicao': competicao,
                    'fase': fase,
                    'adversario': str(jogo[coluna_visitante]).strip(),
                    'local': 'casa'
                })
            
            # Adiciona informações para o time visitante
            visitante = str(jogo[coluna_visitante]).strip()
            if visitante and visitante != 'nan':
                if visitante not in jogos_por_time:
                    jogos_por_time[visitante] = []
                
                fase = str(jogo[coluna_fase]).strip() if coluna_fase else 'F'
                jogos_por_time[visitante].append({
                    'data': data_jogo,
                    'competicao': competicao,
                    'fase': fase,
                    'adversario': str(jogo[coluna_mandante]).strip(),
                    'local': 'fora'
                })
            
        except (ValueError, KeyError) as e:
            continue
    
    return jogos_por_time

# Processa os jogos de copa
jogos_copa_brasil = processar_jogos_copa(df_copa_brasil, 'Copa do Brasil')
jogos_libertadores = processar_jogos_copa(df_libertadores, 'Libertadores')
jogos_sudamericana = processar_jogos_copa(df_sudamericana, 'Sudamericana')
    
# Combina os dois dicionários
todos_jogos_copa = {}
for time in set(list(jogos_copa_brasil.keys()) + list(jogos_libertadores.keys()) + list(jogos_sudamericana.keys())):
    todos_jogos_copa[time] = (jogos_copa_brasil.get(time, []) + 
                             jogos_libertadores.get(time, []) + 
                             jogos_sudamericana.get(time, []))

# Ordena os jogos por data para cada time
for time in todos_jogos_copa:
    if todos_jogos_copa[time]:  # Verifica se há jogos
        todos_jogos_copa[time].sort(key=lambda x: x['data'])
    
# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def extrair_gols(placar):
    """Extrai gols do placar no formato 'X-Y'."""
    try:
        gols = str(placar).replace('–', '-').split('-')
        return int(gols[0]), int(gols[1])
    except:
        return 0, 0

def calcular_momentum_ia(deque_resultados):
    """Calcula momentum ponderado dos últimos resultados (V/E/D)."""
    if not deque_resultados:
        return 0
    pontos_map = {'V': 3, 'E': 1, 'D': 0}
    vals = [pontos_map.get(res, 0) for res in deque_resultados]
    pesos = range(1, len(vals) + 1)
    return sum(v * p for v, p in zip(vals, pesos)) / sum(pesos)

def calcular_desespero(pos, rd):
    """Calcula nível de desespero baseado na posição e rodada."""
    if rd < 10:
        return 0
    urgencia = 0
    if pos <= 3:
        urgencia = 1.0  # Título
    elif pos <= 8:
        urgencia = 0.7  # Libertadores
    elif pos >= 17:
        urgencia = 1.2  # Rebaixamento
    elif pos >= 14:
        urgencia = 0.5  # Alerta
    return urgencia * (rd / 38)

def get_proxima_copa(time, data_atual):
    """Retorna código da próxima partida de copa (se houver)."""
    if 'todos_jogos_copa' in globals() and time in todos_jogos_copa:
        proximos = [j for j in todos_jogos_copa[time] if j['data'] > data_atual]
        if proximos:
            prox = min(proximos, key=lambda x: x['data'])
            if (prox['data'] - data_atual).days <= 7:
                return f"{prox['competicao'][0]}{prox['fase'][0]}"
    return '-'

def calcular_soberba(tem_copa, pos_time, pos_adv, rodada):
    """Calcula risco de soberba (poupar jogadores)."""
    if tem_copa == 0:
        return 0
    
    gap_tabela = pos_adv - pos_time
    if gap_tabela > 0:
        sinal = (gap_tabela / 20) ** 2
        return sinal * (rodada / 38)
    return 0

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def gerar_features_completas(df_jogos, df_times, df_copas=None, stats_h2h=None):
    """Gera features completas para modelagem de jogos com correção de KeyError."""
    print("\n--- Integrando Sinais: Momentum, Força e Desespero ---")
    
    # Constantes
    COLUNA_MANDANTE = 'Time da Casa'
    COLUNA_VISITANTE = 'Time Visitante'
    
    if stats_h2h is None:
        stats_h2h = {}
    
    df_jogos['Data_Datetime'] = pd.to_datetime(
        df_jogos['Data'], 
        format='%d/%m/%y', 
        dayfirst=True, 
        errors='coerce'
    )
    # Mapeamento região
    
    df_jogos['Rodada'] = pd.to_numeric(df_jogos['Rodada'], errors='coerce')
    df_jogos = df_jogos.dropna(subset=['Data', 'Rodada']).copy()
    df_jogos = df_jogos[df_jogos['Rodada'].between(1, 38)].copy()
    
    # 🛡️ 1. LIMPEZA INICIAL (Evita quebras por data inválida ou jogos vazios)
    df_jogos = df_jogos.dropna(subset=['Data']).copy()
    df_jogos = df_jogos.sort_values(by='Rodada').reset_index(drop=True)
    
    df_jogos['Gols_Mandante'] = df_jogos['Placar'].apply(lambda p: extrair_gols(p)[0])
    df_jogos['Gols_Visitante'] = df_jogos['Placar'].apply(lambda p: extrair_gols(p)[1])
        
        
    # Média de gols da liga
    media_gols_liga = df_jogos['Gols_Mandante'].mean() if not df_jogos.empty else 1.2
    
    mapa_time_regiao = df_times.set_index('time')['região'].to_dict()
    
    # Times únicos
    unique_teams = pd.concat([df_jogos[COLUNA_MANDANTE], df_jogos[COLUNA_VISITANTE]]).unique()
    
    # ============================================================================
    # INICIALIZAÇÃO DE ESTRUTURAS
    # ============================================================================
    
    stats_times = {time: {
        'pontos': 0, 'jogos': 0, 'vitorias': 0, 'sg_casa': 0, 'sg_fora': 0,
        'gols_marcados_casa': 0, 'gols_sofridos_casa': 0, 'jogos_casa': 0,
        'gols_marcados_fora': 0, 'gols_sofridos_fora': 0, 'jogos_fora': 0,
        'ultimos_5_saldos_casa': deque(maxlen=5),
        'ultimos_5_saldos_fora': deque(maxlen=5),
        'ultimos_5_resultados': deque(maxlen=5)
    } for time in unique_teams}
    
    listas_features = {k: [] for k in [
        'Eh_Serie_B', 'Posicao_Mandante', 'Posicao_Visitante', 'Media_GM_Casa', 
        'Media_GS_Casa', 'Media_GM_Fora', 'Media_GS_Fora', 'Saldo_Gols_Casa_Mandante', 
        'Saldo_Gols_Fora_Visitante', 'Saldo_Ultimos_5_Casa_Mandante', 
        'Saldo_Ultimos_5_Fora_Visitante', 'Sequencia_5_Mandante', 'Sequencia_5_Visitante',
        'Momentum_M', 'Momentum_V', 'Proxima_Copa_Mandante', 'Proxima_Copa_Visitante',
        'Forca_Atk_M', 'Forca_Def_V', 'Sinal_Dominio', 'Desespero_Mandante', 
        'Desespero_Visitante', 'Delta_Desespero', 'Soberba_Mandante', 
        'Soberba_Visitante', 'Delta_Soberba','H2H_Vits_M_Casa', 'H2H_Derrotas_M_Casa', 
        'H2H_Vits_V_Fora', 'H2H_Derrotas_V_Fora', 'H2H_Empates_H2H', 'H2H_Taxa_Vits_M','H2H_Aproveitamento_M'
    ]}
    
    # ============================================================================
    # PROCESSAMENTO RODADA A RODADA
    # ============================================================================
    
    for rodada in range(1, 39):
        # Classificação atual
        df_class = pd.DataFrame.from_dict(stats_times, orient='index')
        df_class['sg_total'] = df_class['sg_casa'] + df_class['sg_fora']
        df_class = df_class.sort_values(by=['pontos', 'vitorias', 'sg_total'], ascending=False)
        df_class['posicao'] = range(1, len(df_class) + 1)
        mapa_posicao = df_class['posicao'].to_dict()
        
        jogos_da_rodada = df_jogos[df_jogos['Rodada'] == rodada]
        
        for index, jogo in jogos_da_rodada.iterrows():
            mandante = str(jogo[COLUNA_MANDANTE]).strip()
            visitante = str(jogo[COLUNA_VISITANTE]).strip()
            data_jogo = jogo['Data_Datetime']
            eh_serie_b = jogo.get('Eh_Serie_B', 1)
            
            m, v = jogo['Time da Casa'], jogo['Time Visitante']
            
            # --------------------------------------------------------------------
            # 🚀 CÁLCULO DO SENSOR H2H (Busca o passado antes deste jogo)
            # --------------------------------------------------------------------
            # Criamos a chave única para o confronto direto com mando de campo
            confronto_direto = (mandante, visitante)
            h2h = stats_h2h.get(confronto_direto, {'v_m': 0, 'v_v': 0, 'e': 0})
            
            # Preenchemos as listas com o histórico ACUMULADO até aqui
            # Após registrar, atualizamos o histórico com o resultado do jogo atual
            g_m, g_v = jogo['Gols_Mandante'], jogo['Gols_Visitante']
            if eh_serie_b == 1: 
                listas_features['H2H_Vits_M_Casa'].append(0)    # Quantas vezes M ganhou de V em casa
                listas_features['H2H_Derrotas_M_Casa'].append(0) # Quantas vezes M perdeu de V em casa
                listas_features['H2H_Vits_V_Fora'].append(0)    # Quantas vezes V ganhou de M fora
                listas_features['H2H_Derrotas_V_Fora'].append(0) # Quantas vezes V perdeu de M fora
                listas_features['H2H_Empates_H2H'].append(0)      # Quantas vezes empataram nesse mando
                listas_features['H2H_Taxa_Vits_M'].append(0.5) # 50% se nunca se enfrentaram
            
            else:
                
                listas_features['H2H_Vits_M_Casa'].append(h2h['v_m'])    # Quantas vezes M ganhou de V em casa
                listas_features['H2H_Derrotas_M_Casa'].append(h2h['v_v']) # Quantas vezes M perdeu de V em casa
                listas_features['H2H_Vits_V_Fora'].append(h2h['v_v'])    # Quantas vezes V ganhou de M fora
                listas_features['H2H_Derrotas_V_Fora'].append(h2h['v_m']) # Quantas vezes V perdeu de M fora
                listas_features['H2H_Empates_H2H'].append(h2h['e'])      # Quantas vezes empataram nesse mando
                
                if confronto_direto not in stats_h2h:
                    stats_h2h[confronto_direto] = {'v_m': 0, 'v_v': 0, 'e': 0}
                
                if g_m > g_v:
                    stats_h2h[confronto_direto]['v_m'] += 3
                elif g_v > g_m:
                    stats_h2h[confronto_direto]['v_v'] += 3
                else:
                    stats_h2h[confronto_direto]['e'] += 1
            
                # Dentro do loop de geração de features, após coletar os H2H:
                total_confrontos = h2h['v_m'] + h2h['v_v'] + h2h['e']
                if total_confrontos > 0:
                    listas_features['H2H_Taxa_Vits_M'].append(h2h['v_m'] / total_confrontos)
                else:
                    listas_features['H2H_Taxa_Vits_M'].append(0.5) # 50% se nunca se enfrentaram
            # --------------------------------------------------------------------
            
            # --- 🕒 H2H COM PESO NO TEMPO (Time-Decay) ---
            total_h2h = h2h['v_m'] + h2h['v_v'] + h2h['e']
            if total_h2h > 0:
                # Em vez de apenas contar, vamos dar peso 1.0 para jogos recentes 
                # e ir diminuindo 0.05 a cada ano de distância.
                # (Essa é uma lógica conceitual, para aplicar no loop de anos)
                # Por enquanto, vamos apenas "diluir" a confiança:
                aprov_m = (h2h['v_m'] + (h2h['e'] * 0.5)) / (total_h2h + 2) # O '+2' atua como 'Dúvida'
                listas_features['H2H_Aproveitamento_M'].append(aprov_m)
            else:
                listas_features['H2H_Aproveitamento_M'].append(0.5)
                
            # --------------------------------------------------------------------
            stats_m, stats_v = stats_times[mandante], stats_times[visitante]
            pos_m, pos_v = mapa_posicao.get(mandante, 21), mapa_posicao.get(visitante, 21)
            
            # --- 🚀 Geração de Features (Compactada para economia) ---
            listas_features['Eh_Serie_B'].append(jogo.get('Eh_Serie_B', 0))
            listas_features['Posicao_Mandante'].append(pos_m)
            listas_features['Posicao_Visitante'].append(pos_v)
            
            d_m, d_v = calcular_desespero(pos_m, rodada), calcular_desespero(pos_v, rodada)
            listas_features['Desespero_Mandante'].append(d_m)
            listas_features['Desespero_Visitante'].append(d_v)
            listas_features['Delta_Desespero'].append(d_m - d_v)
            
            mgm_c = stats_m['gols_marcados_casa'] / stats_m['jogos_casa'] if stats_m['jogos_casa'] > 0 else 0
            mgs_f = stats_v['gols_sofridos_fora'] / stats_v['jogos_fora'] if stats_v['jogos_fora'] > 0 else 0
            
            listas_features['Media_GM_Casa'].append(mgm_c)
            listas_features['Media_GS_Casa'].append(stats_m['gols_sofridos_casa'] / stats_m['jogos_casa'] if stats_m['jogos_casa'] > 0 else 0)
            listas_features['Media_GM_Fora'].append(stats_v['gols_marcados_fora'] / stats_v['jogos_fora'] if stats_v['jogos_fora'] > 0 else 0)
            listas_features['Media_GS_Fora'].append(mgs_f)
            listas_features['Saldo_Gols_Casa_Mandante'].append(stats_m['sg_casa'])
            listas_features['Saldo_Gols_Fora_Visitante'].append(stats_v['sg_fora'])
            listas_features['Saldo_Ultimos_5_Casa_Mandante'].append(sum(stats_m['ultimos_5_saldos_casa']))
            listas_features['Saldo_Ultimos_5_Fora_Visitante'].append(sum(stats_v['ultimos_5_saldos_fora']))
            listas_features['Sequencia_5_Mandante'].append(''.join(stats_m['ultimos_5_resultados']) or '-')
            listas_features['Sequencia_5_Visitante'].append(''.join(stats_v['ultimos_5_resultados']) or '-')
            
            listas_features['Forca_Atk_M'].append(mgm_c / media_gols_liga)
            listas_features['Forca_Def_V'].append(mgs_f / media_gols_liga)
            listas_features['Sinal_Dominio'].append((mgm_c / media_gols_liga) * (mgs_f / media_gols_liga))
            listas_features['Momentum_M'].append(calcular_momentum_ia(stats_m['ultimos_5_resultados']))
            listas_features['Momentum_V'].append(calcular_momentum_ia(stats_v['ultimos_5_resultados']))
            
            prox_c_m = get_proxima_copa(mandante, data_jogo)
            prox_c_v = get_proxima_copa(visitante, data_jogo)
            listas_features['Proxima_Copa_Mandante'].append(prox_c_m)
            listas_features['Proxima_Copa_Visitante'].append(prox_c_v)
            
            c_m = 1 if prox_c_m != '-' else 0
            c_v = 1 if prox_c_v != '-' else 0
            sob_m = calcular_soberba(c_m, pos_m, pos_v, rodada)
            sob_v = calcular_soberba(c_v, pos_v, pos_m, rodada)
            listas_features['Soberba_Mandante'].append(sob_m)
            listas_features['Soberba_Visitante'].append(sob_v)
            listas_features['Delta_Soberba'].append(sob_m - sob_v)
            
            # --- ATUALIZAÇÃO PÓS-JOGO (Mantém o estado do time) ---
            g_m, g_v = jogo['Gols_Mandante'], jogo['Gols_Visitante']
            res_m, res_v = ('V', 'D') if g_m > g_v else (('D', 'V') if g_v > g_m else ('E', 'E'))
            
            stats_m['ultimos_5_saldos_casa'].append(g_m - g_v)
            stats_m['ultimos_5_resultados'].append(res_m)
            stats_m['jogos_casa'] += 1; stats_m['gols_marcados_casa'] += g_m; stats_m['gols_sofridos_casa'] += g_v; stats_m['sg_casa'] += (g_m - g_v)
            stats_v['ultimos_5_saldos_fora'].append(g_v - g_m)
            stats_v['ultimos_5_resultados'].append(res_v)
            stats_v['jogos_fora'] += 1; stats_v['gols_marcados_fora'] += g_v; stats_v['gols_sofridos_fora'] += g_m; stats_v['sg_fora'] += (g_v - g_m)
            
            if g_m > g_v: stats_m['pontos'] += 3; stats_m['vitorias'] += 1
            elif g_v > g_m: stats_v['pontos'] += 3; stats_v['vitorias'] += 1
            else: stats_m['pontos'] += 1; stats_v['pontos'] += 1
    
    # 🛡️ 2. FINALIZAÇÃO (Sincronização Segura)
    for nome, lista in listas_features.items():
        if len(lista) == len(df_jogos):
            df_jogos[nome] = lista
        else:
            # Preenche com zeros se houver erro para não quebrar as próximas linhas
            df_jogos[nome] = [0] * len(df_jogos)
            print(f"⚠️ Alerta Crítico: Coluna {nome} desalinhada. Verifique dados brutos.")

    
    # --- FINALIZAÇÃO (Sincronização Segura) ---
    for nome, lista in listas_features.items():
        if len(lista) == len(df_jogos):
            df_jogos[nome] = lista
        else:
            df_jogos[nome] = [0] * len(df_jogos)
            print(f"⚠️ Alerta Crítico: Coluna {nome} desalinhada.")
    
    df_jogos['Diferenca_Posicao'] = df_jogos['Posicao_Mandante'] - df_jogos['Posicao_Visitante']
    df_jogos['Equilibrio_Posicao'] = (abs(df_jogos['Diferenca_Posicao']) <= 3).astype(int)
    df_jogos['Jogo_de_6_Pontos'] = (abs(df_jogos['Diferenca_Posicao']) <= 4).astype(int)
    df_jogos['Delta_Momentum'] = df_jogos['Momentum_M'] - df_jogos['Momentum_V']
    df_jogos['Soma_Forca_Atk_Def'] = df_jogos['Forca_Atk_M'] + df_jogos['Forca_Def_V']
    df_jogos['Produto_Forca_Atk_Def'] = df_jogos['Forca_Atk_M'] * df_jogos['Forca_Def_V']
    df_jogos['Diferenca_Forca_Atk_Def'] = abs(df_jogos['Forca_Atk_M'] - df_jogos['Forca_Def_V'])
    
    # Clássico regional
    df_jogos['É_Clássico'] = (df_jogos[COLUNA_MANDANTE].map(mapa_time_regiao) == 
                               df_jogos[COLUNA_VISITANTE].map(mapa_time_regiao)).astype(int)
    
    print(f"✅ Sucesso! DF Série {'B' if df_jogos['Eh_Serie_B'].iloc[0] == 1 else 'A'} finalizado.")
    return df_jogos


# 1. CRIAMOS A MEMÓRIA VAZIA (SÓ UMA VEZ!)
memoria_h2h = {} 
df_lista_treino = []

# 2. PERCORRENDO OS ANOS (REVEZAMENTO DE DADOS)
for ano in range(2006, 2021):
    
    # Carregue seus dados aqui (exemplo de nomes de arquivos)
    df_a = pd.read_csv(f'dados/brasileiraoA/brasileiraoA{ano}.csv')
    df_b = pd.read_csv(f'dados/brasileiraoB/brasileiraoB{ano}.csv')
    df_t = pd.read_csv(f'dados/times/times{ano}.csv')
    
    # Marcando as séries
    df_a['Eh_Serie_B'] = 0
    df_b['Eh_Serie_B'] = 1
    
    # 🧠 O PULO DO GATO: Passamos a 'memoria_h2h' para a função.
    # Ela vai ler o que já tem lá (anos anteriores) e SALVAR o que acontecer agora.
    df_a_enriq = gerar_features_completas(df_a, df_t, stats_h2h=memoria_h2h)
    df_b_enriq = gerar_features_completas(df_b, df_t, stats_h2h=memoria_h2h)
    
    df_lista_treino.append(df_a_enriq)
    df_lista_treino.append(df_b_enriq)

# 3. UNIFICANDO TUDO EM UM SUPER BANCO DE DADOS
df_total_treino = pd.concat(df_lista_treino, ignore_index=True)

# --- PROVA REAL ---
print("\n📊 Verificação de sanidade do H2H:")
print(f"Total de vitórias acumuladas no H2H: {df_total_treino['H2H_Vits_M_Casa'].sum()}")

# ============================================================================
# 2. FUNÇÃO DE EXIBIÇÃO FORMATADA
# ============================================================================

def exibir_jogos_por_rodada(df, rodada_desejada):
    df_rodada = df[df['Rodada'] == rodada_desejada].copy()
    if df_rodada.empty: return
    
    col_config = {
            'Data': {'nome': 'Data', 'largura': 10, 'alinhamento': '^'},
            'Time da Casa': {'nome': 'Mandante', 'largura': 12, 'alinhamento': '<'},
            'Time Visitante': {'nome': 'Visitante', 'largura': 12, 'alinhamento': '<'},
            'Placar': {'nome': 'Placar', 'largura': 7, 'alinhamento': '^'},
            
            # --- TABELA E FORÇA ---
            'Posicao_Mandante': {'nome': 'PosM', 'largura': 4, 'alinhamento': '>'},
            'Posicao_Visitante': {'nome': 'PosV', 'largura': 4, 'alinhamento': '>'},
            'Momentum_M': {'nome': 'MomM', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: f"{x:.1f}"},
            'Momentum_V': {'nome': 'MomV', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: f"{x:.1f}"},
            'Forca_Atk_M': {'nome': 'AtkM', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: f"{x:.1f}"},
            'Forca_Def_V': {'nome': 'DefV', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: f"{x:.1f}"},
            
            # --- PSICOLÓGICO E COPAS ---
            'Desespero_Mandante': {'nome': 'DesM', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: f"{x:.1f}"},
            'Desespero_Visitante': {'nome': 'DesV', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: f"{x:.1f}"},
            'Soberba_Mandante': {'nome': 'SobM', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: f"{x:.1f}"},
            'Soberba_Visitante': {'nome': 'SobV', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: f"{x:.1f}"},
            'Proxima_Copa_Mandante': {'nome': 'CpM', 'largura': 4, 'alinhamento': '^'},
            
            # --- HISTÓRICO (Onde a IA está focando) ---
            'H2H_Taxa_Vits_M': {'nome': 'H2H%', 'largura': 6, 'alinhamento': '^', 'formato': lambda x: f"{x:.0%}"},
            'H2H_Aproveitamento_M': {'nome': 'AproM', 'largura': 6, 'alinhamento': '^', 'formato': lambda x: f"{x:.2f}"},
            'H2H_Vits_M_Casa': {'nome': 'V_M', 'largura': 3, 'alinhamento': '>'},
            'H2H_Derrotas_M_Casa': {'nome': 'D_M', 'largura': 3, 'alinhamento': '>'},
            'H2H_Empates_H2H': {'nome': 'E', 'largura': 3, 'alinhamento': '>'},
            
            # --- CONTEXTO ---
            'Eh_Serie_B': {'nome': 'B?', 'largura': 2, 'alinhamento': '^', 'formato': lambda x: 'S' if x == 1 else 'N'},
            'É_Clássico': {'nome': 'CL', 'largura': 2, 'alinhamento': '^', 'formato': lambda x: 'S' if x == 1 else 'N'},
        }
    
    largura_total = sum(config['largura'] for config in col_config.values()) + len(col_config)
    print("\n" + "=" * largura_total)
    print(f"RODADA {rodada_desejada}".center(largura_total))
    print("=" * largura_total)
    print(" ".join([f"{c['nome']:{c['alinhamento']}{c['largura']}}" for c in col_config.values()]))
    
    for _, row in df_rodada.iterrows():
        linha = []
        for col, config in col_config.items():
            valor = row[col]
            if 'formato' in config: valor = config['formato'](valor)
            linha.append(f"{str(valor)[:config['largura']]:{config['alinhamento']}{config['largura']}}")
        print(" ".join(linha))
    print("=" * largura_total)

# ============================================================================
# 3. INTERFACE INTERATIVA
# ============================================================================


while True:
    try:
        entrada_ano = input("\n📅 Digite o ANO para carregar (ex: 2021) ou 'sair': ")
        if entrada_ano.lower() == 'sair': break
        
        ano = int(entrada_ano)
        # Carregando arquivos (Ajuste os caminhos conforme seu Linux)
        df_a = pd.read_csv(f'dados/brasileiraoA/brasileiraoA{ano}.csv')
        df_b = pd.read_csv(f'dados/brasileiraoB/brasileiraoB{ano}.csv')
        df_t = pd.read_csv(f'dados/times/times{ano}.csv')
        
        df_a['Eh_Serie_B'] = 0
        df_b['Eh_Serie_B'] = 1
        
        print(f"🔄 Processando dados de {ano}...")
        df_a_en = gerar_features_completas(df_a, df_t, stats_h2h=memoria_h2h)
        df_b_en = gerar_features_completas(df_b, df_t, stats_h2h=memoria_h2h)
        tudo = pd.concat([df_a_en, df_b_en], ignore_index=True)
        
        while True:
            r_input = input(f"\n🏟️ {ano} | Digite a Rodada (1-38) ou 'voltar' para mudar o ano: ")
            if r_input.lower() == 'voltar': break
            
            rodada = int(r_input)
            if 1 <= rodada <= 38:
                exibir_jogos_por_rodada(tudo, rodada)
            else:
                print("❌ Rodada inválida!")
                
    except FileNotFoundError:
        print(f"❌ Arquivos do ano {entrada_ano} não encontrados!")
    except Exception as e:
        print(f"⚠️ Erro: {e}")