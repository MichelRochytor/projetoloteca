import pandas as pd
import numpy as np

def classificar_campeonato(row):
    mandante = str(row['Mandante']).upper().strip()
    visitante = str(row['Visitante']).upper().strip()
    campeonato_caixa = str(row['Campeonato']).upper()
    data_jogo = pd.to_datetime(row['Data'], format='%d/%m/%Y', errors='coerce')
    mes = data_jogo.month
    dia_semana = str(row['Dia_Semana']).upper()

    # 1. Filtros Diretos (Base e Feminino)
    if 'SUB 20' in campeonato_caixa or 'SUB 20' in mandante or 'SUB 20' in visitante:
        return 'Categoria de Base (Sub-20)'
    if '(FEM)' in campeonato_caixa or 'FEMININO' in campeonato_caixa:
        return 'Futebol Feminino'

    # 2. Futebol de Seleções
    selecoes = ['BRASIL', 'ARGENTINA', 'ALEMANHA', 'FRANCA', 'ESPANHA', 'ITALIA', 'INGLATERRA', 'URUGUAI', 'COLOMBIA', 'PORTUGAL', 'CROACIA', 'HOLANDA', 'MEXICO', 'JAPAO', 'CHILE', 'PARAGUAI', 'EQUADOR', 'VENEZUELA', 'PERU', 'BOLIVIA']
    if mandante in selecoes or visitante in selecoes:
        return 'Seleções (Copa/Eliminatórias/Amistosos)'

    # 3. Ligas Europeias (Champions, La Liga, Premier League, Calcio)
    times_europeus = ['REAL MADRID', 'BARCELONA', 'CHELSEA', 'ARSENAL', 'MILAN', 'JUVENTUS', 'PSG', 'LIVERPOOL', 'MANCHESTER CITY', 'MANCHESTER UNITED', 'BAYERN DE MUNIQUE', 'NAPOLI', 'ROMA', 'INTER DE MILAO', 'SEVILLA', 'ATLETICO MADRID', 'TOTTENHAM', 'DORTMUND', 'VILLARREAL', 'LYON']
    if mandante in times_europeus or visitante in times_europeus:
        # Se os times forem do mesmo país, é liga nacional (Ex: Real x Barça = La Liga)
        espanhois = ['REAL MADRID', 'BARCELONA', 'SEVILLA', 'ATLETICO MADRID', 'VILLARREAL', 'REAL BETIS', 'REAL SOCIEDAD', 'ATHLETIC BILBAO', 'VALENCIA CLUB', 'CELTA DE VIGO', 'ESPANYOL']
        ingleses = ['CHELSEA', 'ARSENAL', 'LIVERPOOL', 'MANCHESTER CITY', 'MANCHESTER UNITED', 'TOTTENHAM', 'WEST HAM', 'LEICESTER', 'EVERTON', 'WOLVES', 'ASTON VILLA']
        italianos = ['JUVENTUS', 'MILAN', 'INTER DE MILAO', 'ROMA', 'NAPOLI', 'LAZIO', 'ATALANTA BERGAMAS', 'FIORENTINA', 'SAMPODRIA', 'TORINO']
        franceses = ['PSG', 'LYON', 'MARSEILLE', 'MONACO', 'LILLE', 'RENNES', 'NICE', 'SAINT-ETIENNE', 'BORDEAUX']
        
        if mandante in espanhois and visitante in espanhois: return 'La Liga (Espanha)'
        if mandante in ingleses and visitante in ingleses: return 'Premier League (Inglaterra)'
        if mandante in italianos and visitante in italianos: return 'Serie A (Itália)'
        if mandante in franceses and visitante in franceses: return 'Ligue 1 (França)'
        
        return 'Champions League / Europa League'

    # 4. Copas Continentais Sul-Americanas (Meio de semana a partir de Fevereiro)
    times_sulamericanos = ['BOCA JUNIORS', 'RIVER PLATE', 'INDEPENDIENTE', 'RACING/ARG', 'SAN LORENZO', 'ESTUDIANTES', 'PENAROL', 'NACIONAL', 'COLO COLO', 'UNIVERSIDAD CHILE', 'UNIVERS CATOLICA', 'OLIMPIA', 'CERRO PORTENO', 'LIBERTAD', 'LDU', 'BARCELONA', 'INDEP. DEL VALLE', 'ATLETICO NACIONAL', 'AMERICA DE CALI', 'MILLONARIOS', 'THE STRONGEST', 'BOLIVAR', 'ALIANZA LIMA', 'SPORTING CRISTAL']
    if mandante in times_sulamericanos or visitante in times_sulamericanos:
         return 'Copa Libertadores / Sul-Americana'

    # 5. Estaduais ou Regionais Brasileiros (Janeiro a Abril)
    if 1 <= mes <= 4:
        # Dicionários de Clássicos Estaduais Fortes
        paulistas = ['CORINTHIANS', 'SAO PAULO', 'PALMEIRAS', 'SANTOS', 'PONTE PRETA', 'GUARANI', 'BRAGANTINO', 'ITUANO', 'MIRASSOL', 'SAO BERNARDO']
        cariocas = ['FLAMENGO', 'FLUMINENSE', 'VASCO DA GAMA', 'BOTAFOGO', 'VOLTA REDONDA', 'BANGU', 'BOAVISTA']
        mineiros = ['CRUZEIRO', 'ATLETICO', 'AMERICA', 'TOMBENSE', 'VILLA NOVA', 'CALDENSE']
        gauchos = ['INTERNACIONAL', 'GREMIO', 'JUVENTUDE', 'CAXIAS', 'BRASIL', 'BRASIL RS', 'YPIRANGA']
        
        if mandante in paulistas and visitante in paulistas: return 'Campeonato Paulista'
        if mandante in cariocas and visitante in cariocas: return 'Campeonato Carioca'
        if mandante in mineiros and visitante in mineiros: return 'Campeonato Mineiro'
        if mandante in gauchos and visitante in gauchos: return 'Campeonato Gaúcho'
        
        if dia_semana in ['TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA']:
            return 'Copa do Brasil / Copa do Nordeste'
        return 'Campeonatos Estaduais'

    # 6. Campeonato Brasileiro (Maio a Dezembro)
    if 5 <= mes <= 12:
        # Copas Nacionais de Meio de Semana
        if dia_semana in ['TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA']:
             return 'Copa do Brasil / Libertadores (Fases Finais)'

        # Lógica de Inferência Série A vs B vs C
        # Se envolver os times gigantes que dificilmente caem ou ficaram muito tempo na A:
        gigantes_a = ['FLAMENGO', 'SAO PAULO', 'CORINTHIANS', 'PALMEIRAS', 'SANTOS', 'FLUMINENSE', 'ATLETICO', 'CRUZEIRO', 'INTERNACIONAL', 'GREMIO', 'ATHLETICO', 'BOTAFOGO']
        
        # Times clássicos de Série B/C
        times_serie_b_c = ['CRB', 'SAMPAIO CORREA', 'SAMP CORREA', 'LONDRINA', 'OPERARIO', 'VILA NOVA', 'GUARANI', 'PONTE PRETA', 'ITUANO', 'NOVORIZONTINO', 'TOMBENSE', 'BRASIL DE PELOTAS', 'OESTE', 'CONFIANCA', 'NAUTICO', 'CSA', 'ABC', 'PAYSANDU', 'REMO', 'CRICIUMA']
        
        if mandante in gigantes_a or visitante in gigantes_a:
            return 'Campeonato Brasileiro - Série A'
        elif mandante in times_serie_b_c and visitante in times_serie_b_c:
            return 'Campeonato Brasileiro - Série B'
        elif mandante in times_serie_b_c or visitante in times_serie_b_c:
            return 'Campeonato Brasileiro - Série B/C'
        else:
            return 'Campeonato Brasileiro (Série B/C/D)'

    return 'Futebol Nacional (Outros)'

def executar_classificacao():
    print("Carregando o dataset original...")
    try:
        df = pd.read_csv('dataset_loteca_2006_presente.csv')
        print(f"Dataset carregado com {len(df)} jogos. Iniciando classificação exata...")
        
        # Aplica o algoritmo
        df['Torneio_Exato'] = df.apply(classificar_campeonato, axis=1)
        
        # Salva o novo arquivo
        df.to_csv('dataset_loteca_classificado_ia.csv', index=False, encoding='utf-8')
        print("\nPronto! Arquivo 'dataset_loteca_classificado_ia.csv' gerado com sucesso.")
        
        # Mostra um resumo do que ele encontrou
        print("\nDistribuição dos torneios encontrados:")
        print(df['Torneio_Exato'].value_counts())
        
    except FileNotFoundError:
        print("Erro: O arquivo 'dataset_loteca_2006_presente.csv' não foi encontrado na mesma pasta.")

if __name__ == "__main__":
    executar_classificacao()