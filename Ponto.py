from datetime import datetime, timedelta
import calendar
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class Ponto:
    def __init__(self, driver, user, password, contrato, centro_custo="3"):
        self.driver = driver
        self.user = user
        self.password = password
        self.contrato = contrato
        self.centro_custo = centro_custo

    def __str__(self):
        return str(self.driver)

    def logar(self):
        print('PAGINA INICIAL')
        self.driver.get("https://srvmk01.kuriermeridio.com.br/boldbrasil/#/")
        time.sleep(1)

        print('     Inserindo usuario e senha')
        usuario = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "user"))
        )
        usuario.send_keys(self.user)
        time.sleep(1)

        senha = self.driver.find_element(By.ID, "password")
        senha.send_keys(self.password)
        time.sleep(1)

        print('     Clicando no botao para logar')
        botao = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        botao.click()
        time.sleep(1)

    def listar(self):
        print('     Aguardando loading desaparecer')
        WebDriverWait(self.driver, 15).until(
            EC.invisibility_of_element_located((By.ID, "loading-container"))
        )
        time.sleep(1)

        try:
            loading = self.driver.find_element(By.ID, "loading-container")
            display = loading.value_of_css_property("display")
            print(f'     Loading display: {display}')
            if display != "none":
                print('     Loading ainda visível, aguardando mais...')
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.find_element(By.ID, "loading-container").value_of_css_property("display") == "none"
                )
                time.sleep(1)
        except:
            pass

        print('     Clicando no menu')
        botao_ponto = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span[ng-click='validarHome();']"))
        )
        self.driver.execute_script("arguments[0].click();", botao_ponto)
        time.sleep(1)

        print('     Clicando no relogio')
        relogio = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@ng-click='abrirPagina(option)']//span[contains(text(),'Registrar Atividades no Timesheet')]"
            ))
        )
        relogio.click()
        time.sleep(1)

        print('     Verificando se há modal de confirmação...')
        try:
            botao_ok = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.sa-confirm-button-container button.confirm")
                )
            )
            print('     Modal encontrado - Clicando no botão OK')
            botao_ok.click()
            WebDriverWait(self.driver, 5).until(EC.invisibility_of_element(botao_ok))
            print('     Modal fechado - Continuando fluxo')
        except TimeoutException:
            print('     Nenhum modal encontrado - Continuando normalmente')

        # --- Filtro: Centro de Custo ---
        print('     Centro de Custo / Unidade')
        self._preencher_input_consulta_js(
            "campo-consulta-centro-custo input.code", self.centro_custo
        )

        # --- Filtro: Contrato ---
        print('     Contrato')
        self._preencher_input_consulta_js(
            "campo-consulta-contrato input.code", self.contrato
        )

        # --- Filtro: Tipo de Atividade ---
        print('     Tipo de Atividade')
        self._preencher_input_consulta_js(
            "campo-consulta-tipo-atividade input.code", "1"
        )

        # --- Data "A partir de": primeiro dia do mês ---
        print("A partir de")
        hoje = datetime.today()
        primeiro_dia = hoje.replace(day=1).strftime("%Y-%m-%d")

        campo_data = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(),'A partir de')]/following::input[@type='date'][1]")
            )
        )
        self.driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, campo_data, primeiro_dia)
        WebDriverWait(self.driver, 5).until(
            lambda d: campo_data.get_attribute('value') == primeiro_dia
        )
        time.sleep(1)

        # --- Data "até": último dia do mês vigente ---
        print("até")
        ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month)[1]
        data_final = hoje.replace(day=ultimo_dia_num).strftime("%Y-%m-%d")
        print(f'     Data final calculada: {data_final}')

        campo_data_final = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "(//input[@type='date'])[2]")
            )
        )
        self.driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, campo_data_final, data_final)
        WebDriverWait(self.driver, 5).until(
            lambda d: campo_data_final.get_attribute('value') == data_final
        )
        time.sleep(1)

        # --- Clica em Incluir para abrir o formulário ---
        print("Clicando em Incluir")
        botao_incluir = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//span[contains(text(),'Incluir')]]")
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", botao_incluir)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", botao_incluir)

        print('     Aguardando formulário de cadastro...')
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form.form-dados"))
        )
        time.sleep(1)

    # ------------------------------------------------------------------
    # Helper: preenche um input.code via JS (evita ElementNotInteractable)
    # Usado apenas nos filtros da tela de listagem (não abre modal)
    # ------------------------------------------------------------------
    def _preencher_input_consulta_js(self, css_seletor, valor):
        """Seta o valor de um input.code via JS sem abrir modal (para filtros)."""
        campo = WebDriverWait(self.driver, 10).until(
            lambda d: next(
                (el for el in d.find_elements(By.CSS_SELECTOR, css_seletor)
                 if el.is_displayed() and not el.get_attribute("disabled")), None
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", campo)
        time.sleep(0.3)
        self.driver.execute_script("""
            var el = arguments[0];
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            setter.call(el, arguments[1]);
            el.dispatchEvent(new Event('input',  { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, campo, valor)
        time.sleep(0.3)

    # ------------------------------------------------------------------
    # Helper: preenche um campo de consulta NO FORMULÁRIO DE CADASTRO
    # Clica no input.code, digita, dispara blur, aguarda modal e seleciona
    # ------------------------------------------------------------------
    def _preencher_campo_consulta(self, css_seletor, valor, nome_campo):
        print(f'     {nome_campo}')

        campo = WebDriverWait(self.driver, 15).until(
            lambda d: next(
                (el for el in d.find_elements(By.CSS_SELECTOR, css_seletor)
                 if el.is_displayed() and not el.get_attribute("disabled")), None
            )
        )
        if not campo:
            print(f'     ERRO: campo {nome_campo} não encontrado ou desabilitado')
            return

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", campo)
        time.sleep(0.3)

        # Clica via JS para garantir foco no contexto Angular
        self.driver.execute_script("arguments[0].click(); arguments[0].focus();", campo)
        time.sleep(0.3)

        # Digita o valor diretamente no elemento com foco
        campo.send_keys(Keys.CONTROL + "a")
        campo.send_keys(Keys.DELETE)
        time.sleep(0.2)
        campo.send_keys(valor)
        print(f'     Valor digitado: {valor}')
        time.sleep(0.8)

        # Pressiona Tab para acionar ng-blur -> resolve o campo automaticamente
        campo.send_keys(Keys.TAB)
        time.sleep(0.3)

        # Confirma se a descrição foi preenchida
        try:
            desc_css = css_seletor.replace("input.code", "input.content")
            desc = WebDriverWait(self.driver, 5).until(
                lambda d: d.find_element(By.CSS_SELECTOR, desc_css).get_attribute('value') or None
            )
            print(f'     {nome_campo} confirmado: {desc}')
        except:
            print(f'     {nome_campo}: descrição ainda não preenchida')

    # ------------------------------------------------------------------
    # Preenche uma sessão completa do formulário de cadastro e salva
    # data_str: "YYYY-MM-DD"
    # hora_inicio_str / hora_fim_str: "HH:MM"
    # primeiro_registro: se True, preenche também cliente/centro/contrato/tipo
    # ------------------------------------------------------------------
    def _cadastrar_sessao(self, data_str, hora_inicio_str, hora_fim_str, primeiro_registro=False):
        print(f'\n     === Cadastrando {data_str} {hora_inicio_str}-{hora_fim_str} ===')

        print('     Aguardando formulário estar pronto...')
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form.form-dados"))
        )
        time.sleep(1)

        # No primeiro registro do dia (manhã) precisamos preencher todos os campos;
        # nas demais sessões o formulário pode já ter sido limpo (Incluir abre um novo)
        # então sempre preenchemos tudo.

        # Centro de Custo
        self._preencher_campo_consulta(
            "campo-consulta-centro-custo input.code", self.centro_custo, "Centro de Custo / Unidade"
        )

        # Cliente: já vem pré-preenchido (código 39) — apenas verifica
        print('     Cliente')
        try:
            clientes = self.driver.find_elements(By.CSS_SELECTOR, "campo-consulta-pessoa input.code")
            for c in clientes:
                if c.is_displayed():
                    val = c.get_attribute('value')
                    if val:
                        print(f'     Cliente já preenchido com: {val}')
                    break
        except Exception as e:
            print(f'     Aviso ao verificar Cliente: {e}')

        # Contrato
        self._preencher_campo_consulta(
            "campo-consulta-contrato input.code", self.contrato, "Contrato"
        )

        # Tipo de Atividade
        self._preencher_campo_consulta(
            "campo-consulta-tipo-atividade input.code", "1", "Tipo de Atividade"
        )

        # Data
        print('     Data')
        try:
            data_inputs = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Data'] input[type='date']")
            data_input = next((el for el in data_inputs if el.is_displayed() and not el.get_attribute("disabled")), None)
            if data_input:
                self.driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input',  { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur',   { bubbles: true }));
                """, data_input, data_str)
                WebDriverWait(self.driver, 5).until(
                    lambda d: data_input.get_attribute('value') == data_str
                )
                print(f'     Data preenchida: {data_str}')
                time.sleep(0.3)
        except Exception as e:
            print(f'     Erro ao preencher Data: {e}')

        # Hora Início
        print(f'     Hora Início: {hora_inicio_str}')
        try:
            hi_inputs = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Hora Início'] input[type='time']")
            hi = next((el for el in hi_inputs if el.is_displayed() and not el.get_attribute("disabled")), None)
            if hi:
                ActionChains(self.driver).move_to_element(hi).click().perform()
                time.sleep(0.3)
                self.driver.execute_script("""
                    var el = arguments[0];
                    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(el, arguments[1]);
                    el.dispatchEvent(new Event('input',  { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                """, hi, hora_inicio_str)
                WebDriverWait(self.driver, 5).until(lambda d: hi.get_attribute('value') == hora_inicio_str)
                print(f'     Hora Início preenchida: {hora_inicio_str}')
                hi.send_keys(Keys.TAB)
                time.sleep(0.3)
        except Exception as e:
            print(f'     Erro ao preencher Hora Início: {e}')

        # Hora Fim
        print(f'     Hora Fim: {hora_fim_str}')
        try:
            hf_inputs = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Hora Fim'] input[type='time']")
            hf = next((el for el in hf_inputs if el.is_displayed() and not el.get_attribute("disabled")), None)
            if hf:
                ActionChains(self.driver).move_to_element(hf).click().perform()
                time.sleep(0.3)
                self.driver.execute_script("""
                    var el = arguments[0];
                    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(el, arguments[1]);
                    el.dispatchEvent(new Event('input',  { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                """, hf, hora_fim_str)
                WebDriverWait(self.driver, 5).until(lambda d: hf.get_attribute('value') == hora_fim_str)
                print(f'     Hora Fim preenchida: {hora_fim_str}')
                hf.send_keys(Keys.TAB)
                time.sleep(0.3)
        except Exception as e:
            print(f'     Erro ao preencher Hora Fim: {e}')

        # Total Horas: aguarda cálculo automático; se não vier, preenche manualmente
        print('     Total Horas')
        try:
            th_inputs = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Total Horas'] input[type='time']")
            th = next((el for el in th_inputs if el.is_displayed()), None)
            if th:
                try:
                    WebDriverWait(self.driver, 5).until(
                        lambda d: th.get_attribute('value') not in ('', None)
                    )
                    print(f'     Total Horas calculado: {th.get_attribute("value")}')
                except TimeoutException:
                    # Calcula a diferença e preenche manualmente
                    fmt = "%H:%M"
                    diff = datetime.strptime(hora_fim_str, fmt) - datetime.strptime(hora_inicio_str, fmt)
                    total_min = int(diff.total_seconds() // 60)
                    total_str = f"{total_min // 60:02d}:{total_min % 60:02d}"
                    print(f'     Preenchendo Total Horas manualmente: {total_str}')
                    ActionChains(self.driver).move_to_element(th).click().perform()
                    time.sleep(0.3)
                    self.driver.execute_script("""
                        var el = arguments[0];
                        var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        setter.call(el, arguments[1]);
                        el.dispatchEvent(new Event('input',  { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    """, th, total_str)
                    WebDriverWait(self.driver, 5).until(lambda d: th.get_attribute('value') == total_str)
                    th.send_keys(Keys.TAB)
                    print(f'     Total Horas preenchido: {total_str}')
                    time.sleep(0.3)
        except Exception as e:
            print(f'     Erro ao preencher Total Horas: {e}')
            time.sleep(0.3)

        # Descrição
        print('     Descrição')
        try:
            desc_els = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Descrição'] textarea")
            desc = next((el for el in desc_els if el.is_displayed() and not el.get_attribute("disabled")), None)
            if desc:
                self.driver.execute_script("arguments[0].focus();", desc)
                time.sleep(0.3)
                self.driver.execute_script("""
                    arguments[0].value = 'Trabalhando nos Projeto: kora-mms-contrato, kora-mms-localidade';
                    arguments[0].dispatchEvent(new Event('input',  { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, desc)
                WebDriverWait(self.driver, 5).until(lambda d: desc.get_attribute('value') != '')
                print('     Descrição preenchida')
                time.sleep(0.3)
        except Exception as e:
            print(f'     Erro ao preencher Descrição: {e}')

        # Salvar
        print('     Clicando em Salvar')
        time.sleep(0.3)
        try:
            salvares = self.driver.find_elements(By.XPATH, "//button[.//span[contains(text(),'Salvar')]]")
            salvar = next((el for el in salvares if el.is_displayed()), None)
            if salvar:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", salvar)
                time.sleep(0.3)
                self.driver.execute_script("arguments[0].click();", salvar)

                print('     Aguardando confirmação...')
                time.sleep(0.3)

                try:
                    modal = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.sweet-alert, div.swal2-popup"))
                    )
                    try:
                        mensagem = modal.find_element(By.CSS_SELECTOR, "h2, .swal2-title").text
                        print(f'     Modal: {mensagem}')
                    except:
                        print('     Modal detectado')
                    time.sleep(1)
                    botao_ok = modal.find_element(By.CSS_SELECTOR, "button.confirm, button.swal2-confirm")
                    self.driver.execute_script("arguments[0].click();", botao_ok)
                    print('     Salvo com sucesso!')
                    WebDriverWait(self.driver, 5).until(EC.invisibility_of_element(modal))
                    time.sleep(0.3)
                except TimeoutException:
                    print('     Nenhum modal de confirmação após salvar')

        except Exception as e:
            print(f'     Erro ao clicar em Salvar: {e}')

    # ------------------------------------------------------------------
    # Abre o formulário de um novo registro clicando em "Incluir"
    # ------------------------------------------------------------------
    def _clicar_incluir(self):
        print('\n     Clicando em Incluir para próximo registro...')
        botao_incluir = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[.//span[normalize-space()='Incluir']]"
            ))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", botao_incluir)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", botao_incluir)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form.form-dados"))
        )
        time.sleep(0.3)

    # ------------------------------------------------------------------
    # Loop principal: cadastra manhã + tarde de cada dia útil do mês
    # do dia 1 até o dia de hoje (inclusive)
    # ------------------------------------------------------------------
    def cadastrar_mes(self):
        hoje = datetime.today()
        ano = hoje.year
        mes = hoje.month
        dia_atual = hoje.day

        # Gera lista de todos os dias úteis do dia 1 até hoje
        dias_uteis = []
        dia = datetime(ano, mes, 1)
        while dia.day <= dia_atual:
            # 0=segunda ... 4=sexta, 5=sabado, 6=domingo
            if dia.weekday() < 5:
                dias_uteis.append(dia)
            dia += timedelta(days=1)

        total = len(dias_uteis)
        print(f'\n=== Cadastrando {total} dias úteis de {dias_uteis[0].strftime("%d/%m/%Y")} até {dias_uteis[-1].strftime("%d/%m/%Y")} ===\n')

        primeiro = True
        for idx, dia in enumerate(dias_uteis):
            data_str = dia.strftime("%Y-%m-%d")
            print(f'\n--- Dia {idx + 1}/{total}: {dia.strftime("%d/%m/%Y (%A)")} ---')

            # Manhã: 09:Xm → 12:Xm  (exatamente 3h, mesmo offset nos dois)
            rnd_manha = random.randint(0, 5)
            hi_manha = f"09:{rnd_manha:02d}"
            hf_manha = f"12:{rnd_manha:02d}"

            if not primeiro:
                self._clicar_incluir()
            primeiro = False

            self._cadastrar_sessao(data_str, hi_manha, hf_manha)

            # Tarde: 13:Xt → 18:Xt  (exatamente 5h, mesmo offset nos dois)
            rnd_tarde = random.randint(0, 5)
            hi_tarde = f"13:{rnd_tarde:02d}"
            hf_tarde = f"18:{rnd_tarde:02d}"

            self._clicar_incluir()
            self._cadastrar_sessao(data_str, hi_tarde, hf_tarde)

        print(f'\n=== Cadastro do mês concluído! {total * 2} registros inseridos ===')

    # ------------------------------------------------------------------
    # Mantém compatibilidade com main.py legado (cadastra apenas 1 sessão)
    # ------------------------------------------------------------------
    def cadastrar(self):
        hoje = datetime.today()
        data_str = hoje.strftime("%Y-%m-%d")
        self._cadastrar_sessao(data_str, "09:00", "12:00")

