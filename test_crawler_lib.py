from SAR_Crawler_lib import SAR_Wiki_Crawler
import lxml
import json

if __name__ == "__main__":
    crawler = SAR_Wiki_Crawler()
    url_ini = "https://es.wikipedia.org/wiki/Videojuego"
    (text, urls) = crawler.get_wikipedia_entry_content(url_ini)
    resultado = crawler.parse_wikipedia_textual_content(text, url_ini)
    with open("hola.json", mode="+w", encoding="utf-8") as fl:
        json.dump(resultado, fp=fl)
    # for section in resultado["sections"]:
    #     print(section)
