from SAR_Crawler_lib import SAR_Wiki_Crawler
import lxml
if __name__ == "__main__":
    crawler = SAR_Wiki_Crawler()
    url_ini = "https://es.wikipedia.org/wiki/Videojuego"
    (text, urls) = crawler.get_wikipedia_entry_content(url_ini)
    resultado = crawler.parse_wikipedia_textual_content(text, url_ini)
    print(resultado)
