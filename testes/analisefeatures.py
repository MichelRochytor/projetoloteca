import pandas as pd
import numpy as np
from textwrap import shorten

# --- ETAPA 1: CARREGAMENTO DOS ARQUIVOS ---
caminho_serie_a = 'brasileiraoA/brasileiraoA2015.csv'
caminho_serie_b = 'brasileiraoB/brasileiraoB2015.csv'
caminho_times = 'times/times2015.csv'

try:
    df_serie_a = pd.read_csv(caminho_serie_a)
    df_serie_b = pd.read_csv(caminho_serie_b)
    df_times = pd.read_csv(caminho_times)
    print("✅ Arquivos CSV carregados com sucesso!")
except FileNotFoundError as e:
    print(f"❌ Erro: Arquivo não encontrado! Verifique o caminho: {e.filename}")
    exit()

# --- ETAPA 2: FUNÇÃO PRINCIPAL DE ENGENHARIA DE FEATURES ---
def gerar_features_completas(df_jogos, df_times):
    print("\n--- Iniciando a criação completa de features para a Série A ---")
    COLUNA_MANDANTE = 'Time da Casa'
    COLUNA_VISITANTE = 'Time Visitante'
    df_jogos = df_jogos.sort_values(by='Rodada').reset_index(drop=True)
    
    def extrair_gols(placar):
        try:
            gols = str(placar).replace('–', '-').split('-')
            return int(gols[0]), int(gols[1])
        except: 
            return 0, 0
            
    df_jogos['Gols_Mandante'] = df_jogos['Placar'].apply(lambda p: extrair_gols(p)[0])
    df_jogos['Gols_Visitante'] = df_jogos['Placar'].apply(lambda p: extrair_gols(p)[1])
    
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
        'sg': 0,
        'gols_marcados_casa': 0, 
        'gols_sofridos_casa': 0,
        'jogos_casa': 0,
        'gols_marcados_fora': 0, 
        'gols_sofridos_fora': 0,
        'jogos_fora': 0
    } for time in unique_teams}
    
    listas_features = {
        'Posicao_Mandante': [], 
        'Posicao_Visitante': [],
        'Media_GM_Casa': [], 
        'Media_GS_Casa': [],
        'Media_GM_Fora': [], 
        'Media_GS_Fora': [],
        'Saldo_GM_Casa': [],
        'Saldo_GS_Casa': [],
        'Saldo_GM_Fora': [],
        'Saldo_GS_Fora': []
    }
    
    for rodada in range(1, 39):
        df_classificacao = pd.DataFrame.from_dict(stats_times, orient='index')
        df_classificacao = df_classificacao.sort_values(by=['pontos', 'vitorias', 'sg'], ascending=False)
        df_classificacao['posicao'] = range(1, len(df_classificacao) + 1)
        mapa_posicao = df_classificacao['posicao'].to_dict()
        
        jogos_da_rodada = df_jogos[df_jogos['Rodada'] == rodada]
        
        for index, jogo in jogos_da_rodada.iterrows():
            mandante = jogo[COLUNA_MANDANTE]
            visitante = jogo[COLUNA_VISITANTE]
            
            # Adiciona as features baseadas nas estatísticas até a rodada anterior
            stats_m = stats_times[mandante]
            stats_v = stats_times[visitante]
            
            listas_features['Posicao_Mandante'].append(mapa_posicao.get(mandante, 21))
            listas_features['Posicao_Visitante'].append(mapa_posicao.get(visitante, 21))
            
            # Médias por mando de campo
            listas_features['Media_GM_Casa'].append(
                stats_m['gols_marcados_casa'] / stats_m['jogos_casa'] if stats_m['jogos_casa'] > 0 else 0
            )
            listas_features['Media_GS_Casa'].append(
                stats_m['gols_sofridos_casa'] / stats_m['jogos_casa'] if stats_m['jogos_casa'] > 0 else 0
            )
            listas_features['Media_GM_Fora'].append(
                stats_v['gols_marcados_fora'] / stats_v['jogos_fora'] if stats_v['jogos_fora'] > 0 else 0
            )
            listas_features['Media_GS_Fora'].append(
                stats_v['gols_sofridos_fora'] / stats_v['jogos_fora'] if stats_v['jogos_fora'] > 0 else 0
            )
            
            # Somas (saldos) em vez de médias
            listas_features['Saldo_GM_Casa'].append(stats_m['gols_marcados_casa'])
            listas_features['Saldo_GS_Casa'].append(stats_m['gols_sofridos_casa'])
            listas_features['Saldo_GM_Fora'].append(stats_v['gols_marcados_fora'])
            listas_features['Saldo_GS_Fora'].append(stats_v['gols_sofridos_fora'])
            
            # Atualiza as estatísticas com o resultado do jogo atual
            g_m, g_v = jogo['Gols_Mandante'], jogo['Gols_Visitante']
            
            # Atualiza estatísticas do mandante
            stats_m.update({
                'jogos': stats_m['jogos'] + 1,
                'jogos_casa': stats_m['jogos_casa'] + 1,
                'gols_marcados_casa': stats_m['gols_marcados_casa'] + g_m,
                'gols_sofridos_casa': stats_m['gols_sofridos_casa'] + g_v,
                'sg': stats_m['sg'] + (g_m - g_v)
            })
            
            # Atualiza estatísticas do visitante
            stats_v.update({
                'jogos': stats_v['jogos'] + 1,
                'jogos_fora': stats_v['jogos_fora'] + 1,
                'gols_marcados_fora': stats_v['gols_marcados_fora'] + g_v,
                'gols_sofridos_fora': stats_v['gols_sofridos_fora'] + g_m,
                'sg': stats_v['sg'] + (g_v - g_m)
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
    
    # Adiciona todas as features ao DataFrame
    for nome_feature, lista_valores in listas_features.items():
        df_jogos[nome_feature] = lista_valores
    
    df_jogos['Diferenca_Posicao'] = df_jogos['Posicao_Mandante'] - df_jogos['Posicao_Visitante']
    df_jogos['Jogo_de_6_Pontos'] = (abs(df_jogos['Diferenca_Posicao']) <= 4).astype(int)
    
    print("✅ Todas as features foram calculadas e adicionadas.")
    return df_jogos

# --- ETAPA 3: FUNÇÃO PARA EXIBIR JOGOS POR RODADA ---
def exibir_jogos_por_rodada(df, rodada_desejada):
    """Exibe todos os jogos de uma rodada específica com formatação de tabela"""
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
        'É_Clássico': {'nome': 'Cláss', 'largura': 5, 'alinhamento': '^', 'formato': lambda x: 'SIM' if x == 1 else 'NAO'},
        'Jogo_de_6_Pontos': {'nome': '6Pts', 'largura': 4, 'alinhamento': '^', 'formato': lambda x: 'SIM' if x == 1 else 'NAO'},
        'Saldo_GM_Casa': {'nome': 'GM Casa', 'largura': 8, 'alinhamento': '>'},
        'Saldo_GS_Casa': {'nome': 'GS Casa', 'largura': 8, 'alinhamento': '>'},
        'Saldo_GM_Fora': {'nome': 'GM Fora', 'largura': 8, 'alinhamento': '>'},
        'Saldo_GS_Fora': {'nome': 'GS Fora', 'largura': 8, 'alinhamento': '>'},
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
    
    # Estatísticas explicativas
    if rodada_desejada == 1:
        print("\n📝 NOTA: Para a Rodada 1, as estatísticas são baseadas em dados históricos ou valores padrão,")
        print("pois não há jogos anteriores na temporada para calcular saldos.")
    
    # Exemplo específico para Vasco x Flamengo se estiver na rodada
    jogo_vasco_flamengo = df_rodada[
        (df_rodada['Time da Casa'] == 'Vasco') & 
        (df_rodada['Time Visitante'] == 'Flamengo')
    ]
    
    if not jogo_vasco_flamengo.empty:
        jogo = jogo_vasco_flamengo.iloc[0]
        print(f"\n🎯 EXEMPLO VASCO x FLAMENGO:")
        print(f"Data: {jogo['Data']}")
        print(f"Vasco (mandante): {jogo['Saldo_GM_Casa']} gols marcados em casa, {jogo['Saldo_GS_Casa']} gols sofridos em casa")
        print(f"Flamengo (visitante): {jogo['Saldo_GM_Fora']} gols marcados fora, {jogo['Saldo_GS_Fora']} gols sofridos fora")

# --- ETAPA 4: EXECUÇÃO PRINCIPAL ---
df_serie_a_enriquecido = gerar_features_completas(df_serie_a, df_times)

# Loop para consultar rodadas específicas
while True:
    try:
        rodada = input("\nDigite o número da rodada (1-38) ou 'sair' para encerrar: ")
        if rodada.lower() == 'sair':
            break
        
        rodada = int(rodada)
        if 1 <= rodada <= 38:
            exibir_jogos_por_rodada(df_serie_a_enriquecido, rodada)
        else:
            print("❌ Por favor, digite um número entre 1 e 38!")
    except ValueError:
        print("❌ Entrada inválida! Digite um número ou 'sair'.")