"""
Busca, dentro dos testes já existentes no repositório, os trechos mais
parecidos com o código alterado no PR — para a IA seguir o estilo do
projeto ao gerar novos testes, em vez de inventar um padrão do zero.

Implementação enxuta com TF-IDF (sem dependência de serviço externo de
embeddings), suficiente para repositórios pequenos/médios. Para bases
maiores, trocar por um banco vetorial (ex: ChromaDB) é o próximo passo.
"""
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def carregar_testes_existentes(pasta_testes: str = "tests") -> list[dict]:
    arquivos = list(Path(pasta_testes).glob("**/*.py"))
    documentos = []
    for arquivo in arquivos:
        conteudo = arquivo.read_text(encoding="utf-8", errors="ignore")
        if conteudo.strip():
            documentos.append({"caminho": str(arquivo), "conteudo": conteudo})
    return documentos


def buscar_contexto_similar(diff_texto: str, pasta_testes: str = "tests", top_k: int = 3) -> str:
    """Retorna os trechos de teste mais similares ao diff, concatenados."""
    documentos = carregar_testes_existentes(pasta_testes)
    if not documentos:
        return "Nenhum teste existente encontrado — siga convenções padrão do pytest."

    textos = [d["conteudo"] for d in documentos] + [diff_texto]
    vetorizador = TfidfVectorizer(max_features=2000)
    matriz = vetorizador.fit_transform(textos)

    similaridades = cosine_similarity(matriz[-1], matriz[:-1]).flatten()
    indices_top = similaridades.argsort()[::-1][:top_k]

    trechos = []
    for i in indices_top:
        if similaridades[i] > 0:
            trechos.append(f"# Exemplo de: {documentos[i]['caminho']}\n{documentos[i]['conteudo'][:1500]}")

    return "\n\n---\n\n".join(trechos) if trechos else "Nenhum teste similar encontrado."


if __name__ == "__main__":
    import sys
    diff = Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else ""
    print(buscar_contexto_similar(diff))
