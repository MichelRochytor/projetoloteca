import pandas as pd
import os
import glob
import re

# 1. MAPEAMENTO DE ESTADOS (Para preencher a coluna 'região' automaticamente)
MAPA_REGIOES = {
    # --- SÃO PAULO (SP) ---
    'Palmeiras': 'SP', 'Corinthians': 'SP', 'São Paulo': 'SP', 'Santos': 'SP', 
    'Bragantino': 'SP', 'Red Bull Bragantino': 'SP', 'Ponte Preta': 'SP', 
    'Guarani': 'SP', 'Ituano': 'SP', 'Mirassol': 'SP', 'Novorizontino': 'SP', 
    'Botafogo-SP': 'SP', 'Oeste': 'SP', 'Ferroviária': 'SP', 'Santo André': 'SP', 
    'Portuguesa': 'SP', 'Grêmio Barueri': 'SP', 'Grêmio Prudente': 'SP', 
    'Mogi Mirim': 'SP', 'São Caetano': 'SP', 'Guaratinguetá': 'SP', 
    'Americana': 'SP', 'Linense': 'SP', 'Marília': 'SP', 'Paulista': 'SP',
    'União Barbarense': 'SP', 'São Bernardo': 'SP', 'Água Santa': 'SP',

    # --- RIO DE JANEIRO (RJ) ---
    'Flamengo': 'RJ', 'Fluminense': 'RJ', 'Vasco': 'RJ', 'Vasco da Gama': 'RJ',
    'Botafogo': 'RJ', 'Macaé': 'RJ', 'Madureira': 'RJ', 'Duque de Caxias': 'RJ', 
    'Volta Redonda': 'RJ', 'Boavista': 'RJ', 'Nova Iguaçu': 'RJ', 'Americano': 'RJ',

    # --- MINAS GERAIS (MG) ---
    'Atlético-MG': 'MG', 'Cruzeiro': 'MG', 'América-MG': 'MG', 'Ipatinga': 'MG', 
    'Boa Esporte': 'MG', 'Ituiutaba': 'MG', 'Tombense': 'MG', 'Tupi': 'MG', 
    'Guarani-MG': 'MG', 'Villa Nova-MG': 'MG', 'Uberlândia': 'MG',

    # --- RIO GRANDE DO SUL (RS) ---
    'Internacional': 'RS', 'Grêmio': 'RS', 'Juventude': 'RS', 'Brasil-RS': 'RS', 
    'Brasil de Pelotas': 'RS', 'Caxias': 'RS', 'Ypiranga-RS': 'RS', 'Pelotas': 'RS', 
    'São José-RS': 'RS', 'Novo Hamburgo': 'RS',

    # --- PARANÁ (PR) ---
    'Athletico-PR': 'PR', 'Athletico Paranaense': 'PR', 'Coritiba': 'PR', 
    'Paraná': 'PR', 'Operário-PR': 'PR', 'Operário Ferroviário': 'PR', 
    'Londrina': 'PR', 'Maringá': 'PR', 'Cascavel': 'PR', 'J. Malucelli': 'PR',
    'Corinthians Paranaense': 'PR', 'Cianorte': 'PR',

    # --- SANTA CATARINA (SC) ---
    'Avaí': 'SC', 'Figueirense': 'SC', 'Chapecoense': 'SC', 'Criciúma': 'SC', 
    'Joinville': 'SC', 'Brusque': 'SC', 'Metropolitano': 'SC', 'Marcílio Dias': 'SC',

    # --- GOIÁS (GO) ---
    'Goiás': 'GO', 'Atlético-GO': 'GO', 'Vila Nova': 'GO', 'Itumbiara': 'GO', 
    'Anapolina': 'GO', 'CRAC': 'GO', 'Aparecidense': 'GO',

    # --- BAHIA (BA) ---
    'Bahia': 'BA', 'Vitória': 'BA', 'Vitória da Conquista': 'BA',

    # --- PERNAMBUCO (PE) ---
    'Sport': 'PE', 'Sport Recife': 'PE', 'Náutico': 'PE', 'Santa Cruz': 'PE', 
    'Salgueiro': 'PE', 'Central': 'PE',

    # --- CEARÁ (CE) ---
    'Ceará': 'CE', 'Ceará SC': 'CE', 'Fortaleza': 'CE', 'Icasa': 'CE', 
    'Guarany de Sobral': 'CE',

    # --- ALAGOAS (AL) ---
    'CRB': 'AL', 'CSA': 'AL', 'ASA': 'AL',

    # --- RIO GRANDE DO NORTE (RN) ---
    'ABC': 'RN', 'América-RN': 'RN', 'Alecrim': 'RN',

    # --- PARÁ (PA) ---
    'Paysandu': 'PA', 'Remo': 'PA', 'Águia de Marabá': 'PA',

    # --- MATO GROSSO E MATO GROSSO DO SUL (MT/MS) ---
    'Cuiabá': 'MT', 'Luverdense': 'MT', 'União Rondonópolis': 'MT', 
    'Operário-MS': 'MS', 'CENE': 'MS',

    # --- MARANHÃO (MA) ---
    'Sampaio Corrêa': 'MA', 'Sampaio Corr': 'MA', 'Moto Club': 'MA',

    # --- DISTRITO FEDERAL (DF) ---
    'Brasiliense': 'DF', 'Gama': 'DF',

    # --- AMAZONAS (AM) ---
    'Manaus': 'AM', 'Amazonas': 'AM', 'Amazonas FC': 'AM',

    # --- OUTROS ---
    'Confiança': 'SE', 'Campinense': 'PB', 'Treze': 'PB', 'Botafogo-PB': 'PB', 
    'River-PI': 'PI', 'Altos': 'PI', 'Rio Branco-AC': 'AC'
}

