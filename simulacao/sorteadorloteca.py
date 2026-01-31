import pandas as pd
import os
import glob

def gerar_simulacoes_lote(ano_inicio=2006, ano_fim=2022):
    """
    Percorre os anos e gera arquivos de rodadas da Loteca para cada um.
    """
    for ano in range(ano_inicio, ano_fim + 1):
        # Caminhos dos arquivos baseados no padrão de pastas
        arquivo_a = f'dados/brasileiraoA/brasileiraoA{ano}.csv'
        arquivo_b = f'dados/brasileiraoB/brasileiraoB{ano}.csv'
        output_dir = f"simulacao/{ano}"

        # Verifica se os arquivos do ano existem antes de processar
        if not os.path.exists(arquivo_a) or not os.path.exists(arquivo_b):
            print(f"⏩ Pulando ano {ano}: Arquivos de Série A ou B não encontrados.")
            continue

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"\n📅 Processando Temporada: {ano}")
        
        # 1. Carga dos Dados
        df_a = pd.read_csv(arquivo_a)
        df_b = pd.read_csv(arquivo_b)
        df_a['Serie'] = 'A'
        df_b['Serie'] = 'B'

        # Tratamento de data para ordenação
        for df in [df_a, df_b]:
            df['Data_dt'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')

        concursos_gerados = 0

        # 2. Loop pelas 38 rodadas
        for rd in range(1, 39):
            jogos_a = df_a[df_a['Rodada'] == rd]
            jogos_b = df_b[df_b['Rodada'] == rd]

            # Tentativa de composição: Prioridade Série A + Resto Série B
            comp_a = jogos_a.copy()
            qtd_faltante = 14 - len(comp_a)
            
            # Garante que não tente sortear mais do que existe na Série B daquela rodada
            n_sorteio_b = min(qtd_faltante, len(jogos_b))
            
            if n_sorteio_b > 0:
                comp_b = jogos_b.sample(n=n_sorteio_b, random_state=rd)
                concurso_final = pd.concat([comp_a, comp_b])
            else:
                concurso_final = comp_a

            # Se ainda não deu 14 (casos de rodadas com jogos adiados)
            if len(concurso_final) < 14:
                # Pega jogos da Série B de outras rodadas para tapar o buraco
                extras = df_b[df_b['Rodada'] != rd].sample(n=14-len(concurso_final), random_state=rd)
                concurso_final = pd.concat([concurso_final, extras])

            # Ordenação Final
            concurso_final = concurso_final.sort_values(['Data_dt', 'Serie'])
            concurso_final = concurso_final.head(14) 
            
            # Limpeza e Numeração dos jogos (1 a 14)
            if 'Jogo' in concurso_final.columns:
                concurso_final = concurso_final.drop(columns=['Jogo'])
            concurso_final.insert(0, 'Jogo', range(1, 15))
            
            # 3. Salvamento
            nome_arq = os.path.join(output_dir, f"rodada{rd}.csv")
            # Mantemos as colunas originais do seu modelo
            concurso_final[['Jogo', 'Data', 'Time da Casa', 'Time Visitante', 'Serie', 'Rodada']].to_csv(
                nome_arq, index=False, encoding='utf-8-sig'
            )
            concursos_gerados += 1

        print(f"✅ Temporada {ano} finalizada: {concursos_gerados} arquivos gerados em '{output_dir}'.")

# Executar a geração total
gerar_simulacoes_lote(2006, 2022)