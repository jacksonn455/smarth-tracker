# main.py

import os
from dotenv import load_dotenv
from driver import driver
from Ponto import Ponto

load_dotenv()

def start():
    usuario = os.getenv("USER")
    senha = os.getenv("PASSWORD")
    contrato = os.getenv("CONTRATO")

    if not usuario or not senha:
        raise ValueError("Erro: USER e PASSWORD devem estar definidos no arquivo .env")

    if not contrato:
        raise ValueError("Erro: CONTRATO deve estar definido no arquivo .env")

    step = Ponto(driver, usuario, senha, contrato)
    step.logar()
    step.listar()
    step.cadastrar()

if __name__ == "__main__":
    start()