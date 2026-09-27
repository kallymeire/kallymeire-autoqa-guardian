"""
Envia o diff de um Pull Request + contexto de testes existentes (RAG)
para a API da Claude, e grava:
  - um arquivo de teste gerado (quality gate roda o pytest sobre ele)
  - um resumo de riscos em Markdown (comentado automaticamente no PR)
"""
import argparse
import os
from pathlib import Path

import anthropic

from rag_context import buscar_contexto_similar

PROMPT_SISTEMA = """Você é um revisor de qualidade de código sênior.
Analise o diff de um Pull Request e produza duas saídas, claramente
separadas pelos marcadores abaixo:

===TESTES===
<código Python de testes pytest para os trechos do diff que não têm
cobertura, seguindo o estilo dos exemplos de contexto fornecidos>

===RESUMO===
<resumo em markdown, em português, com bullets curtos: riscos
identificados, trechos sem tratamento de erro, e o que os testes
gerados cobrem>
"""


def analisar(diff_texto: str, contexto_rag: str) -> tuple[str, str]:
    cliente = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    mensagem = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=PROMPT_SISTEMA,
        messages=[{
            "role": "user",
            "content": (
                f"## Contexto de testes existentes no repositório\n{contexto_rag}\n\n"
                f"## Diff do Pull Request\n```diff\n{diff_texto}\n```"
            ),
        }],
    )

    texto = "".join(bloco.text for bloco in mensagem.content if bloco.type == "text")

    testes = texto.split("===TESTES===")[1].split("===RESUMO===")[0].strip() if "===TESTES===" in texto else ""
    resumo = texto.split("===RESUMO===")[1].strip() if "===RESUMO===" in texto else texto

    return testes, resumo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff", required=True, help="Caminho do arquivo .diff/.patch")
    parser.add_argument("--out", default="tests/test_generated.py")
    parser.add_argument("--summary", default="risk_summary.md")
    parser.add_argument("--pasta-testes", default="tests")
    args = parser.parse_args()

    diff_texto = Path(args.diff).read_text(encoding="utf-8", errors="ignore")
    if not diff_texto.strip():
        Path(args.summary).write_text("Nenhuma alteração detectada no diff.")
        return

    contexto = buscar_contexto_similar(diff_texto, pasta_testes=args.pasta_testes)
    testes, resumo = analisar(diff_texto, contexto)

    if testes:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(testes, encoding="utf-8")

    Path(args.summary).write_text(resumo, encoding="utf-8")
    print(f"Testes gerados em: {args.out}")
    print(f"Resumo gerado em: {args.summary}")


if __name__ == "__main__":
    main()
