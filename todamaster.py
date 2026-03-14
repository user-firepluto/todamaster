import time
import requests
import os
import textwrap
from bs4 import BeautifulSoup
from google import genai

API_KEY = input("Digite a sua chave de api do Gemini: ")
client = genai.Client(api_key=API_KEY)

def extrair_conteudo(url):
    print("\n[1/3] Lendo o artigo...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove lixo da página
        for noise in soup(['script', 'style', 'nav', 'footer', 'header']):
            noise.decompose()

        artigo = soup.find('article') or soup.find('body')
        paragrafos = [p.get_text().strip() for p in artigo.find_all('p') if len(p.get_text()) > 40]

        return " ".join(paragrafos)[:7000]
    except Exception as e:
        return f"Erro: {e}"


def gerar_resumo(texto):
    print("[2/3] IA criando o resumo...")
    prompt = (
            "Resuma o texto abaixo em um parágrafo único e fluido de 60 a 90 palavras. "
            "Não use tópicos, listas ou negrito (**). Texto:\n\n" + texto
    )
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        # Limpeza rigorosa de formatação Markdown que a IA possa enviar
        resumo = response.text.replace("*", "").replace("#", "").replace("_", "").strip()
        return resumo
    except Exception as e:
        return f"Erro na IA: {e}"


def imprimir_formatado(texto, titulo=""):
    """Exibe o texto quebrando as linhas de acordo com o tamanho do terminal"""
    try:
        # Pega a largura do terminal ou usa 80 como padrão
        largura = os.get_terminal_size().columns - 4
    except:
        largura = 76

    if titulo:
        print(f"\n{titulo.center(largura)}")
        print("-" * largura)

    # O textwrap.fill faz o trabalho de quebrar as linhas sem cortar palavras
    print(textwrap.fill(texto, width=largura))
    print("-" * largura)


def teste_wpm(texto_referencia):
    imprimir_formatado(texto_referencia, "TEXTO PARA DIGITAR")

    input("\nPronto? Pressione ENTER para começar...")

    print("\n" + ">>> DIGITE ABAIXO ".ljust(40, ">"))
    inicio = time.time()
    digitado = input()
    fim = time.time()

    tempo_minutos = (fim - inicio) / 60
    palavras = len(digitado.split())
    wpm = palavras / tempo_minutos if tempo_minutos > 0 else 0

    # Validação de acerto
    caracteres_certos = sum(1 for a, b in zip(digitado, texto_referencia) if a == b)
    precisao = (caracteres_certos / len(texto_referencia)) * 100 if len(texto_referencia) > 0 else 0

    print("\n" + "=" * 30)
    print(f"RESULTADO:")
    print(f"Velocidade: {wpm:.2f} WPM")
    print(f"Precisão: {precisao:.1f}%")
    print(f"Tempo: {fim - inicio:.2f} segundos")
    print("=" * 30)


def main():
    url = input("URL do Toda Matéria ou InfoEscola: ")
    if "todamateria.com.br" not in url:
        print("Use um link do Toda Matéria.")
        return

    texto_puro = extrair_conteudo(url)
    if "Erro" in texto_puro:
        print(texto_puro)
        return

    resumo = gerar_resumo(texto_puro)
    if "Erro" in resumo:
        print(resumo)
        return

    teste_wpm(resumo)


if __name__ == "__todamaster__":
    main()
