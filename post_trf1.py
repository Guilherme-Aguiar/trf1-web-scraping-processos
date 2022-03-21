from bs4 import BeautifulSoup
from urllib import parse
import requests
import pandas as pd

def get_cookies(url):
    session = requests.Session()
    response = session.get(url)
    return session.cookies.get_dict()

MAIN_URL = 'https://processual.trf1.jus.br/'
SEARCH_URL = 'https://processual.trf1.jus.br/consultaProcessual/parte/listar.php'
PROCESSOS_URL = 'https://processual.trf1.jus.br/consultaProcessual/processo.php'

data = {
  'secao': 'TRF1',
  'pg': '2',
  'enviar': 'Pesquisar',
  'nome': 'joao silva'
}

cookies = get_cookies(MAIN_URL)
search_response = requests.post(SEARCH_URL, cookies=cookies, data=data)
search_html = BeautifulSoup(search_response.text, "html.parser")
processos = search_html.findAll('a', {'class':'listar-processo'})
temp_href_list = [f'https://processual.trf1.jus.br{processo["href"]}' for processo in processos]

processos_params_list = []
params = (('secao', 'TRF1'),)
for href in temp_href_list:
  
  temp_response = requests.get(href, cookies=cookies, params=params)
  temp_html = BeautifulSoup(temp_response.text, "html.parser")
  temp_info = temp_html.find('a')
  processos_params_list.append((parse.parse_qsl(temp_info['href'])[0][1], parse.parse_qsl(temp_info['href'])[2][1]))

headers = {
  'Referer': 'https://processual.trf1.jus.br/consultaProcessual/nomeParte.php?secao=TRF1',
}

columns = ['PROCESSO', 'NOVA_NUMERACAO', 'GRUPO', 'ASSUNTO', 'DATA_DE_ATUACAO', 'ORGAO_JULGADOR', 'JUIZ_RELATOR', 'PROCESSO_ORIGINARIO']

df = pd.DataFrame(columns=columns)

for processo in processos_params_list[:10]:
  current_param = (
    ('proc', processo[0]),
    ('secao', 'TRF1'),
    ('nome', processo[1]),
    ('mostrarBaixados', 'N'),
  )
  processo_table = BeautifulSoup(requests.get(PROCESSOS_URL, params=current_param, cookies=cookies, headers=headers).text, "html.parser").find('table')
  df.loc[df.shape[0]] = [i.get_text() for i in processo_table.findAll('td')]

df = df.reset_index(drop=True)
df['ASSUNTO'] = df['ASSUNTO'].str.strip()
df.to_csv('processos.csv', index=False)