import pandas as pd
import os

def processar_e_gerar_concursos_por_rodada(arquivo_serie_a, arquivo_serie_b):
    """
    Lê os arquivos CSV dos jogos, agrupa por RODADA, sorteia 14 jogos
    e salva cada concurso da Loteca em um arquivo CSV separado.
    """
    try:
        # Carregar os dados para DataFrames do pandas
        df_a = pd.read_csv(arquivo_serie_a)
        df_b = pd.read_csv(arquivo_serie_b)
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado! Verifique se o caminho '{e.filename}' está correto.")
        return

    # Adicionar uma coluna para identificar a série
    df_a['Serie'] = 'A'
    df_b['Serie'] = 'B'

    # Combinar os dois dataframes
    df_total = pd.concat([df_a, df_b], ignore_index=True)

    # Converter a coluna 'Data' para o formato de data para poder ordenar depois
    df_total['Data_dt'] = pd.to_datetime(df_total['Data'], format='%d/%m/%Y', errors='coerce')
    df_total['Data_dt'] = df_total['Data_dt'].fillna(pd.to_datetime(df_total['Data'], format='%d/%m/%y', errors='coerce'))

    # Remover linhas que não puderam ser convertidas para data (caso haja alguma)
    df_total.dropna(subset=['Data_dt'], inplace=True)
    
    # Criar um diretório para salvar os concursos
    output_dir = "simulacao2015"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # === PRINCIPAL ALTERAÇÃO AQUI ===
    # Agrupar jogos pela coluna 'Rodada'
    for rodada, jogos_da_rodada in df_total.groupby('Rodada'):
        
        # Define a quantidade de jogos a sortear
        num_jogos_sortear = 14
        if len(jogos_da_rodada) < num_jogos_sortear:
            # Se houver menos de 14 jogos na rodada, usa todos
            jogos_sorteados = jogos_da_rodada.copy()
        else:
            # Sorteia 14 jogos aleatoriamente do grupo da rodada
            jogos_sorteados = jogos_da_rodada.sample(n=num_jogos_sortear, random_state=42) # random_state para resultados consistentes
        
        # Ordena os jogos sorteados pela data para melhor visualização
        jogos_sorteados = jogos_sorteados.sort_values('Data_dt')
        
        # Adiciona a coluna 'Jogo' numerada de 1 a 14
        jogos_sorteados.insert(0, 'Jogo', range(1, len(jogos_sorteados) + 1))
        
        # Selecionar as colunas para o arquivo final
        concurso_final = jogos_sorteados[['Jogo', 'Data', 'Time da Casa', 'Time Visitante', 'Serie', 'Rodada']]
        
        # Definir o nome do arquivo com base na rodada
        nome_arquivo = os.path.join(output_dir, f"rodada{rodada}.csv")
        
        # Salvar o concurso em um arquivo CSV
        concurso_final.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"Gerado: {nome_arquivo}")
        
    print(f"\nProcesso concluído! Os arquivos foram salvos na pasta '{output_dir}'.")

# --- Início da Execução ---
# Nomes dos arquivos de entrada (ajuste os caminhos se necessário)
arquivo_a = 'brasileiraoA/brasileiraoA2015.csv'
arquivo_b = 'brasileiraoB/brasileiraoB2015.csv'

processar_e_gerar_concursos_por_rodada(arquivo_a, arquivo_b)