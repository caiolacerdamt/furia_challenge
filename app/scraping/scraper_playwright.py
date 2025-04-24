from playwright.sync_api import sync_playwright
from app.firebase.firebase_admin import salvar_jogadores, salvar_dados

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

def extrair_jogadores(url):
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

if __name__ == "__main__":
    for url in urls:
        team_id = url.split("/")[-1] 
        jogo = url.split("/")[5]
        jogadores = extrair_jogadores(url)
        salvar_jogadores(jogadores, team_id, jogo)
        print(f"{len(jogadores)} jogadores salvos para o time '{team_id}' no jogo '{jogo}'")
        salvar_dados(urls)