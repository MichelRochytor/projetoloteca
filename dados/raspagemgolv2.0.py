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
    # ==========================================
    # 📋 FILA DE CAMPEONATOS (BATCH PROCESSING)
    # Adicione quantos quiser seguindo este formato!
    # ==========================================
    fila_de_campeonatos = [
        {
            "nome_arquivo_base": "goiano",
            "ano_inicial": 1944,
            "url_inicial": "https://www.ogol.com.br/edicao/goiano-1944/26949/calendario",
            "pasta_destino": os.path.join('dados', 'brasil', 'estaduais', 'goiano')
        },
        {
            "nome_arquivo_base": "capixaba",
            "ano_inicial": 1918,
            "url_inicial": "https://www.ogol.com.br/edicao/campeonato-capixaba-1918/40710/calendario",
            "pasta_destino": os.path.join('dados', 'brasil', 'estaduais', 'capixaba')
        },
        {
            "nome_arquivo_base": "matogrossense",
            "ano_inicial": 1944,
            "url_inicial": "https://www.ogol.com.br/edicao/mato-grosso-1945/46089/calendario",
            "pasta_destino": os.path.join('dados', 'brasil', 'estaduais', 'matogrossense')
        },
        {
            "nome_arquivo_base": "sulmatogrossense",
            "ano_inicial": 1979,
            "url_inicial": "https://www.ogol.com.br/edicao/sul-mato-grossense-1979/45963/calendario",
            "pasta_destino": os.path.join('dados', 'brasil', 'estaduais', 'sulmatogrossense')
        },
        {
            "nome_arquivo_base": "paraibano",
            "ano_inicial": 1913,
            "url_inicial": "https://www.ogol.com.br/edicao/campeonato-paraibano-1913/41923/calendario",
            "pasta_destino": os.path.join('dados', 'brasil', 'estaduais', 'paraibano')
        },
        {
            "nome_arquivo_base": "pernambucano",
            "ano_inicial": 1915,
            "url_inicial": "https://www.ogol.com.br/edicao/campeonato-pernambucano-1915/131645/calendario",
            "pasta_destino": os.path.join('dados', 'brasil', 'estaduais', 'pernambucano')
        },
        {
            "nome_arquivo_base": "catarinense",
            "ano_inicial": 1924,
            "url_inicial": "https://www.ogol.com.br/edicao/campeonato-catarinense-1924/38804/calendario",
            "pasta_destino": os.path.join('dados', 'brasil', 'estaduais', 'catarinense')
        },
        {
            "nome_arquivo_base": "paranaense",
            "ano_inicial": 1915,
            "url_inicial": "https://www.ogol.com.br/edicao/paranaense-1915/41236/calendario",
            "pasta_destino": os.path.join('dados', 'brasil', 'estaduais', 'paranaense')
        }
        # Basta colocar uma vírgula acima e adicionar outro dicionário {...} para o Mineiro, Carioca, etc.
    ]

    opcoes = Options()
    opcoes.page_load_strategy = 'eager' 
    opcoes.add_argument("--disable-notifications")
    opcoes.add_argument("--blink-settings=imagesEnabled=false") 
    
    # 🕵️‍♂️ MODO STEALTH (BACKGROUND) 🕵️‍♂️
    opcoes.add_argument("--headless=new") # Oculta o navegador
    opcoes.add_argument("--window-size=1920,1080") # Garante que os botões não sumam no modo invisível
    opcoes.add_argument("--disable-gpu") # Melhora a estabilidade em modo headless no Linux/Windows
    opcoes.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    opcoes.add_argument("--disable-dev-shm-usage")

    print("🤖 Iniciando o navegador em modo invisível (Headless)...")
    pagina = webdriver.Chrome(options=opcoes)
    pagina.set_page_load_timeout(30)
    
    # ==========================================
    # LOOP MASTER: NAVEGAÇÃO ENTRE OS CAMPEONATOS
    # ==========================================
    for campeonato in fila_de_campeonatos:
        temporada_atual = campeonato["ano_inicial"]
        pasta_destino = campeonato["pasta_destino"]
        prefixo = campeonato["nome_arquivo_base"]
        
        print("\n" + "="*60)
        print(f"🏆 INICIANDO RASPAGEM: {prefixo.upper()}")
        print("="*60)
        
        os.makedirs(pasta_destino, exist_ok=True)
        print(f"📁 Destino: {os.path.abspath(pasta_destino)}")
        
        # Acessa a página inicial deste campeonato específico
        pagina.get(campeonato["url_inicial"])
        time.sleep(3) # Pausa para garantir o carregamento inicial
        
        # ==========================================
        # LOOP EXTERNO: NAVEGAÇÃO ENTRE AS TEMPORADAS
        # ==========================================
        while True:
            nome_arquivo = f'{prefixo}{temporada_atual}.csv'
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)
            
            print(f"\n[{nome_arquivo}] Iniciando extração da temporada...")
            
            with open(caminho_completo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
                escritor = csv.writer(arquivo_csv)
                escritor.writerow(['Rodada', 'Data', 'Time da Casa', 'Placar', 'Time Visitante'])
                
                pagina_atual = 1
                
                # ==========================================
                # LOOP INTERNO: NAVEGAÇÃO ENTRE AS PÁGINAS DA TEMPORADA
                # ==========================================
                while True:
                    print(f"--- Coletando dados da página {pagina_atual} ---")
                    
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
                        pass

                    time.sleep(2) 
                    
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
                            
                            if not time_casa: continue
                                
                            rodada = fase_raw.replace('R', '') if 'R' in fase_raw else fase_raw
                            try: data_formatada = datetime.strptime(data_raw, "%Y-%m-%d").strftime("%d/%m/%y")
                            except ValueError: data_formatada = data_raw 
                            
                            escritor.writerow([rodada, data_formatada, time_casa, placar, time_fora])
                            
                        except AttributeError:
                            continue
                    
                    # Avança para o próximo número de página
                    try:
                        proxima_pagina_num = str(pagina_atual + 1)
                        xpath_numero = f"//div[@class='numbers']//a[text()='{proxima_pagina_num}']"
                        botao_numero = pagina.find_element(By.XPATH, xpath_numero)
                        pagina.execute_script("arguments[0].click();", botao_numero)
                        pagina_atual += 1
                        time.sleep(3)
                    except Exception:
                        print(f"Número {pagina_atual + 1} não encontrado. Fim das páginas da edição {temporada_atual}.")
                        break 
                
            # ==========================================
            # AVANÇANDO PARA A PRÓXIMA TEMPORADA
            # ==========================================
            try:
                print("\nProcurando a próxima temporada (seta direita)...")
                botao_prox_temporada = pagina.find_element(By.CSS_SELECTOR, "a.zz-combo-arrow-right")
                pagina.execute_script("arguments[0].click();", botao_prox_temporada)
                
                temporada_atual += 1
                time.sleep(5) 
                
                aba_calendario = pagina.find_element(By.XPATH, "//div[contains(@class, 'zz-enthdr-menu-bar-items')]//a[contains(@href, '/calendario')]")
                pagina.execute_script("arguments[0].click();", aba_calendario)
                time.sleep(4) 
                
            except Exception as e:
                print(f"\n✅ Seta não encontrada. Finalizamos o campeonato: {prefixo.upper()}!")
                break # Quebra o loop de temporadas e passa para o próximo campeonato da fila!

    # Fecha o navegador apenas quando TODOS os campeonatos da fila terminarem
    pagina.quit()
    print("\n🚀 EXTRAÇÃO EM MASSA DE TODAS AS LIGAS CONCLUÍDA COM SUCESSO!")

if __name__ == "__main__":
    raspar_gol()