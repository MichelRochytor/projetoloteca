import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def minerar_goyaz_v2():
    # URL base da edição de 2006 (Série B)
    url_base = "https://www.futeboldegoyaz.com.br/campeonatos/93/edicao"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    todos_jogos = []

    print("🛰️ Iniciando mineração robusta da Série B 2006...")

    for rodada in range(1, 39):
        print(f"📦 Minerando Rodada {rodada}/38...", end='\r')
        try:
            # O site carrega a rodada via parâmetro GET
            response = requests.get(f"{url_base}?rodada={rodada}", headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Procuramos por todas as linhas de tabela
            linhas = soup.find_all('tr')
            
            for linha in linhas:
                celulas = linha.find_all('td')
                # Uma linha de jogo válida no Futebol de Goyaz tem geralmente 5 a 6 colunas
                if len(celulas) >= 5:
                    texto_placar = celulas[3].get_text(strip=True)
                    
                    if ' x ' in texto_placar:
                        data = celulas[0].get_text(strip=True).split(' ')[0]
                        time_casa = celulas[2].get_text(strip=True)
                        placar = texto_placar.replace(' x ', '-')
                        time_fora = celulas[4].get_text(strip=True)

                        todos_jogos.append({
                            'Rodada': rodada,
                            'Data': data,
                            'Time da Casa': time_casa,
                            'Placar': placar,
                            'Time Visitante': time_fora
                        })
            
            time.sleep(0.5) # Pausa leve para não ser bloqueado

        except Exception as e:
            print(f"\n❌ Erro na rodada {rodada}: {e}")

    if todos_jogos:
        df = pd.DataFrame(todos_jogos)
        # Limpeza de nomes (Removendo as siglas de estado tipo -MG, -PE)
        df['Time da Casa'] = df['Time da Casa'].str.split('-').str[0].str.strip()
        df['Time Visitante'] = df['Time Visitante'].str.split('-').str[0].str.strip()
        
        # Mapeamento para o seu padrão oficial
        mapa_oficial = {
            'Atlético': 'Atlético-MG',
            'Sport': 'Sport Recife',
            'Ceará': 'Ceará SC',
            'América': 'América-RN', # Cuidado: 2006 tinha América-RN na B
            'Vitória': 'EC Vitória'
        }
        df['Time da Casa'] = df['Time da Casa'].replace(mapa_oficial)
        df['Time Visitante'] = df['Time Visitante'].replace(mapa_oficial)

        df.to_csv('brasileiraoB2006_goyaz.csv', index=False, encoding='utf-8-sig')
        print(f"\n✅ Finalizado! {len(df)} jogos salvos.")
    else:
        print("\n⚠️ O site pode estar bloqueando o script ou mudou a estrutura. Verifique o arquivo HTML salvo.")

minerar_goyaz_v2()