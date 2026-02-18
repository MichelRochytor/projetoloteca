import pandas as pd
import numpy as np
from textwrap import shorten
from collections import deque
from datetime import datetime, timedelta

# --- ETAPA 1: CARREGAMENTO DOS ARQUIVOS ---
caminho_serie_a = 'dados/brasileiraoA/brasileiraoA2013.csv'
caminho_serie_b = 'dados/brasileiraoB/brasileiraoB2013.csv'
caminho_times = 'dados/times/times2013.csv'
caminho_copa_brasil = 'dados/copadobrasil/copadobrasil2013.csv'
caminho_libertadores = 'dados/libertadores/libertadores2013.csv'
caminho_sudamericana = 'dados/sudamericana/sudamericana2013.csv'
# Carrega os arquivos principais

try:
    df_serie_a = pd.read_csv(caminho_serie_a)
    df_serie_b = pd.read_csv(caminho_serie_b)
    df_times = pd.read_csv(caminho_times)
    
    # Carrega os arquivos de copa e mostra as colunas para debug
    df_copa_brasil = pd.read_csv(caminho_copa_brasil)
    df_libertadores = pd.read_csv(caminho_libertadores)
    df_sudamericana = pd.read_csv(caminho_sudamericana)
    
    print("✅ Arquivos CSV carregados com sucesso!")
    print(f"Colunas Série A: {df_serie_a.columns.tolist()}")
    print(f"Colunas Série B: {df_serie_b.columns.tolist()}")
    print(f"Colunas Times: {df_times.columns.tolist()}")
    print(f"Colunas Copa do Brasil: {df_copa_brasil.columns.tolist()}")
    print(f"Colunas Libertadores: {df_libertadores.columns.tolist()}")
    print(f"Colunas Sudamericana: {df_sudamericana.columns.tolist()}")

except FileNotFoundError as e:
    print(f"❌ Erro: Arquivo não encontrado! Verifique o caminho: {e.filename}")
    exit()

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
    
    print(f"Processando {competicao}:")
    print(f"  Coluna Mandante: {coluna_mandante}")
    print(f"  Coluna Visitante: {coluna_visitante}")
    print(f"  Coluna Data: {coluna_data}")
    print(f"  Coluna Fase: {coluna_fase}")
    
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
for time in set(list(jogos_copa_brasil.keys()) + list(jogos_libertadores.keys())):
    todos_jogos_copa[time] = (jogos_copa_brasil.get(time, []) + 
                             jogos_libertadores.get(time, []) +
                             jogos_sudamericana.get(time, []))

# Ordena os jogos por data para cada time
for time in todos_jogos_copa:
    todos_jogos_copa[time].sort(key=lambda x: x['data'])

# Mostra estatísticas dos jogos de copa processados
print(f"\n📊 Estatísticas dos jogos de copa processados:")
print(f"Times na Copa do Brasil: {len(jogos_copa_brasil)}")
print(f"Times na Libertadores: {len(jogos_libertadores)}")
print(f"Times na Sudamericana: {len(jogos_sudamericana)}")
print(f"Times totais com jogos de copa: {len(todos_jogos_copa)}")

