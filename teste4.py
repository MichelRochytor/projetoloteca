import pandas as pd

def calcular_classificacao(df, rodada):
    # Filtra os jogos até a rodada especificada
    df_rodada = df[df['Rodada'] <= rodada]
    
    # Lista de todos os times
    times = list(set(df_rodada['Time da Casa'].unique()).union(set(df_rodada['Time Visitante'].unique())))
    
    # Cria estrutura para armazenar as estatísticas
    classificacao = []
    
    for time in times:
        # Jogos como mandante (Time da Casa)
        mandante = df_rodada[df_rodada['Time da Casa'] == time]
        # Jogos como visitante
        visitante = df_rodada[df_rodada['Time Visitante'] == time]
        
        # Calcula estatísticas
        vitorias = empates = derrotas = pontos = gols_pro = gols_contra = 0
        
        # Processa jogos como mandante
        for _, jogo in mandante.iterrows():
            gols = jogo['Placar'].split('-')
            gols_m, gols_v = int(gols[0]), int(gols[1])
            
            gols_pro += gols_m
            gols_contra += gols_v
            
            if gols_m > gols_v:
                vitorias += 1
                pontos += 3
            elif gols_m == gols_v:
                empates += 1
                pontos += 1
            else:
                derrotas += 1
        
        # Processa jogos como visitante
        for _, jogo in visitante.iterrows():
            gols = jogo['Placar'].split('-')
            gols_m, gols_v = int(gols[0]), int(gols[1])
            
            gols_pro += gols_v
            gols_contra += gols_m
            
            if gols_v > gols_m:
                vitorias += 1
                pontos += 3
            elif gols_v == gols_m:
                empates += 1
                pontos += 1
            else:
                derrotas += 1
        
        # Adiciona à classificação
        classificacao.append({
            'Time': time,
            'Pts': pontos,
            'J': vitorias + empates + derrotas,
            'V': vitorias,
            'E': empates,
            'D': derrotas,
            'GP': gols_pro,
            'GC': gols_contra,
            'SG': gols_pro - gols_contra
        })
    
    # Ordena a classificação
    classificacao = sorted(classificacao, key=lambda x: (-x['Pts'], -x['V'], -x['SG'], -x['GP'], x['GC'], x['Time']))
    
    # Cria DataFrame com a classificação
    df_classificacao = pd.DataFrame(classificacao)
    df_classificacao.index = range(1, len(df_classificacao) + 1)
    
    return df_classificacao

def mostrar_jogos_rodada(df, rodada):
    jogos_rodada = df[df['Rodada'] == rodada]
    
    if jogos_rodada.empty:
        print(f"Nenhum jogo encontrado para a rodada {rodada}.")
        return
    
    print(f"\nJogos da Rodada {rodada}:")
    print("="*60)
    for _, jogo in jogos_rodada.iterrows():
        print(f"{jogo['Time da Casa']} {jogo['Placar']} {jogo['Time Visitante']}")
    print("="*60)

def main():
    print("Tabela do Campeonato Brasileiro - Visualizador por Rodada")
    print("="*60)
    
    try:
        # Lê o arquivo CSV (ajuste o caminho conforme necessário)
        df = pd.read_csv('brasileiraoA/brasileiraoA2015.csv')
        
        # Verifica se as colunas necessárias existem
        colunas_necessarias = ['Rodada', 'Time da Casa', 'Placar', 'Time Visitante']
        if not all(col in df.columns for col in colunas_necessarias):
            print("O arquivo CSV não possui as colunas necessárias.")
            print("Colunas encontradas:", df.columns.tolist())
            print("Colunas necessárias:", colunas_necessarias)
            return
        
        while True:
            try:
                rodada = int(input("\nDigite o número da rodada (1-38) ou 0 para sair: "))
                if rodada == 0:
                    print("Saindo...")
                    break
                if 1 <= rodada <= 38:
                    # Mostra jogos da rodada
                    mostrar_jogos_rodada(df, rodada)
                    
                    # Calcula e mostra a classificação até a rodada
                    classificacao = calcular_classificacao(df, rodada)
                    
                    print(f"\nClassificação até a Rodada {rodada}:")
                    print("="*60)
                    print(classificacao[['Time', 'Pts', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG']])
                    print("="*60)
                else:
                    print("Por favor, digite um número entre 1 e 38.")
            except ValueError:
                print("Por favor, digite um número válido.")
    except FileNotFoundError:
        print("Arquivo 'brasileirao.csv' não encontrado no diretório.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()