# 2. DICIONÁRIO DE NORMALIZAÇÃO (Corrige nomes cortados ou variações)
def normalizar_nome(nome):
    nome = str(nome).strip()
    substituicoes = {
        'Internaciona': 'Internacional', 'Sampaio Corr': 'Sampaio Corrêa',
        'Atletico-GO': 'Atlético-GO', 'Atlético-MG': 'Atlético-MG',
        'Athletico-PR': 'Athletico-PR', 'Athletico Paranaens': 'Athletico-PR',
        'Ceará SC': 'Ceará', 'Sport Recife': 'Sport', 'Vasco da Gama': 'Vasco',
        'América Mineiro': 'América-MG', 'Red Bull Bragantino': 'Bragantino',
        'Grêmio Novorizontino': 'Novorizontino', 'Cuiabá Saf': 'Cuiabá'
    }
    for curto, completo in substituicoes.items():
        if nome.startswith(curto): return completo
    return nome

# 3. LOOP PRINCIPAL DE PROCESSAMENTO
pastas = ['brasileiraoA', 'brasileiraoB', 'copadobrasil', 'libertadores', 'sudamericana']
times_por_ano = {} # Dicionário para guardar conjuntos de times: {2006: {set of teams}}

print("🚀 Iniciando saneamento dos dados...")

for pasta in pastas:
    caminho_pasta = f'dados/{pasta}'
    arquivos = glob.glob(os.path.join(caminho_pasta, '*.csv'))
    
    for arquivo in arquivos:
        # Extrai o ano do nome do arquivo (ex: brasileiraoA2020.csv -> 2020)
        ano_match = re.search(r'(\d{4})', os.path.basename(arquivo))
        if not ano_match: continue
        ano = int(ano_match.group(1))
        
        df = pd.read_csv(arquivo)
        
        # Padroniza nomes nas colunas de jogos
        df['Time da Casa'] = df['Time da Casa'].apply(normalizar_nome)
        df['Time Visitante'] = df['Time Visitante'].apply(normalizar_nome)
        
        # Salva o arquivo padronizado (sobrescreve o original para limpar a base)
        df.to_csv(arquivo, index=False)
        
        # Coleta times para a lista anual (apenas de ligas A e B para evitar inflar com times estrangeiros)
        if pasta in ['brasileiraoA', 'brasileiraoB']:
            if ano not in times_por_ano: times_por_ano[ano] = []
            
            # Identifica a série
            serie = 'A' if 'brasileiraoA' in pasta else 'B'
            
            # Adiciona mandantes e visitantes ao set do ano
            for t in df['Time da Casa'].unique():
                times_por_ano[ano].append({'time': t, 'serie': serie})
            for t in df['Time Visitante'].unique():
                times_por_ano[ano].append({'time': t, 'serie': serie})

# 4. GERAÇÃO DOS ARQUIVOS NA PASTA TIMES
print("📂 Gerando listas de times por ano...")
os.makedirs('dados/times', exist_ok=True)

for ano, lista in times_por_ano.items():
    df_ano = pd.DataFrame(lista).drop_duplicates(subset=['time'])
    
    # Adiciona a região baseada no dicionário MAPA_REGIOES
    df_ano['região'] = df_ano['time'].map(MAPA_REGIOES).fillna('OUTRO')
    
    # Reordena colunas para o formato pedido: time,região,serie
    df_ano = df_ano[['time', 'região', 'serie']]
    
    caminho_time = f'dados/times/times{ano}.csv'
    df_ano.to_csv(caminho_time, index=False)
    print(f"✅ Arquivo {caminho_time} gerado com {len(df_ano)} times.")

print("\n✨ Processo finalizado! Base de dados higienizada.")