from playwright.sync_api import sync_playwright
from app.firebase.firebase_admin import db_firebase

class FuriaScraper:
    def __init__(self, urls):
        self.urls = urls

    def run(self):
        for url in self.urls:
            team_id = self.get_team_id(url)
            jogo = self.get_game(url)
            jogadores = self.extrair_jogadores(url)

            self.salvar_jogadores(jogadores, team_id, jogo)
            print(f"{len(jogadores)} jogadores salvos para o time '{team_id}' no jogo '{jogo}'")

        self.salvar_dados_gerais()

    def extrair_jogadores(self, url):
        jogadores = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(5000)

            blocos = page.query_selector_all('div.flex.flex-wrap.items-center')

            for bloco in blocos:
                try:
                    nome_display = bloco.query_selector("span.font-bold").inner_text().strip()
                    nome_completo = bloco.evaluate('el => el.nextElementSibling?.innerText', bloco)
                    link = bloco.query_selector('a').get_attribute('href')
                    link = "https://escharts.com" + link if link else ""

                    pais = bloco.query_selector("[data-tippy-content]") \
                        .get_attribute('data-tippy-content') if bloco.query_selector('[data-tippy-content]') else ""
                    
                    funcao_el = bloco.query_selector('div.tag')
                    funcao = funcao_el.inner_text().strip() if funcao_el else ""

                    jogadores.append({
                        "apelido": nome_display,
                        "nome_completo": nome_completo,
                        "país": pais,
                        "função": funcao,
                        "link": link
                    })

                except Exception as e:
                    print(f"Erro ao processar bloco: {e}")
                    continue
            
            browser.close()

        return jogadores

    def salvar_jogadores(self, jogadores, team_id, jogo):
        time_ref = db_firebase.collection("jogos").document(jogo).collection("times").document(team_id)

        for jogador in jogadores:
            apelido_id = jogador["apelido"].lower().replace(" ", "_")
            jogador_ref = time_ref.collection("jogadores").document(apelido_id)
            jogador_ref.set(jogador)

    def salvar_dados_gerais(self):
        jogos = {}

        for url in self.urls:
            jogo = self.get_game(url)
            team_id = self.get_team_id(url)

            if jogo not in jogos:
                jogos[jogo] = []
            jogos[jogo].append(team_id)

        for jogo, teams in jogos.items():
            jogo_ref = db_firebase.collection("jogos").document(jogo)
            jogo_ref.set({"times": teams}, merge=True)

    @staticmethod
    def get_team_id(url):
        return url.split("/")[-1]

    @staticmethod
    def get_game(url):
        return url.split("/")[5]


if __name__ == "__main__":
    urls = [
        "https://escharts.com/pt/teams/csgo/furia",
        "https://escharts.com/pt/teams/csgo/furiaa",
        "https://escharts.com/pt/teams/csgo/furiafem",
        "https://escharts.com/pt/teams/csgo/furia-female",
        "https://escharts.com/pt/teams/pubg/furia",
        "https://escharts.com/pt/teams/lol/furia",
        "https://escharts.com/pt/teams/lol/fura",
        "https://escharts.com/pt/teams/lol/furia-youth",
        "https://escharts.com/pt/teams/rainbow-6/furia",
        "https://escharts.com/pt/teams/valorant/furia-esports",
        "https://escharts.com/pt/teams/valorant/furia-esports-female",
        "https://escharts.com/pt/teams/valorant/furia-academy",
        "https://escharts.com/pt/teams/apex/furia",
        "https://escharts.com/pt/teams/pubg-mobile/furia-esports",
        "https://escharts.com/pt/teams/free-fire/furiafem",
        "https://escharts.com/pt/teams/fifa/furia",
        "https://escharts.com/pt/teams/rl/furia"
    ]

    scraper = FuriaScraper(urls)
    scraper.run()
