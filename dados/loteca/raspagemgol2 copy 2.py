import csv
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def raspar_gol():
    opcoes = Options()
    opcoes.page_load_strategy = 'eager' 
    opcoes.add_argument("--disable-notifications")
    opcoes.add_argument("--blink-settings=imagesEnabled=false") 
    opcoes.add_argument("--start-maximized")
    opcoes.add_argument("--disable-dev-shm-usage")

    print("Iniciando o navegador para coleta intensiva do Loteca...")
    pagina = webdriver.Chrome(options=opcoes)
    pagina.set_page_load_timeout(180)
    
    # Acessa a página inicial (ponto de partida)
    pagina.get("https://www.ogol.com.br/edicao/campeonato-maranhense-1918/127897/calendario")
    
    temporada_atual = 1918  # Temporada inicial  
    
    # ==========================================
    # 📁 CONFIGURAÇÃO DE DIRETÓRIO DE SAÍDA
    # ==========================================
    pasta_destino = os.path.join('dados', 'brasil', 'estaduais', 'maranhense')
    
    # Cria a pasta e subpastas caso não existam
    os.makedirs(pasta_destino, exist_ok=True)
    print(f"📁 Os arquivos serão salvos no diretório: {os.path.abspath(pasta_destino)}")
    
    # ==========================================
    # LOOP EXTERNO: NAVEGAÇÃO ENTRE AS TEMPORADAS
    # ==========================================
    while True:
        nome_arquivo = f'maranhense{temporada_atual}.csv'
        
        # Junta a pasta com o nome do arquivo
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        
        print(f"\n[{nome_arquivo}] Iniciando extração da temporada...")
        
        # Usa o caminho_completo em vez de apenas o nome_arquivo
        with open(caminho_completo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
            escritor = csv.writer(arquivo_csv)
            escritor.writerow(['Rodada', 'Data', 'Time da Casa', 'Placar', 'Time Visitante'])
            
            pagina_atual = 1
            
            # ==========================================
            # LOOP INTERNO: NAVEGAÇÃO ENTRE AS PÁGINAS DA TEMPORADA
            # ==========================================
            while True:
                print(f"--- Coletando dados da página {pagina_atual} ---")
                
                # Tratamento do Pop-up (z-index: 1000)
                try:
                    botao_anuncio = WebDriverWait(pagina, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@style, 'z-index: 1000')]"))
                    )
                    pagina.execute_script("arguments[0].click();", botao_anuncio)
                    time.sleep(3) 
                    
                    if len(pagina.window_handles) > 1:
                        aba_velha = pagina.window_handles[0]
                        aba_nova = pagina.window_handles[-1]
                        
                        pagina.switch_to.window(aba_velha)
                        pagina.close()
                        pagina.switch_to.window(aba_nova)
                        print(">> Pop-up destruído e aba pirata fechada!")
                except Exception:
                    pass # Sem pop-up, segue o jogo

                time.sleep(2) 
                
                # Extração da Tabela
                html = pagina.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                tabela = soup.find('table', class_='zztable stats')
                if not tabela:
                    print("Tabela não encontrada nesta página.")
                    break
                    
                linhas = tabela.find('tbody').find_all('tr')
                
                for linha in linhas:
                    try:
                        fase_raw = linha.find('td', class_='phase').text.strip()
                        data_raw = linha.find('td', class_='date').text.strip()
                        time_casa = linha.find('td', class_='text home').text.strip()
                        placar = linha.find('td', class_='result').text.strip()
                        time_fora = linha.find('td', class_='text away').text.strip()
                        
                        if not time_casa:
                            continue
                            
                        rodada = fase_raw.replace('R', '') if 'R' in fase_raw else fase_raw
                        
                        try:
                            data_formatada = datetime.strptime(data_raw, "%Y-%m-%d").strftime("%d/%m/%y")
                        except ValueError:
                            data_formatada = data_raw 
                        
                        escritor.writerow([rodada, data_formatada, time_casa, placar, time_fora])
                        
                    except AttributeError:
                        continue
                
                # ==========================================
                # NOVO MÉTODO: NAVEGAÇÃO PELOS NÚMEROS DA PÁGINA
                # ==========================================
                try:
                    proxima_pagina_num = str(pagina_atual + 1)
                    xpath_numero = f"//div[@class='numbers']//a[text()='{proxima_pagina_num}']"
                    botao_numero = pagina.find_element(By.XPATH, xpath_numero)
                    
                    pagina.execute_script("arguments[0].click();", botao_numero)
                    pagina_atual += 1
                    time.sleep(3)
                except Exception:
                    print(f"Número {pagina_atual + 1} não encontrado. Fim das páginas para a temporada {temporada_atual}.")
                    break 
            
        # ==========================================
        # AVANÇANDO PARA A PRÓXIMA TEMPORADA
        # ==========================================
        try:
            print("\nProcurando a próxima temporada (seta direita)...")
            botao_prox_temporada = pagina.find_element(By.CSS_SELECTOR, "a.zz-combo-arrow-right")
            pagina.execute_script("arguments[0].click();", botao_prox_temporada)
            
            temporada_atual += 1
            print("Carregando a página da nova temporada...")
            time.sleep(5) 
            
            print("Buscando a aba 'Calendário' na nova temporada...")
            aba_calendario = pagina.find_element(By.XPATH, "//div[contains(@class, 'zz-enthdr-menu-bar-items')]//a[contains(@href, '/calendario')]")
            pagina.execute_script("arguments[0].click();", aba_calendario)
            
            print("Aba Calendário acessada com sucesso! Preparando para extrair...")
            time.sleep(4) 
            
        except Exception as e:
            print("\nSeta para a próxima temporada não encontrada ou erro na aba. Chegamos à edição mais recente!")
            break 

    pagina.quit()
    print("\nExtração em massa concluída com sucesso!")

if __name__ == "__main__":
    raspar_gol()