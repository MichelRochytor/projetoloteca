import pandas as pd
import os

def gerar_csv_por_anos(arquivo_principal):
    print(f"📂 Abrindo arquivo: {arquivo_principal}...")
    
    # 1. Carrega o dataset completo
    try:
        df = pd.read_csv(arquivo_principal)
    except FileNotFoundError:
        print("❌ Erro: Arquivo 'campeonato-brasileiro-full.csv' não encontrado!")
        return

    # 2. Converte a coluna de data para o formato datetime do Python
    # O formato no seu CSV é dia/mês/ano (ex: 29/3/2003)
    df['data_dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    
    # Remove linhas onde a data é inválida
    df = df.dropna(subset=['data_dt'])
    
    # 3. Mapeamento de Normalização (Padronizando conforme a sua lista)
    mapa_nomes = {
        'Vasco': 'Vasco da Gama', 'Gremio': 'Grêmio', 'Goias': 'Goiás',
        'Criciuma': 'Criciúma', 'Sao Paulo': 'São Paulo', 'Vitoria': 'EC Vitória',
        'Atletico-MG': 'Atlético-MG', 'Parana': 'Paraná', 'Sao Caetano': 'São Caetano',
        'Botafogo-RJ': 'Botafogo', 'Athletico-PR': 'Athletico-PR', 'Atletico-PR': 'Athletico-PR',
        'Ceara': 'Ceará SC', 'America-MG': 'América-MG', 'Sport': 'Sport Recife'
    }

    # Pasta para salvar os anos
    output_dir = "anos_processados"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 4. Loop por cada ano presente no arquivo
    anos = sorted(df['data_dt'].dt.year.unique())
    
    print(f"📊 Anos encontrados: {anos}")

    for ano in anos:
        df_ano = df[df['data_dt'].dt.year == ano].copy()
        
        # Normaliza nomes de mandante e visitante
        df_ano['mandante'] = df_ano['mandante'].replace(mapa_nomes)
        df_ano['visitante'] = df_ano['visitante'].replace(mapa_nomes)
        
        # Cria a estrutura final que definimos
        df_final = pd.DataFrame()
        df_final['Rodada'] = df_ano['rodata']
        df_final['Data'] = df_ano['data_dt'].dt.strftime('%d/%m/%y')
        df_final['Time da Casa'] = df_ano['mandante']
        # Converte placar para o formato 3-0 (removendo o .0 se houver)
        df_final['Placar'] = df_ano['mandante_Placar'].astype(int).astype(str) + "-" + df_ano['visitante_Placar'].astype(int).astype(str)
        df_final['Time Visitante'] = df_ano['visitante']
        
        # Salva o arquivo individual
        nome_arquivo = os.path.join(output_dir, f"brasileiraoA{int(ano)}.csv")
        df_final.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        print(f"✅ Gerado: {nome_arquivo} ({len(df_final)} jogos)")

    print(f"\n🚀 Tudo pronto! Seus arquivos estão na pasta '{output_dir}'.")

# Executa o script
gerar_csv_por_anos('campeonato-brasileiro-full.csv')