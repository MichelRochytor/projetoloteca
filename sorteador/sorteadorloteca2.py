import pandas as pd
import os

def gerar_38_concursos_loteca(arquivo_a, arquivo_b, output_dir="simulacao2016"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Carga dos Dados
    df_a = pd.read_csv(arquivo_a)
    df_b = pd.read_csv(arquivo_b)
    df_a['Serie'] = 'A'
    df_b['Serie'] = 'B'

    # Tratamento de data padrão
    for df in [df_a, df_b]:
        df['Data_dt'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')

    concursos_gerados = 0

    # 2. Loop por cada uma das 38 rodadas
    for rd in range(1, 39):
        # Pegamos todos os jogos da rodada X na Série A e na Série B
        jogos_a = df_a[df_a['Rodada'] == rd]
        jogos_b = df_b[df_b['Rodada'] == rd]

        # Verificamos se há jogos suficientes (Mínimo 14 no total)
        if len(jogos_a) + len(jogos_b) >= 14:
            # Simulação Realista:
            # Pegamos os 10 jogos da Série A (o "filé" da Loteca)
            # E sorteamos 4 jogos da Série B para completar os 14
            
            # Se a Série A tiver menos de 10 (jogos adiados), pegamos o que tiver
            comp_a = jogos_a.copy()
            qtd_faltante = 14 - len(comp_a)
            
            # Sorteamos o restante da Série B
            comp_b = jogos_b.sample(n=min(qtd_faltante, len(jogos_b)), random_state=rd)
            
            concurso_final = pd.concat([comp_a, comp_b])
            
            # Se mesmo assim não deu 14 (casos raros de rodadas incompletas), 
            # pegamos jogos da rodada anterior/próxima para não quebrar o arquivo
            if len(concurso_final) < 14:
                extras = df_b[df_b['Rodada'] != rd].sample(n=14-len(concurso_final), random_state=rd)
                concurso_final = pd.concat([concurso_final, extras])

            # Ordenação e Formatação
            concurso_final = concurso_final.sort_values(['Data_dt', 'Serie'])
            concurso_final = concurso_final.head(14) # Garante exatamente 14
            concurso_final.insert(0, 'Jogo', range(1, 15))
            
            # Salvar
            nome_arq = os.path.join(output_dir, f"rodada{rd}.csv")
            concurso_final[['Jogo', 'Data', 'Time da Casa', 'Time Visitante', 'Serie', 'Rodada']].to_csv(
                nome_arq, index=False, encoding='utf-8-sig'
            )
            concursos_gerados += 1
            print(f"✅ Arquivo gerado: rodada{rd}.csv | Jogos: {len(concurso_final)}")
        else:
            print(f"⚠️ Rodada {rd} não tinha jogos suficientes nos arquivos.")

    print(f"\n🚀 Pronto! {concursos_gerados} rodadas processadas em '{output_dir}'.")

# Executar
gerar_38_concursos_loteca('brasileiraoA/brasileiraoA2016.csv', 'brasileiraoB/brasileiraoB2016.csv')