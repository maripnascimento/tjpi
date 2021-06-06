import re
import requests
from bs4 import BeautifulSoup


def cnj_breaker(cnj):
	cnj_regex = re.compile(r'(\d{7})-(\d{2}).(\d{4}).(\d).(\d{2}).(\d{4})')
	cnj_result = cnj_regex.search(cnj)
	if not cnj_result:
		print('nao achei')
	
	return cnj_result


def cnj_cleaner(cnj):
	
	return cnj.replace('-','').replace('.','') 

def get_params(cnj):
	broken_cnj = cnj_breaker(cnj)	
	clean_cnj = cnj_cleaner(cnj)

	params = {
	'NNNNNNN':broken_cnj.group(1),
	'DD':broken_cnj.group(2),
	'AAAA':broken_cnj.group(3),
	'T':broken_cnj.group(4),
	'TR':broken_cnj.group(5),
	'OOOO':broken_cnj.group(6),
	'num_unico':clean_cnj
	}
	
	return params

def get_lawsuit(cnj):
	print('Fazendo requisicao do processo')
	url = 'http://www.tjpi.jus.br/e-tjpi/consulta_processo.php'
	params = get_params(cnj)
	response = requests.get(url,params=params,verify=False)
	#precisa colocar o verify nesse caso pq a url so eh http e nao https
	lawsuit = parser(response.content)
	
	
	return lawsuit

def parser(data):
	print('Filtrando as informacoes')
	parsed = BeautifulSoup(data,'html.parser')
	text = parsed.text
	lawsuit = {
	'number': get_number(text),
	'nature': get_element(parsed,'Natureza'),
	'reporter': get_element(parsed,'Relator'),
	'value': get_element(parsed, 'Valor da Causa'),
	'_class': get_element_list(parsed, 'Classe Processual'),
	'subject': get_element_list(parsed, 'Assuntos'),
	'activity_list': get_activity_list(parsed),
	'get_people': get_people(parsed)
	}
	
	return parsed.text

def get_number(data):
	print('Extraindo o numero do processo')

	result = re.search(r'\d{7}-\d{2}.\d{4}.\d.\d{2}.\d{4}',data)
	if result: 
		return result.group()	

def get_element(data,field):
	head = data.find('dt',text=field)
	next_element = head.find_next_sibling()

	return next_element.text 

def get_element_list(data,field):
	element = get_element(data,field)
	
	return element.split('>')

def get_activity_list(data):
	activity_list = []
	activity_table = data.find('div',id='movimentacoes')	
	activity_tbody = activity_table.find('tbody')
	trs = activity_tbody.find_all('tr')
	for tr in trs:
		tds = tr.find_all('td')
		date_role = normalize_text(tds[1].text)
		date = extract_by_regex(re.compile(r'(\d{2}/\d{2}/\d{2,4})',date_role))
		activity = {
		'date': date,
		'text': normalize_text(tds[2].text)
		}
		activity_list.append(activity)
	
	return	activity_list

def normalize_text(text):

	return text.replace('\n','').replace('\t','').strip()
# sempre que for pegar os dados na html o parametro eh data,
# quando for usar o regex, usa text	

def get_people(data):
	related_people = []
	people_table = data.find('div', id='partes')
	dls = people_table.find_all('dl')
	for dl in dls:
		dts = dl.find_all('dt')
		for dt in dts:
			role = dt.text
			parties = dt.findNext('ul')
			people = parties.find_all('li')
			for li in people:
				person = {
				'name': normalize_text(li.text),
				'role': role
				}
				related_people.append(person)
	lawyers = get_lawyers(people_table)
	related_people.extend(lawyers)
# diferenca entre append e extend. append nao serve para listas, apenas unico item.
	return related_people

def get_lawyers(data):
	lawyers = []
	lawyers_table = data.find_all('fieldset')[-1]
	lawyers_list = lawyers_table.find_all('li')
	for li in lawyers_list:
		lawyer = {
		'name': normalize_text(li.text),
		'role': 'Advogado(a)'
		}
		lawyers.append(lawyer)

	return lawyers
		
def extract_by_regex(regex,data):

	result = regex.search(data,re.IGNORECASE)
	if result:
		
		return result.group(1).strip()	


print(get_lawsuit('0002508-53.2014.8.18.0000'))