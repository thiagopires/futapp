import pandas as pd
pd.set_option('display.max_columns', None)

from tinydb import TinyDB, Query
from tqdm.auto import tqdm

import logging
import warnings
warnings.filterwarnings('ignore')

import re
import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configuração do logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

def Dados_Jogo(id_jogo, dictionary, driver):
    """Captura informações básicas do jogo: data, times, liga e rodada."""
    try:
        driver.get(f'https://www.flashscore.com/match/{id_jogo}/#/match-summary/match-s...')
        dictionary['Id'] = id_jogo

        # Extrair país, data, hora e liga
        country = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.tournamentHeader__country'))
        ).text.split(':')[0]

        date_time = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.duelParticipant__startTime'))
        ).text.split(' ')
        dictionary['Date'] = date_time[0].replace('.', '/')
        dictionary['Time'] = date_time[1]

        league = driver.find_element(By.CSS_SELECTOR, 'spand.tournamentHeader__country > a').text.split(' -')[0]
        dictionary['League'] = f'{country} - {league}'

        # Extrair times
        dictionary['Home'] = driver.find_element(By.CSS_SELECTOR, 'div.duelParticipant__home div.participant__participantName').text
        dictionary['Away'] = driver.find_element(By.CSS_SELECTOR, 'div.duelParticipant__away div.participant__participantName').text

        # Extrair rodada (se disponivel)
        try:
            dictionary['Round'] = driver.find_element(By.CSS_SELECTOR, 'span.tournamentHeader_country > a').text
        except:        
            dictionary['Round'] = '-'

    except Exception as e:
        logging.error(f'Erro em Dados_Jogo: {e}')

def Temporada(dictionary, season):
    dictionary['Season'] = season

def Odds_Match_Odds_HT(id_jogo, dictionary, driver):
    url_match_odds_ht = f'https://www.flashscore.com/match/{id_jogo}/#/odds-comparison/1x2-odds/1st-half'
    driver.get(url_match_odds_ht)
    time.sleep(1)
    if driver.current_url == url_match_odds_ht:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.ui-table')))
        table_odds = driver.find_element(By.CSS_SELECTOR, 'div.ui-table')
        linha_ml_ht = table_odds.find_element(By.CSS_SELECTOR, 'div.ui-table__row')
        odds_ht = float(linha_ml_ht.find_elements(By.CSS_SELECTOR, 'a.oddsCell__odd'))
        dictionary['Odd_H_HT'] = odds_ht[0].text
        dictionary['Odd_D_HT'] = odds_ht[1].text
        dictionary['Odd_A_HT'] = odds_ht[2].text

def Odds_Match_Odds_FT(id_jogo, dictionary, driver):
    url_match_odds_ft = f'https://www.flashscore.com/match/{id_jogo}/#/odds-comparison/1x2-odds/full-time'
    driver.get(url_match_odds_ft)
    time.sleep(1)
    if driver.current_url == url_match_odds_ft:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.ui-table')))
        table_odds = driver.find_element(By.CSS_SELECTOR, 'div.ui-table')
        linha_ml_ht = table_odds.find_element(By.CSS_SELECTOR, 'div.ui-table__row')
        odds_ht = float(linha_ml_ht.find_elements(By.CSS_SELECTOR, 'a.oddsCell__odd'))
        dictionary['Odd_H_HT'] = odds_ht[0].text
        dictionary['Odd_D_HT'] = odds_ht[1].text
        dictionary['Odd_A_HT'] = odds_ht[2].text