# --- ETAPA 2: FUNÇÃO PRINCIPAL DE ENGENHARIA DE FEATURES ---
def gerar_features_completas(df_jogos, df_times):
    print(f"\n--- Iniciando a criação completa de features para o dataframe com {len(df_jogos)} jogos ---")
    COLUNA_MANDANTE = 'Time da Casa'
    COLUNA_VISITANTE = 'Time Visitante'
    
    # Ordena por rodada
    df_jogos = df_jogos.sort_values(by='Rodada').reset_index(drop=True)
    
    def extrair_gols(placar):
        try:
            gols = str(placar).replace('–', '-').split('-')
            return int(gols[0]), int(gols[1])
        except: 
            return 0, 0
            
    df_jogos['Gols_Mandante'] = df_jogos['Placar'].apply(lambda p: extrair_gols(p)[0])
    df_jogos['Gols_Visitante'] = df_jogos['Placar'].apply(lambda p: extrair_gols(p)[1])
    
    # Converte datas para datetime
    try:
        df_jogos['Data_Datetime'] = pd.to_datetime(df_jogos['Data'], format='%d/%m/%y', errors='coerce')
    except:
        df_jogos['Data_Datetime'] = pd.to_datetime(df_jogos['Data'], errors='coerce')
    
    mapa_time_regiao = df_times.set_index('time')['região'].to_dict()
    df_jogos['Regiao_Mandante'] = df_jogos[COLUNA_MANDANTE].map(mapa_time_regiao)
    df_jogos['Regiao_Visitante'] = df_jogos[COLUNA_VISITANTE].map(mapa_time_regiao)
    df_jogos['É_Clássico'] = (df_jogos['Regiao_Mandante'] == df_jogos['Regiao_Visitante']).astype(int)
    
    unique_teams = pd.concat([df_jogos[COLUNA_MANDANTE], df_jogos[COLUNA_VISITANTE]]).unique()
    
    # Estatísticas mais detalhadas para cada time
    stats_times = {time: {
        'pontos': 0, 
        'jogos': 0, 
        'vitorias': 0, 
        'sg_casa': 0,  # Saldo de gols em casa
        'sg_fora': 0,  # Saldo de gols fora
        'gols_marcados_casa': 0, 
        'gols_sofridos_casa': 0,
        'jogos_casa': 0,
        'gols_marcados_fora': 0, 
        'gols_sofridos_fora': 0,
        'jogos_fora': 0,
        'ultimos_5_saldos_casa': deque(maxlen=5),  # Saldo dos últimos 5 jogos em casa
        'ultimos_5_saldos_fora': deque(maxlen=5),  # Saldo dos últimos 5 jogos fora
        'ultimos_5_resultados': deque(maxlen=5)  # Resultados dos últimos 5 jogos (V/E/D)
    } for time in unique_teams}
    
    # Inicializa as listas com valores None
    total_jogos = len(df_jogos)
    listas_features = {
        'Posicao_Mandante': [None] * total_jogos, 
        'Posicao_Visitante': [None] * total_jogos,
        'Media_GM_Casa': [None] * total_jogos, 
        'Media_GS_Casa': [None] * total_jogos,
        'Media_GM_Fora': [None] * total_jogos, 
        'Media_GS_Fora': [None] * total_jogos,
        'Saldo_GM_Casa': [None] * total_jogos,
        'Saldo_GS_Casa': [None] * total_jogos,
        'Saldo_GM_Fora': [None] * total_jogos,
        'Saldo_GS_Fora': [None] * total_jogos,
        'Saldo_Gols_Casa_Mandante': [None] * total_jogos,  # Saldo completo de gols em casa do mandante
        'Saldo_Gols_Fora_Visitante': [None] * total_jogos,  # Saldo completo de gols fora do visitante
        'Saldo_Ultimos_5_Casa_Mandante': [None] * total_jogos,
        'Saldo_Ultimos_5_Fora_Visitante': [None] * total_jogos,
        'Sequencia_5_Mandante': [None] * total_jogos,
        'Sequencia_5_Visitante': [None] * total_jogos,
        'Proxima_Copa_Mandante': [None] * total_jogos,  # Próximo jogo de copa do mandante
        'Proxima_Copa_Visitante': [None] * total_jogos   # Próximo jogo de copa do visitante
    }
    
    # Processa rodada por rodada
    rodadas = sorted(df_jogos['Rodada'].unique())
    indice_atual = 0
    
    for rodada_num in rodadas:
        # Calcula classificação antes desta rodada
        df_classificacao = pd.DataFrame.from_dict(stats_times, orient='index')
        # Classificação por pontos, vitórias e saldo total (casa + fora)
        df_classificacao['sg_total'] = df_classificacao['sg_casa'] + df_classificacao['sg_fora']
        df_classificacao = df_classificacao.sort_values(by=['pontos', 'vitorias', 'sg_total'], ascending=False)
        df_classificacao['posicao'] = range(1, len(df_classificacao) + 1)
        mapa_posicao = df_classificacao['posicao'].to_dict()
        
        # Pega todos os jogos desta rodada
        jogos_da_rodada = df_jogos[df_jogos['Rodada'] == rodada_num]
        
        for _, jogo in jogos_da_rodada.iterrows():
            mandante = jogo[COLUNA_MANDANTE]
            visitante = jogo[COLUNA_VISITANTE]
            data_jogo = jogo['Data_Datetime']
            
            if pd.isna(data_jogo):
                indice_atual += 1
                continue
            
            # Adiciona as features baseadas nas estatísticas até a rodada anterior
            stats_m = stats_times[mandante]
            stats_v = stats_times[visitante]
            
            listas_features['Posicao_Mandante'][indice_atual] = mapa_posicao.get(mandante, 21)
            listas_features['Posicao_Visitante'][indice_atual] = mapa_posicao.get(visitante, 21)
            
            # Médias por mando de campo
            listas_features['Media_GM_Casa'][indice_atual] = (
                stats_m['gols_marcados_casa'] / stats_m['jogos_casa'] if stats_m['jogos_casa'] > 0 else 0
            )
            listas_features['Media_GS_Casa'][indice_atual] = (
                stats_m['gols_sofridos_casa'] / stats_m['jogos_casa'] if stats_m['jogos_casa'] > 0 else 0
            )
            listas_features['Media_GM_Fora'][indice_atual] = (
                stats_v['gols_marcados_fora'] / stats_v['jogos_fora'] if stats_v['jogos_fora'] > 0 else 0
            )
            listas_features['Media_GS_Fora'][indice_atual] = (
                stats_v['gols_sofridos_fora'] / stats_v['jogos_fora'] if stats_v['jogos_fora'] > 0 else 0
            )
            
            # Somas (saldos) em vez de médias
            listas_features['Saldo_GM_Casa'][indice_atual] = stats_m['gols_marcados_casa']
            listas_features['Saldo_GS_Casa'][indice_atual] = stats_m['gols_sofridos_casa']
            listas_features['Saldo_GM_Fora'][indice_atual] = stats_v['gols_marcados_fora']
            listas_features['Saldo_GS_Fora'][indice_atual] = stats_v['gols_sofridos_fora']
            
            # Saldo completo de gols por mando
            listas_features['Saldo_Gols_Casa_Mandante'][indice_atual] = stats_m['sg_casa']
            listas_features['Saldo_Gols_Fora_Visitante'][indice_atual] = stats_v['sg_fora']
            
            # Saldo dos últimos 5 jogos em casa do mandante
            saldo_ultimos_5_casa_m = sum(stats_m['ultimos_5_saldos_casa'])
            listas_features['Saldo_Ultimos_5_Casa_Mandante'][indice_atual] = saldo_ultimos_5_casa_m
            
            # Saldo dos últimos 5 jogos fora do visitante
            saldo_ultimos_5_fora_v = sum(stats_v['ultimos_5_saldos_fora'])
            listas_features['Saldo_Ultimos_5_Fora_Visitante'][indice_atual] = saldo_ultimos_5_fora_v
            
            # Sequência dos últimos 5 resultados
            sequencia_5_m = ''.join(stats_m['ultimos_5_resultados'])
            sequencia_5_v = ''.join(stats_v['ultimos_5_resultados'])
            listas_features['Sequencia_5_Mandante'][indice_atual] = sequencia_5_m if sequencia_5_m else '-'
            listas_features['Sequencia_5_Visitante'][indice_atual] = sequencia_5_v if sequencia_5_v else '-'
            
            # Informações sobre jogos de copa
            def get_proxima_copa(time, data_atual):
                if time in todos_jogos_copa:
                    # Encontra o próximo jogo de copa após a data atual
                    proximos_jogos = [j for j in todos_jogos_copa[time] if j['data'] > data_atual]
                    if proximos_jogos:
                        proximo = min(proximos_jogos, key=lambda x: x['data'])
                        dias_para_jogo = (proximo['data'] - data_atual).days
                        if dias_para_jogo <= 7:  # Próximos 7 dias
                            competicao_char = 'L' if 'Libertadores' in proximo['competicao'] else 'C'
                            fase_char = proximo['fase'][0] if proximo['fase'] else 'F'
                            return f"{competicao_char}{fase_char}"
                return '-'
            
            listas_features['Proxima_Copa_Mandante'][indice_atual] = get_proxima_copa(mandante, data_jogo)
            listas_features['Proxima_Copa_Visitante'][indice_atual] = get_proxima_copa(visitante, data_jogo)
            
            # Atualiza as estatísticas com o resultado do jogo atual
            g_m, g_v = jogo['Gols_Mandante'], jogo['Gols_Visitante']
            
            # Determina o resultado para cada time
            resultado_m = 'V' if g_m > g_v else 'E' if g_m == g_v else 'D'
            resultado_v = 'V' if g_v > g_m else 'E' if g_v == g_m else 'D'
            
            # Calcula o saldo de gols para este jogo
            saldo_m = g_m - g_v
            saldo_v = g_v - g_m
            
            # Atualiza as listas de últimos jogos específicas por mando
            stats_m['ultimos_5_saldos_casa'].append(saldo_m)  # Mandante jogando em casa
            stats_v['ultimos_5_saldos_fora'].append(saldo_v)  # Visitante jogando fora
            
            # Atualiza a lista geral de resultados
            stats_m['ultimos_5_resultados'].append(resultado_m)
            stats_v['ultimos_5_resultados'].append(resultado_v)
            
            # Atualiza estatísticas do mandante (jogando em casa)
            stats_m.update({
                'jogos': stats_m['jogos'] + 1,
                'jogos_casa': stats_m['jogos_casa'] + 1,
                'gols_marcados_casa': stats_m['gols_marcados_casa'] + g_m,
                'gols_sofridos_casa': stats_m['gols_sofridos_casa'] + g_v,
                'sg_casa': stats_m['sg_casa'] + (g_m - g_v)
            })
            
            # Atualiza estatísticas do visitante (jogando fora)
            stats_v.update({
                'jogos': stats_v['jogos'] + 1,
                'jogos_fora': stats_v['jogos_fora'] + 1,
                'gols_marcados_fora': stats_v['gols_marcados_fora'] + g_v,
                'gols_sofridos_fora': stats_v['gols_sofridos_fora'] + g_m,
                'sg_fora': stats_v['sg_fora'] + (g_v - g_m)
            })
            
            # Atualiza pontos e vitórias
            if g_m > g_v:
                stats_m['pontos'] += 3
                stats_m['vitorias'] += 1
            elif g_v > g_m:
                stats_v['pontos'] += 3
                stats_v['vitorias'] += 1
            else:
                stats_m['pontos'] += 1
                stats_v['pontos'] += 1
            
            indice_atual += 1
    
    # Adiciona todas as features ao DataFrame
    for nome_feature, lista_valores in listas_features.items():
        df_jogos[nome_feature] = lista_valores
    
    df_jogos['Diferenca_Posicao'] = df_jogos['Posicao_Mandante'] - df_jogos['Posicao_Visitante']
    df_jogos['Jogo_de_6_Pontos'] = (abs(df_jogos['Diferenca_Posicao']) <= 4).astype(int)
    
    print(f"✅ Todas as features foram calculadas e adicionadas para {len(df_jogos)} jogos.")
    return df_jogos

