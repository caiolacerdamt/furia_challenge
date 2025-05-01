import re
from app.firebase.firebase_admin import db_firebase
import time
from playwright.sync_api import sync_playwright

class ScraperWhatsappCalendar:
    def __init__(self, contato="FURIA", numero=None):
        self.contato = contato
        self.numero = numero
        self.db = db_firebase

    def limpar_calendario_anterior(self):
        try:
            docs = self.db.collection("calendario").stream()
            for doc in docs:
                doc.reference.delete()
            print("Todos os eventos antigos foram removidos com sucesso.")
        except Exception as e:
            print(f"Erro ao limpar eventos anteriores: {e}")

    def processar_calendario(self, calendario_texto):
        eventos = []
        data_atual = None

        linhas = calendario_texto.split("\n")
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue

            if re.match(r"\d{2}/\d{2}/\d{4}", linha):
                data_atual = linha
                continue

            match = re.match(r"(\d{2}h\d{2}) - \[(.*?)\] (.+)", linha)
            if match and data_atual:
                hora = match.group(1)
                jogo = match.group(2)
                evento_nome = match.group(3)

                evento = {
                    "evento_nome": evento_nome,
                    "jogo": jogo,
                    "data": data_atual,
                    "hora": hora,
                }
                eventos.append(evento)

        return eventos


    def salvar_no_firestore(self, eventos):
        for evento in eventos:
            try:
                doc_ref = self.db.collection("calendario").document() 
                doc_ref.set(evento)  
                print(f"Evento {evento['evento_nome']} salvo com sucesso!")
            except Exception as e:
                print(f"Erro ao salvar evento {evento['evento_nome']}: {e}")

    def get_calendar_from_whatsapp(self):
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir="./whatsapp_profile",
                headless=False
            )
            page = browser.new_page()
            page.goto("https://web.whatsapp.com")

            print("Aguardando login no WhatsApp...")
            page.wait_for_selector("div[aria-label='Search input textbox']", timeout=0)

            search_box = page.locator("div[aria-label='Search input textbox']")
            search_box.click()

            if self.numero:
                formatted_num = self.numero.replace("+", "").replace(" ", "").replace("-", "")
                search_box.fill(formatted_num)
                time.sleep(2)
                try:
                    contato_result = page.locator(f"span[title='{self.numero}']").first
                    contato_result.wait_for(timeout=5000)
                    contato_result.click()
                    print(f"Contato encontrado pelo número: {self.numero}")
                except Exception:
                    print(f"Contato não encontrado pelo número: {self.numero}. Tentando pelo nome...")
                    search_box.fill(self.contato)
                    time.sleep(2)
                    contato_result = page.locator(f"span[title='{self.contato}']").first
                    contato_result.wait_for(timeout=10000)
                    contato_result.click()
                    print(f"Contato encontrado pelo nome: {self.contato}")
            else:
                search_box.fill(self.contato)
                time.sleep(2)
                contato_result = page.locator(f"span[title='{self.contato}']").first
                contato_result.wait_for(timeout=10000)
                contato_result.click()
                print(f"Contato encontrado pelo nome: {self.contato}")

            time.sleep(2)

            msg_box = page.locator("div[aria-label='Type a message']")
            msg_box.click()

            msg_box.fill("Boa tarde")
            page.keyboard.press("Enter")
            print("Mensagem 'Boa Tarde' enviada, aguardando resposta...")
            time.sleep(15)

            msg_box.fill("Ver calendário")
            page.keyboard.press("Enter")
            print("Mensagem 'Ver calendário' enviada, aguardando resposta...")
            time.sleep(30) 

            mensagens = page.query_selector_all("div.message-in")
            ultimas_msg = [msg.inner_text() for msg in mensagens[-3:]]

            texto_completo = "\n".join(ultimas_msg)
            print("Texto completo unificado:")
            print(texto_completo)
            eventos = self.processar_calendario(texto_completo)

            self.limpar_calendario_anterior()

            print(f"Calendário processado: {eventos}")
            self.salvar_no_firestore(eventos)

            browser.close()
            return eventos

if __name__ == "__main__":
    numero = "+55 11 99340-4466"
    scraper = ScraperWhatsappCalendar(contato="FURIA", numero=numero) 
    calendario = scraper.get_calendar_from_whatsapp()
    print("Calendário processado e salvo no Firestore!")
