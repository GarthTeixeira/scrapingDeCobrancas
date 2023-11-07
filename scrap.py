import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')
URL = os.environ.get('URL')
CSV_OUTPUT = os.environ.get('CSV_OUTPUT')



class Cobranca:
    def __init__(self, bank_billet_id, register, status):
        self.bank_billet_id = bank_billet_id
        self.register = register
        self.status = status


def get_data(dataRow):
    
    bank_billet_id = dataRow['id']
    bank_register = dataRow.find('i',attrs={'class':'fa-exchange-alt'})['aria-label']
    bank_status = dataRow.find('a',attrs={'class':'circle'})['aria-label']

    data = Cobranca(bank_billet_id, bank_register, bank_status)

    return data
def get_data_item(content_list):
    cardBody = content_list.find('div',attrs={'class':'card-body'})
    tbody = cardBody.find('tbody')
    dataRowsTr = tbody.find_all('tr')
    dataRows = map(get_data,dataRowsTr)
    return list(dataRows)


options = Options()


#options.add_argument('--headless')
navegador = webdriver.Firefox(options=options)
navegador.get(URL)
action = ActionChains(navegador)


menu_humburguer = navegador.find_element(By.CLASS_NAME,'menu-trigger')
menu_humburguer.click()
sleep(0.5)

login_link = navegador.find_element(By.LINK_TEXT,'Entrar')
login_link.click()
sleep(1)

email_input = navegador.find_element(By.ID,'user_email')
email_input.send_keys(EMAIL)

password_input = navegador.find_element(By.ID,'user_password')
password_input.send_keys(PASSWORD)

submit_button = navegador.find_element(By.NAME,'commit')
submit_button.click()

sleep(1)

option_cobranca = navegador.find_element(By.ID,'topnav-cobranca')
action.move_to_element(option_cobranca).perform()
sleep(1)

option_boleto = navegador.find_element(By.ID,'topnav-banco')
action.move_to_element(option_boleto).perform()
sleep(1)

option_gerenciar = navegador.find_element(By.LINK_TEXT,'Gerenciar')
action.click(option_gerenciar).perform()

sleep(1)

pages_contents = []

for i in range(0,10):

    print(i)
    
    page_content = navegador.page_source
    pages_contents.append(page_content)
    sleep(0.2)
    navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(0.8)

    next_button = navegador.find_elements(By.CLASS_NAME,'page-link')[-1]
    if(next_button.get_attribute('aria-label') == 'next'):
        sleep(0.5)
        next_button.click()
        sleep(1)

contents = map(lambda x: BeautifulSoup(x, 'html.parser'), pages_contents)

dadosMap = map(get_data_item,list(contents))

dadosMatrix = np.array(list(dadosMap))

lista_de_dados = dadosMatrix.flatten()

dados = {
    "Id": [cobranca.bank_billet_id for cobranca in lista_de_dados],
    "Registro No Banco": [cobranca.register for cobranca in lista_de_dados],
    "Status": [cobranca.status for cobranca in lista_de_dados]
}

# Passo 2: Criar um DataFrame do Pandas
df = pd.DataFrame(dados)

# Passo 3: Exportar o DataFrame para um arquivo CSV
df.to_csv(CSV_OUTPUT, index=False)