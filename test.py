import pytest
from .crawler import cnj_breaker, cnj_cleaner

def test_cnj_cleaner:
	fixture = '0002120-57.2020.8.03.0001'
	clean_number = cnj_cleaner(fixture)

	assert clean_number == '00021205720208030001'

def test_cnj_breaker:
	fixture = '0002120-57.2020.8.03.0001'	
	cnj_breaker = cnj_breaker(fixture)

	assert not cnj_breaker == 'nao achei'
	assert cnj_breaker.group() = fixture