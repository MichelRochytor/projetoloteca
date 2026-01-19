import pandas as pd
import random

# Funções para a tabela do campeonato
def calcular_classificacao(df, rodada):
    df_rodada = df[df['Rodada'] <= rodada]
    times = list(set(df_rodada['Time da Casa'].unique()).union(set(df_rodada['Time Visitante'].unique())))
    
    classificacao = []
    for time in times:
        mandante = df_rodada[df_rodada['Time da Casa'] == time]
        visitante = df_rodada[df_rodada['Time Visitante'] == time]
        
        vitorias = empates = derrotas = pontos = gols_pro = gols_contra = 0
        
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
    
    classificacao = sorted(classificacao, key=lambda x: (-x['Pts'], -x['V'], -x['SG'], -x['GP'], x['GC'], x['Time']))
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

# Funções para o sorteador Loteca
def sortear_palpite():
    return random.choice(['1', 'X', '2'])

def sortear_loteca(serie_a, serie_b, rodada):
    jogos_a = serie_a[serie_a['Rodada'] == rodada]
    jogos_b = serie_b[serie_b['Rodada'] == rodada]
    todos_jogos = pd.concat([jogos_a, jogos_b])
    
    if todos_jogos.empty:
        print(f"Nenhum jogo encontrado para a rodada {rodada} nas séries A e B.")
        return None
    
    palpites = []
    for _, jogo in todos_jogos.iterrows():
        palpite = sortear_palpite()
        palpites.append({
            'Rodada': rodada,
            'Time da Casa': jogo['Time da Casa'],
            'Time Visitante': jogo['Time Visitante'],
            'Palpite': palpite,
            'Significado': 'Casa' if palpite == '1' else 'Empate' if palpite == 'X' else 'Fora'
        })
    
    return pd.DataFrame(palpites)

# Menu principal
def menu_principal():
    print("\n" + "="*60)
    print("Brasileirão Manager - Sistema Completo".center(60))
    print("="*60)
    print("1. Visualizar Tabela do Campeonato")
    print("2. Sortear Palpites para Loteca")
    print("3. Sair")
    return input("\nEscolha uma opção: ")

def main():
    print("Carregando dados...")
    try:
        serie_a = pd.read_csv('brasileiraoA/brasileiraoA2015.csv')
        serie_b = pd.read_csv('brasileiraoB/brasileiraoB2015.csv')
        
        # Verifica colunas necessárias
        colunas_necessarias = ['Rodada', 'Time da Casa', 'Placar', 'Time Visitante']
        for df, nome in zip([serie_a, serie_b], ['Série A', 'Série B']):
            if not all(col in df.columns for col in colunas_necessarias):
                print(f"Erro: O arquivo da {nome} não possui as colunas necessárias.")
                return
    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivos: {e}")
        return
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return

    while True:
        opcao = menu_principal()
        
        if opcao == '1':
            # Visualizar tabela
            while True:
                try:
                    rodada = int(input("\nDigite o número da rodada (1-38) ou 0 para voltar: "))
                    if rodada == 0:
                        break
                    if 1 <= rodada <= 38:
                        print("\n" + "="*60)
                        print(f"BRASILEIRÃO SÉRIE A - Rodada {rodada}".center(60))
                        print("="*60)
                        mostrar_jogos_rodada(serie_a, rodada)
                        classificacao = calcular_classificacao(serie_a, rodada)
                        print(classificacao[['Time', 'Pts', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG']])
                        
                        print("\n" + "="*60)
                        print(f"BRASILEIRÃO SÉRIE B - Rodada {rodada}".center(60))
                        print("="*60)
                        mostrar_jogos_rodada(serie_b, rodada)
                        classificacao = calcular_classificacao(serie_b, rodada)
                        print(classificacao[['Time', 'Pts', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG']])
                    else:
                        print("Por favor, digite um número entre 1 e 38.")
                except ValueError:
                    print("Por favor, digite um número válido.")
        
        elif opcao == '2':
            # Sortear Loteca
            while True:
                try:
                    rodada = int(input("\nDigite o número da rodada (1-38) ou 0 para voltar: "))
                    if rodada == 0:
                        break
                    if 1 <= rodada <= 38:
                        palpites = sortear_loteca(serie_a, serie_b, rodada)
                        if palpites is not None:
                            print("\n" + "="*60)
                            print(f"PALPITES LOTECA - Rodada {rodada}".center(60))
                            print("="*60)
                            print(palpites[['Time da Casa', 'Time Visitante', 'Palpite', 'Significado']].to_string(index=False))
                            
                            salvar = input("\nDeseja salvar os palpites em CSV? (s/n): ").lower()
                            if salvar == 's':
                                nome_arquivo = f"palpites_loteca_rodada_{rodada}.csv"
                                palpites.to_csv(nome_arquivo, index=False)
                                print(f"Arquivo salvo como {nome_arquivo}")
                    else:
                        print("Por favor, digite um número entre 1 e 38.")
                except ValueError:
                    print("Por favor, digite um número válido.")
        
        elif opcao == '3':
            print("Saindo do sistema...")
            break
        
        else:
            print("Opção inválida. Por favor, escolha 1, 2 ou 3.")

if __name__ == "__main__":
    main()