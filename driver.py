# Imports por ter sido feito no python 2.7
from __future__ import absolute_import
from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import datetime
import time

class Driver(webdriver.Chrome):
    def __init__(self, path, options):
        service = Service(path)
        super().__init__(service=service, options=options)
        self.actions = ActionChains(self)

    # LocalStorage

    # Adicionar chave
    def localStorageAdd(self, key, value):
        print(datetime.datetime.now(), ' - Adicionando chave "'+key+'"ao LocalStorage')
        self.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)
        pass

    # Pegar chave
    def localStorageGet(self, key):
        return self.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    # Pegar todos os dados
    def localStorageGetItems(self) :
        return self.execute_script( \
            "var ls = window.localStorage, items = {}; " \
            "for (var i = 0, k; i < ls.length; ++i) " \
            "  items[k = ls.key(i)] = ls.getItem(k); " \
            "return items; ")

    # Pegar nomes das chaves existentes
    def localStorageKeys(self) :
        return self.execute_script( \
            "var ls = window.localStorage, keys = []; " \
            "for (var i = 0; i < ls.length; ++i) " \
            "  keys[i] = ls.key(i); " \
            "return keys; ")

    # Verificar se existe uma chave
    def LocalStorageHas(self, key):
        return key in self.localStorageKeys()

    # Remover uma chave
    def LocalStorageRemove(self, key):
        self.execute_script("window.localStorage.removeItem(arguments[0]);", key)

    # Limpar
    def LocalStorageClear(self):
        self.execute_script("window.localStorage.clear();")


    # Waits
    def waitForSelector(self, selector):
        try:
            element = WebDriverWait(self, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except:
            print("Elemento nao encontrado!")
        pass

    def waitForXPATH(self, xpath):
        try:
            element = WebDriverWait(self, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except:
            print("Elemento nao encontrado!")
        pass

    def waitForInvisibility(self, selector):
        try:
            element = WebDriverWait(self, 60).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except:
            print("Elemento ainda presente!")

    # Compare
    def canvasDataCompare(self, original, x, y, timeout):
        encountered = False
        for i in range(0, timeout):
            data = self.execute_script( \
            "og = document.querySelector('canvas');" \
            "parte = document.createElement('canvas');" \
            "parte.height = 50;" \
            "parte.width = 50;" \
            "parte.getContext('2d').drawImage(og,arguments[0],arguments[1],50,50,0,0,50,50);"
            "return parte.toDataURL();", x, y)
            if data == original:
                encountered = True
                break
            time.sleep(1)

        return encountered

    def waitForCanvas(self, original, x, y, timeout = 25):
        result = self.canvasDataCompare(original, x, y, timeout)
        if not result:
            print('Elemento nao encontrado no canvas')
            raise Exception()

    def isReady(self):
        return self.execute_script('return document.readyState;')

    # Exit
    # Fecha o browser instantaneamente
    def exit(self):
        self.quit()


# Define as opcoes do navegador
options = Options()
#options.add_argument("--disable-extensions")
options.add_argument("--start-maximized")
#options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36')
options.add_argument('--window-size=1250,1095')

# Instancia um novo driver (Selenium 4+ gerencia o chromedriver automaticamente)
driver = webdriver.Chrome(options=options)
