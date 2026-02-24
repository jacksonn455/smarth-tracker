from datetime import datetime
import calendar
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

class Ponto:
    def __init__(self, driver, user, password, contrato):
        self.driver = driver
        self.user = user
        self.password = password
        self.contrato = contrato

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
        # Aguarda o loading desaparecer antes de interagir com os elementos
        print('     Aguardando loading desaparecer')

        # Espera múltipla: invisibilidade E que o display seja 'none'
        WebDriverWait(self.driver, 15).until(
            EC.invisibility_of_element_located((By.ID, "loading-container"))
        )

        # Aguarda extra para garantir que o loading realmente desapareceu
        time.sleep(1)

        # Verifica se o loading realmente está invisível
        try:
            loading = self.driver.find_element(By.ID, "loading-container")
            display = loading.value_of_css_property("display")
            print(f'     Loading display: {display}')

            # Se ainda estiver visível, aguarda mais
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

        # Usa JavaScript para clicar, evitando problemas de interceptação
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

        # Verifica se apareceu um modal com botão OK e clica nele
        print('     Verificando se há modal de confirmação...')

        try:
            botao_ok = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.sa-confirm-button-container button.confirm")
                )
            )

            print('     Modal encontrado - Clicando no botão OK')
            botao_ok.click()

            # Aguarda o modal desaparecer antes de continuar
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element(botao_ok)
            )

            print('     Modal fechado - Continuando fluxo')

        except TimeoutException:
            print('     Nenhum modal encontrado - Continuando normalmente')

        print('     Centro de Custo / Unidade')
        centro_custo = WebDriverWait(self.driver, 10).until(
            lambda d: next(
                (el for el in d.find_elements(By.CSS_SELECTOR, "campo-consulta-centro-custo input.code")
                 if el.is_displayed() and not el.get_attribute("disabled")), None
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", centro_custo)
        ActionChains(self.driver).move_to_element(centro_custo).click().perform()
        time.sleep(0.3)
        centro_custo.clear()
        centro_custo.send_keys("3")
        WebDriverWait(self.driver, 5).until(
            lambda d: centro_custo.get_attribute('value') == '3'
        )
        time.sleep(0.5)

        print('     Contrato')
        contrato_el = WebDriverWait(self.driver, 10).until(
            lambda d: next(
                (el for el in d.find_elements(By.CSS_SELECTOR, "campo-consulta-contrato input.code")
                 if el.is_displayed() and not el.get_attribute("disabled")), None
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contrato_el)
        ActionChains(self.driver).move_to_element(contrato_el).click().perform()
        time.sleep(0.3)
        contrato_el.clear()
        contrato_el.send_keys(self.contrato)
        WebDriverWait(self.driver, 5).until(
            lambda d: contrato_el.get_attribute('value') == self.contrato
        )
        time.sleep(0.5)

        print('     Tipo de Atividade')
        tipo_atividade = WebDriverWait(self.driver, 10).until(
            lambda d: next(
                (el for el in d.find_elements(By.CSS_SELECTOR, "campo-consulta-tipo-atividade input.code")
                 if el.is_displayed() and not el.get_attribute("disabled")), None
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tipo_atividade)
        ActionChains(self.driver).move_to_element(tipo_atividade).click().perform()
        time.sleep(0.3)
        tipo_atividade.clear()
        tipo_atividade.send_keys("1")
        WebDriverWait(self.driver, 5).until(
            lambda d: tipo_atividade.get_attribute('value') == '1'
        )
        time.sleep(0.5)

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

        # Aguarda o valor estar presente
        WebDriverWait(self.driver, 5).until(
            lambda d: campo_data.get_attribute('value') == primeiro_dia
        )
        time.sleep(1)

        print("até")

        ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
        data_final = hoje.replace(day=ultimo_dia).strftime("%Y-%m-%d")
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

        # Aguarda o valor estar presente
        WebDriverWait(self.driver, 5).until(
            lambda d: campo_data_final.get_attribute('value') == data_final
        )
        time.sleep(1)

        print("Clicando em Incluir")

        botao_incluir = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//span[contains(text(),'Incluir')]]")
            )
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", botao_incluir)
        time.sleep(1)

        self.driver.execute_script("arguments[0].click();", botao_incluir)

        # Aguarda o formulário de cadastro aparecer
        print('     Aguardando formulário de cadastro...')
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form.form-dados"))
        )
        time.sleep(1)

    def _preencher_campo_consulta(self, css_seletor, valor, nome_campo):
        """
        Encontra o input.code dentro do seletor, move o mouse até ele,
        clica, digita o valor e dispara o blur para abrir o modal.
        Depois aguarda o modal e clica no primeiro resultado.
        """
        print(f'     {nome_campo}')

        # Pega todos os elementos e filtra o que está visível e habilitado
        elementos = self.driver.find_elements(By.CSS_SELECTOR, css_seletor)
        campo = None
        for el in elementos:
            if el.is_displayed() and not el.get_attribute("disabled"):
                campo = el
                break

        if not campo:
            print(f'     ERRO: campo {nome_campo} não encontrado ou desabilitado')
            return

        # Scroll até o elemento
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
        time.sleep(0.5)

        # Usa ActionChains para mover o mouse até o elemento e clicar
        actions = ActionChains(self.driver)
        actions.move_to_element(campo).click().perform()
        time.sleep(0.5)

        # Limpa e digita
        campo.clear()
        time.sleep(0.3)
        campo.send_keys(valor)
        print(f'     Valor digitado: {valor}')
        time.sleep(1)

        # Dispara o blur para acionar ng-blur -> abrirModalConsulta()
        self.driver.execute_script("""
            var el = arguments[0];
            el.blur();
            el.dispatchEvent(new FocusEvent('blur', { bubbles: true }));
        """, campo)
        print(f'     Blur disparado, aguardando modal...')
        time.sleep(1)

        # Aguarda o modal aparecer
        try:
            WebDriverWait(self.driver, 8).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content, div[role='dialog']"))
            )
            print(f'     Modal aberto')
            time.sleep(1)

            # Clica no primeiro resultado
            primeiro = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "(//div[contains(@class,'modal-content') or @role='dialog']//tbody/tr)[1]"
                ))
            )
            self.driver.execute_script("arguments[0].click();", primeiro)
            print(f'     Primeiro resultado selecionado')
            time.sleep(1)

            # Aguarda modal fechar
            WebDriverWait(self.driver, 8).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.modal-content, div[role='dialog']"))
            )
            print(f'     Modal fechado')

        except TimeoutException:
            print(f'     Modal não apareceu, continuando...')

        # Confirma se a descrição foi preenchida
        try:
            desc_css = css_seletor.replace("input.code", "input.content")
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_element(By.CSS_SELECTOR, desc_css).get_attribute('value') != ''
            )
            desc = self.driver.find_element(By.CSS_SELECTOR, desc_css).get_attribute('value')
            print(f'     {nome_campo} confirmado: {desc}')
        except:
            print(f'     {nome_campo}: descrição ainda não preenchida')

    def cadastrar(self):
        print('     Aguardando formulário estar pronto...')

        # Aguarda o formulário de cadastro estar visível e ativo
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form.form-dados"))
        )
        time.sleep(1)

        # Preenche cada campo de consulta usando o helper
        self._preencher_campo_consulta(
            "campo-consulta-centro-custo input.code", "3", "Centro de Custo / Unidade"
        )

        print('     Cliente')
        try:
            clientes = self.driver.find_elements(By.CSS_SELECTOR, "campo-consulta-pessoa input.code")
            for c in clientes:
                if c.is_displayed():
                    val = c.get_attribute('value')
                    print(f'     Cliente preenchido com: {val}')
                    break
        except Exception as e:
            print(f'     Erro ao verificar Cliente: {e}')

        self._preencher_campo_consulta(
            "campo-consulta-contrato input.code", self.contrato, "Contrato"
        )

        self._preencher_campo_consulta(
            "campo-consulta-tipo-atividade input.code", "1", "Tipo de Atividade"
        )

        print('     Data')
        try:
            data_inputs = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Data'] input[type='date']")
            data_input = next((el for el in data_inputs if el.is_displayed() and not el.get_attribute("disabled")), None)
            if data_input:
                self.driver.execute_script("""
                    arguments[0].value = '2026-02-23';
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur',  { bubbles: true }));
                """, data_input)
                WebDriverWait(self.driver, 5).until(
                    lambda d: data_input.get_attribute('value') == '2026-02-23'
                )
                print('     Data preenchida com sucesso')
                time.sleep(1)
        except Exception as e:
            print(f'     Erro ao preencher Data: {e}')

        print('     Hora Início')
        hi = None
        try:
            hi_inputs = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Hora Início'] input[type='time']")
            hi = next((el for el in hi_inputs if el.is_displayed() and not el.get_attribute("disabled")), None)
            if hi:
                # Clica, limpa e digita usando ActionChains para garantir foco real
                ActionChains(self.driver).move_to_element(hi).click().perform()
                time.sleep(0.3)
                self.driver.execute_script("""
                    var el = arguments[0];
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(el, '09:00');
                    el.dispatchEvent(new Event('input',  { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                """, hi)
                WebDriverWait(self.driver, 5).until(lambda d: hi.get_attribute('value') == '09:00')
                print('     Hora Início preenchida com sucesso')
                # Dispara blur real para acionar ng-blur -> definirHoraFim / calcularTotalHoras
                hi.send_keys('\t')
                time.sleep(1)
        except Exception as e:
            print(f'     Erro ao preencher Hora Início: {e}')

        print('     Hora Fim')
        hf = None
        try:
            hf_inputs = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Hora Fim'] input[type='time']")
            hf = next((el for el in hf_inputs if el.is_displayed() and not el.get_attribute("disabled")), None)
            if hf:
                ActionChains(self.driver).move_to_element(hf).click().perform()
                time.sleep(0.3)
                self.driver.execute_script("""
                    var el = arguments[0];
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(el, '12:00');
                    el.dispatchEvent(new Event('input',  { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                """, hf)
                WebDriverWait(self.driver, 5).until(lambda d: hf.get_attribute('value') == '12:00')
                print('     Hora Fim preenchida com sucesso')
                # Dispara blur real para acionar ng-blur -> calcularTotalHoras
                hf.send_keys('\t')
                time.sleep(1)
        except Exception as e:
            print(f'     Erro ao preencher Hora Fim: {e}')

        print('     Total Horas')
        try:
            th_inputs = self.driver.find_elements(By.CSS_SELECTOR, "form-field[label='Total Horas'] input[type='time']")
            th = next((el for el in th_inputs if el.is_displayed()), None)

            # Aguarda até 5s para ver se foi calculado automaticamente
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: th.get_attribute('value') not in ('', None)
                )
                print(f'     Total Horas calculado automaticamente: {th.get_attribute("value")}')
            except TimeoutException:
                # Não foi calculado, preenche manualmente (03:00 = 12:00 - 09:00)
                print('     Total Horas não calculado, preenchendo manualmente...')
                ActionChains(self.driver).move_to_element(th).click().perform()
                time.sleep(0.3)
                self.driver.execute_script("""
                    var el = arguments[0];
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(el, '03:00');
                    el.dispatchEvent(new Event('input',  { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                """, th)
                WebDriverWait(self.driver, 5).until(lambda d: th.get_attribute('value') == '03:00')
                th.send_keys('\t')
                print(f'     Total Horas preenchido manualmente: 03:00')
                time.sleep(1)
        except Exception as e:
            print(f'     Erro ao preencher Total Horas: {e}')
            time.sleep(1)

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
                print('     Descrição preenchida com sucesso')
                time.sleep(1)
        except Exception as e:
            print(f'     Erro ao preencher Descrição: {e}')

        print('     Aguardando antes de salvar...')
        time.sleep(1)

        print('     Clicando em Salvar')
        try:
            salvares = self.driver.find_elements(By.XPATH, "//button[.//span[contains(text(),'Salvar')]]")
            salvar = next((el for el in salvares if el.is_displayed()), None)
            if salvar:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", salvar)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", salvar)

                print('     Aguardando confirmação de salvamento...')
                time.sleep(1)

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
                    print('     Modal confirmado')
                    WebDriverWait(self.driver, 5).until(EC.invisibility_of_element(modal))
                    time.sleep(1)
                except TimeoutException:
                    print('     Nenhum modal de confirmação detectado')

        except Exception as e:
            print(f'     Erro ao clicar em Salvar: {e}')

        print('     Processo de cadastro finalizado')
        time.sleep(1)

