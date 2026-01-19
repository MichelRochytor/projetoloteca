import csv
import random
from datetime import datetime
from collections import defaultdict

class Partida:
    def __init__(self, rodada, data, local, time_mandante, placar, time_visitante):
        self.rodada = int(rodada)
        self.data = datetime.strptime(data, '%d/%m/%Y').date()
        self.local = local.strip('"')
        self.time_mandante = time_mandante
        self.placar = placar
        self.time_visitante = time_visitante
        
    def __str__(self):
        return f"Rodada {self.rodada}: {self.time_mandante} vs {self.time_visitante} ({self.data.strftime('%d/%m/%Y')} - {self.local})"

class LeitorPartidas:
    @staticmethod
    def ler_csv(caminho_arquivo):
        partidas = []
        
        with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            cabecalho = next(leitor)
            
            for linha in leitor:
                try:
                    partida = Partida(*linha)
                    partidas.append(partida)
                except Exception as e:
                    print(f"Erro ao processar linha: {linha}. Erro: {e}")
        
        return partidas

class SorteadorLotecaPorRodada:
    @staticmethod
    def sortear_rodada_completa(partidas_a, partidas_b):
        # Agrupa partidas por rodada
        rodadas = defaultdict(list)
        
        for partida in partidas_a + partidas_b:
            rodadas[partida.rodada].append(partida)
        
        # Filtra apenas rodadas com pelo menos 14 jogos combinados (A + B)
        rodadas_validas = {r: jogos for r, jogos in rodadas.items() if len(jogos) >= 14}
        
        if not rodadas_validas:
            raise ValueError("Nenhuma rodada encontrada com pelo menos 14 jogos combinados entre as séries A e B")
        
        # Sorteia uma rodada válida
        rodada_sorteada = random.choice(list(rodadas_validas.keys()))
        jogos_rodada = rodadas_validas[rodada_sorteada]
        
        # Seleciona 14 jogos aleatórios desta rodada
        jogos_sorteados = random.sample(jogos_rodada, 14)
        
        # Ordena por data/horário (se disponível)
        jogos_sorteados.sort(key=lambda x: x.data)
        
        return jogos_sorteados

if __name__ == "__main__":
    try:
        # Carrega as partidas
        partidas_a = LeitorPartidas.ler_csv('brasileiraoA/brasileiraoA2015.csv')
        partidas_b = LeitorPartidas.ler_csv('brasileiraoB/brasileiraoB2015.csv')
        
        # Sorteia os jogos da mesma rodada
        jogos_loteca = SorteadorLotecaPorRodada.sortear_rodada_completa(partidas_a, partidas_b)
        
        print("🎉 Jogos sorteados para a Loteca (Brasileirão 2015 - mesma rodada) 🎢\n")
        print(f"Rodada {jogos_loteca[0].rodada} - {jogos_loteca[0].data.strftime('%d/%m/%Y')}\n")
        print("Nº | Jogo")
        print("---|-------------------------------")
        for i, jogo in enumerate(jogos_loteca, 1):
            print(f"{i:2} | {jogo.time_mandante:20} vs {jogo.time_visitante:20} @ {jogo.local}")
            
        print("\nBoa sorte nos seus palpites! ⚽🎯")
        
    except ValueError as e:
        print(f"Erro: {e}")
    except FileNotFoundError:
        print("Erro: Arquivo CSV não encontrado. Verifique os caminhos dos arquivos.")