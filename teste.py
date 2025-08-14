import pandas as pd
import random
from datetime import datetime
import os

class SimuladorLoteca:
    def __init__(self):
        self.serie_a = None
        self.serie_b = None
        # Garante que os diretórios existam
        os.makedirs('brasileiraoA', exist_ok=True)
        os.makedirs('brasileiraoB', exist_ok=True)
        self.carregar_dados()

    def carregar_dados(self):
        try:
            # Você precisa salvar os dados do Brasileirão Série A e B que eu te passei
            # nos arquivos 'brasileiraoA/brasileiraoA2015.csv' e 'brasileiraoB/brasileiraoB2015.csv'
            self.serie_a = pd.read_csv('brasileiraoA/brasileiraoA2015.csv')
            self.serie_b = pd.read_csv('brasileiraoB/brasileiraoB2015.csv')

            # Verifica colunas necessárias
            colunas_necessarias = ['Rodada', 'Data', 'Time da Casa', 'Placar', 'Time Visitante']
            for df, nome in zip([self.serie_a, self.serie_b], ['Série A', 'Série B']):
                if not all(col in df.columns for col in colunas_necessarias):
                    raise ValueError(f"O arquivo da {nome} não possui todas as colunas necessárias.")

            print("Dados carregados com sucesso!")
        except FileNotFoundError as e:
            print(f"Erro: Arquivo não encontrado. Verifique se os arquivos .csv estão nos diretórios corretos.")
            print(f"Detalhe: {e}")
            print("Por favor, crie as pastas 'brasileiraoA' e 'brasileiraoB' e salve os arquivos CSV nelas.")
            exit()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            exit()

    def sortear_jogos(self, rodada):
        """Sorteia 14 jogos da rodada especificada"""
        jogos_a = self.serie_a[self.serie_a['Rodada'] == rodada]
        jogos_b = self.serie_b[self.serie_b['Rodada'] == rodada]

        todos_jogos = pd.concat([jogos_a, jogos_b])

        if len(todos_jogos) < 14:
            print(f"Aviso: Apenas {len(todos_jogos)} jogos disponíveis na rodada {rodada}.")
            # Se não houver jogos, retorna um DataFrame vazio
            if len(todos_jogos) == 0:
                return pd.DataFrame(), False
            return todos_jogos.sample(n=len(todos_jogos), random_state=1), False

        return todos_jogos.sample(n=14, random_state=1), True # random_state para resultados consistentes

    def simular_concurso(self, rodada):
        """Simula um concurso completo da Loteca com 14 jogos"""
        jogos_sorteados, completo = self.sortear_jogos(rodada)

        if jogos_sorteados.empty:
            print(f"Nenhum jogo disponível para simulação na rodada {rodada}.")
            return

        palpites = []
        for idx, jogo in jogos_sorteados.iterrows():
            palpites.append({
                'Jogo': len(palpites) + 1,
                'Data': jogo['Data'],
                'Time Casa': jogo['Time da Casa'],
                'Time Visitante': jogo['Time Visitante'],
            })

        df_palpites = pd.DataFrame(palpites)

        # Exibe o bilhete da Loteca
        print("\n" + "="*80)
        print(f"LOTECA - Concurso Simulado - Rodada {rodada}".center(80))
        print(f"Data da Simulação: {datetime.now().strftime('%d/%m/%Y %H:%M')}".center(80))
        print("="*80)
        # --- LINHA MODIFICADA ---
        # Adicionamos a coluna 'Data' para ser impressa na tela
        print(df_palpites[['Jogo', 'Data', 'Time Casa', 'Time Visitante']].to_string(index=False))
        print("="*80)

        if not completo:
            print("\nATENÇÃO: Não havia 14 jogos disponíveis nesta rodada.")
            print(f"Foram sorteados apenas {len(palpites)} jogos.")

        # Salva em CSV
        nome_arquivo = f"loteca_simulada_rodada_{rodada}.csv"
        df_palpites.to_csv(nome_arquivo, index=False)
        print(f"\nConcurso simulado salvo em: {nome_arquivo}")

    def menu(self):
        while True:
            print("\n" + "="*60)
            print("SIMULADOR OFICIAL DA LOTECA".center(60))
            print("="*60)
            print("1. Simular concurso com jogos de uma rodada")
            print("2. Sair")

            opcao = input("\nEscolha uma opção: ")

            if opcao == '1':
                try:
                    rodada = int(input("Digite o número da rodada (1-38): "))
                    if 1 <= rodada <= 38:
                        self.simular_concurso(rodada)
                    else:
                        print("Por favor, digite um número entre 1 e 38.")
                except ValueError:
                    print("Por favor, digite um número válido.")
            elif opcao == '2':
                print("Obrigado por usar o Simulador da Loteca!")
                break
            else:
                print("Opção inválida. Por favor, escolha 1 ou 2.")

if __name__ == "__main__":
    simulador = SimuladorLoteca()
    simulador.menu()