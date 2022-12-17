from array import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from time import sleep, time
import os
import sys

from random import randrange, randint

# import certifi
import ssl
import base64
import time

##################################################
# настройки

txt_proxy = '';  # прокси если требуется

url_login = 'https://petfriends.skillfactory.ru/login';
url_pets = 'https://petfriends.skillfactory.ru/my_pets'
login = 'JabbaHutt@mail.com'
password = '12345'

##################################################

profile = webdriver.FirefoxProfile()

if txt_proxy != '':
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.socks", txt_proxy[0])
    profile.set_preference("network.proxy.socks_port", int(txt_proxy[1]))
    profile.set_preference("network.proxy.socks_version", 5)
    profile.update_preferences()

####################################################

# логинимся
print('start - запускаем браузер')

driver = webdriver.Firefox(firefox_profile=profile)

driver.get(url_login)

driver.implicitly_wait(10)  # неявное ожидание пока появится форма логина 10 сек

el = driver.find_element_by_id('email')
el.send_keys(login)

el = driver.find_element_by_id('pass')
el.send_keys(password)

print("Жмем залогиниться...")

driver.find_element_by_css_selector('.btn.btn-success').click();

####################################################

print("Переходим на страницу - мои питомцы")
driver.get(url_pets)

####################################################
# тест 1. присутствуют все питомцы

# получаем кол-во питомцев из статиски

# явное ожидание появления таблицы со статистикой
try:
    elpas = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'left')))
except:
    print('Нет таблицы со статисткой больше 10 секунд!')

buf = driver.find_element_by_css_selector('.left').get_attribute('innerHTML');
i = buf.find('Питомцев:') + 9
j = buf.find('\n', i)
# print(buf, buf[i:j])
# print(int(buf[i:j].strip()))
pets_count = int(buf[i:j].strip())

print("Кол-во Питомцев в статистике: ", pets_count)

# явное таблицы со списком животных
try:
    elpas = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody')))
except:
    print('Нет таблицы с питомцами больше 10 секунд!')

# получением кол-во строк в таблице
trs = driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
# print(trs)
print("Кол-во строк в таблице Питомцев: ", len(trs))

if (len(trs) == pets_count):
    print("Тест 1 - ПРОЙДЕН")
else:
    print("Тест 1 - ОШИБКА! Кол-во строк в таблице и число питомцев в статике не совпадает")

###################################################
# тест 2. хотябы у половины животных есть фото

# получаем все картинки из таблицы
imgs = driver.find_elements(By.CSS_SELECTOR, 'tbody tr img')
imgs_count = 0
for i in imgs:
    src = i.get_attribute('src')

    # если картинка не пустая - увеличиваем кол-во животных с фото
    if (src != ''):
        imgs_count = imgs_count + 1

print('Кол-во питомцев с фото: ', imgs_count)

if (imgs_count > pets_count / 2):
    print('тест 2. хотябы у половины животных есть фото - ПРОЙДЕН!')
else:
    print('тест 2. хотябы у половины животных есть фото - ОШИБКА!  ')

###################################################
# тест 3. у всех питомцев есть имя возраст и порода

driver.implicitly_wait(10)  # неявное ожидание 10 сек

# получаем все строки таблицы питомцев
pets = driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
flag = 1
for pet in pets:
    # в каждой строке получаем все столбцы
    tds = pet.find_elements(By.CSS_SELECTOR, 'td')
    # print(tds)

    # проверяем столбцы с именем, возрастом, породой - что не пустые
    if (tds[0].get_attribute('innerText') == '') or (tds[1].get_attribute('innerText') == '') or (
            tds[2].get_attribute('innerText') == ''):
        # если любое из полей пустое - ставим флаг, что тест не пройден и прерываем цикл
        flag = 0
        break

if (flag == 1):
    print("тест 3. у всех питомцев есть имя возраст и порода - ПРОЙДЕН!")
else:
    print("тест 3. у всех питомцев есть имя возраст и порода - ОШИБКА!")

###################################################
# тест 4. у всех питомцев разные имена

driver.implicitly_wait(10)  # неявное ожидание 10 сек

# получаем все строки таблицы питомцев
pets = driver.find_elements(By.CSS_SELECTOR, 'tbody tr')

# составляем массив имен
pet_names = []
flag = 1
for pet in pets:
    # в каждой строке получаем все столбцы
    tds = pet.find_elements(By.CSS_SELECTOR, 'td')
    # print(tds)

    name = tds[0].get_attribute('innerText')

    # проверяем что имени нет в списке ранее просканированных питомцев
    # print(pet_names.count(name)) - кол-во эл-ов в массиве с данным значением
    if (pet_names.count(name) > 0):
        # если любое из полей пустое - ставим флаг, что тест не пройден
        flag = 0

    # добавляем имя в массив
    pet_names.append(name)

print("Массив имен всех питомцев: ", pet_names)
if (flag == 1):
    print("тест 4. у всех питомцев разные имена - ПРОЙДЕН!")
else:
    print("тест 4. у всех питомцев разные имена - ОШИБКА!")

###################################################
# тест 5. в списке нет повторяющихся питомцев (одинаковые имя+порода+возраст)

driver.implicitly_wait(10)  # неявное ожидание 10 сек

# получаем все строки таблицы питомцев
pets = driver.find_elements(By.CSS_SELECTOR, 'tbody tr')

# проходим всех питомцев
pet_unics = []
flag = 1
for pet in pets:
    # в каждой строке получаем все столбцы
    tds = pet.find_elements(By.CSS_SELECTOR, 'td')
    # print(tds)

    name_age_kind = tds[0].get_attribute('innerText') + '|' + tds[1].get_attribute('innerText') + '|' + tds[
        2].get_attribute('innerText')

    # проверяем что имени нет в списке ранее просканированных питомцев
    # print(pet_names.count(name)) - кол-во эл-ов в массиве с данным значением
    if (pet_unics.count(name_age_kind) > 0):
        # если любое из полей пустое - ставим флаг, что тест не пройден
        flag = 0

    # добавляем имя в массив
    pet_unics.append(name_age_kind)

if (flag == 1):
    print("тест 5. в списке нет повторяющихся питомцев (одинаковые имя+порода+возраст) - ПРОЙДЕН!")
else:
    print("тест 5. в списке нет повторяющихся питомцев (одинаковые имя+порода+возраст) - ОШИБКА!")

# driver.close();

sys.exit();