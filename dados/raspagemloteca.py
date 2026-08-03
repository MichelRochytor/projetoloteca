import requests
import pandas as pd
import urllib3
import time
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def raspar_loteca_resiliente():
    concurso_atual = 195
    arquivo_csv = 'dataset_loteca_2006_presente.csv'
    
    # Se o arquivo já existir de uma execução anterior, vamos apagá-loc para começar limpo
    if os.path.exists(arquivo_csv):
        os.remove(arquivo_csv)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }

    print("Iniciando extração robusta para o projeto Loteca...")
    
    while True:
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/loteca/{concurso_atual}"
        sucesso_no_concurso = False
        
        # Sistema de repetição: tenta até 5 vezes se der timeout
        for tentativa in range(1, 6):
            try:
                resposta = requests.get(url, headers=headers, verify=False, timeout=20)
                
                if resposta.status_code != 200:
                    print(f"Fim dos dados ou erro na rota. Parando no concurso {concurso_atual - 1}.")
                    return # Encerra a função
                    
                json_dados = resposta.json()
                data_apuracao = json_dados.get('dataApuracao')
                
                print(f"Baixando Concurso {concurso_atual} - {data_apuracao} (Tentativa {tentativa})")
                
                lista_jogos = json_dados.get('listaResultadoEquipeEsportiva', [])
                dados_concurso = []
                
                for jogo in lista_jogos:
                    linha = {
                        'Concurso': json_dados.get('numero'),
                        'Data': data_apuracao,
                        'Jogo_Num': jogo.get('nuSequencial'),
                        'Mandante': jogo.get('nomeEquipeUm'),
                        'Gols_Mandante': jogo.get('nuGolEquipeUm'),
                        'Visitante': jogo.get('nomeEquipeDois'),
                        'Gols_Visitante': jogo.get('nuGolEquipeDois'),
                        'Campeonato': jogo.get('nomeCampeonato'),
                        'Dia_Semana': jogo.get('diaSemana')
                    }
                    dados_concurso.append(linha)
                
                if dados_concurso:
                    df_temp = pd.DataFrame(dados_concurso)
                    df_temp = df_temp.dropna(subset=['Gols_Mandante', 'Gols_Visitante'])
                    
                    # Salva no CSV imediatamente. Se for o primeiro, escreve o cabeçalho.
                    incluir_cabecalho = not os.path.exists(arquivo_csv)
                    df_temp.to_csv(arquivo_csv, mode='a', index=False, encoding='utf-8', header=incluir_cabecalho)
                
                sucesso_no_concurso = True
                concurso_atual += 1
                time.sleep(0.5)
                break # Sai do loop de tentativas pois deu certo
                
            except requests.exceptions.Timeout:
                print(f"Timeout no concurso {concurso_atual}. Aguardando 3 segundos... (Tentativa {tentativa}/5)")
                time.sleep(3)
            except Exception as e:
                print(f"Erro inesperado no concurso {concurso_atual}: {e}. (Tentativa {tentativa}/5)")
                time.sleep(3)
                
        # Se esgotou as 5 tentativas e não teve sucesso, aborta a execução para não ficar em loop infinito
        if not sucesso_no_concurso:
            print(f"Falha definitiva ao baixar o concurso {concurso_atual}. Script interrompido.")
            break

if __name__ == "__main__":
    raspar_loteca_resiliente()