# --- ETAPA 3: FUNÇÃO PARA EXIBIR JOGOS POR RODADA ---
def exibir_jogos_por_rodada(df, rodada_desejada):
    """Exibe todos os jogos de uma rodada específica with formatação de tabela"""
    df_rodada = df[df['Rodada'] == rodada_desejada].copy()
    
    if df_rodada.empty:
        print(f"\n❌ Não há jogos registrados para a Rodada {rodada_desejada}!")
        return

    print(f"\n--- JOGOS DA RODADA {rodada_desejada} ---")
    
    # Configuração das colunas para exibição
    col_config = {
        'Data': {'nome': 'Data', 'largura': 12, 'alinhamento': '^'},
        'Time da Casa': {'nome': 'Mandante', 'largura': 16, 'alinhamento': '<'},
        'Time Visitante': {'nome': 'Visitante', 'largura': 16, 'alinhamento': '<'},
        'Placar': {'nome': 'Placar', 'largura': 7, 'alinhamento': '^'},
        'Posicao_Mandante': {'nome': 'Pos(M)', 'largura': 6, 'alinhamento': '>'},
        'Posicao_Visitante': {'nome': 'Pos(V)', 'largura': 6, 'alinhamento': '>'},
        'Saldo_Gols_Casa_Mandante': {'nome': 'SGC(M)', 'largura': 7, 'alinhamento': '>'},
        'Saldo_Gols_Fora_Visitante': {'nome': 'SGF(V)', 'largura': 7, 'alinhamento': '>'},
        'Proxima_Copa_Mandante': {'nome': 'Copa(M)', 'largura': 6, 'alinhamento': '^'},
        'Proxima_Copa_Visitante': {'nome': 'Copa(V)', 'largura': 6, 'alinhamento': '^'},
        'É_Clássico': {'nome': 'Cláss', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: 'SIM' if x == 1 else 'NAO'},
        'Jogo_de_6_Pontos': {'nome': '6Pts', 'largura': 4, 'alinhamento': '^', 'formato': lambda x: 'SIM' if x == 1 else 'NAO'},
        'Saldo_Ultimos_5_Casa_Mandante': {'nome': 'S5C(M)', 'largura': 7, 'alinhamento': '>'},
        'Saldo_Ultimos_5_Fora_Visitante': {'nome': 'S5F(V)', 'largura': 7, 'alinhamento': '>'},
        'Sequencia_5_Mandante': {'nome': 'Seq5(M)', 'largura': 8, 'alinhamento': '^'},
        'Sequencia_5_Visitante': {'nome': 'Seq5(V)', 'largura': 8, 'alinhamento': '^'},
    }
    
    # Cabeçalho
    cabecalho = [f"{config['nome']:{config['alinhamento']}{config['largura']}}" for config in col_config.values()]
    separador = ["-" * config['largura'] for config in col_config.values()]
    
    largura_total = sum(config['largura'] for config in col_config.values()) + len(col_config) - 1
    
    print("=" * largura_total)
    print(f"RODADA {rodada_desejada}".center(largura_total))
    print("=" * largura_total)
    print(" ".join(cabecalho))
    print(" ".join(separador))

    # Linhas dos jogos
    for _, row in df_rodada.iterrows():
        linha = []
        for col, config in col_config.items():
            valor = row[col]
            if 'formato' in config:
                valor = config['formato'](valor)
            if isinstance(valor, str):
                # Para a coluna Data, vamos encurtar se necessário
                if col == 'Data':
                    valor = shorten(str(valor), width=config['largura'], placeholder="")
                else:
                    valor = shorten(str(valor), width=config['largura'], placeholder="..")
            linha.append(f"{str(valor):{config['alinhamento']}{config['largura']}}")
        print(" ".join(linha))
    
    print("=" * largura_total)
    
    # Legenda das novas colunas
    print("\n📊 LEGENDA:")
    print("SGC(M): Saldo completo de gols do Mandante em casa")
    print("SGF(V): Saldo completo de gols do Visitante fora")
    print("Copa(M): Próximo jogo de copa do Mandante (L=Libertadores, C=Copa Brasil)")
    print("Copa(V): Próximo jogo de copa do Visitante")
    print("S5C(M): Saldo dos últimos 5 jogos em casa do Mandante")
    print("S5F(V): Saldo dos últimos 5 jogos fora do Visitante")
    print("Seq5(M): Sequência dos últimos 5 resultados do Mandante (V=Vitória, E=Empate, D=Derrota)")
    print("Seq5(V): Sequência dos últimos 5 resultados do Visitante")
    print("   Ex: L1 = Libertadores Fase 1, CQ = Copa do Brasil Quartas, etc.")

# --- ETAPA 4: EXECUÇÃO PRINCIPAL ---
df_serie_a_enriquecido = gerar_features_completas(df_serie_a, df_times)
df_serie_b_enriquecido = gerar_features_completas(df_serie_b, df_times)
tudo = pd.concat([df_serie_a_enriquecido, df_serie_b_enriquecido], ignore_index=True)

# Loop para consultar rodadas específicas
while True:
    try:
        rodada = input("\nDigite o número da rodada (1-38) ou 'sair' para encerrar: ")
        if rodada.lower() == 'sair':
            break
        
        rodada = int(rodada)
        if 1 <= rodada <= 38:
            exibir_jogos_por_rodada(tudo, rodada)
        else:
            print("❌ Por favor, digite um número entre 1 e 38!")
    except ValueError:
        print("❌ Entrada inválida! Digite um número ou 'sair'.")

