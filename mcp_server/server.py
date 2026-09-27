"""
Servidor MCP do AutoQA Guardian.

Expõe uma ferramenta `get_pipeline_status` que consulta a API do GitHub
Actions e devolve o status das últimas execuções — para que um cliente
MCP (ex: Claude Desktop) responda perguntas como "por que o build #42
falhou?" sem você precisar abrir o navegador.

Requer: pip install mcp requests
Configuração no cliente MCP (ex: claude_desktop_config.json):
{
  "mcpServers": {
    "autoqa-guardian": {
      "command": "python",
      "args": ["mcp_server/server.py"],
      "env": {"GITHUB_TOKEN": "...", "GITHUB_REPO": "usuario/repositorio"}
    }
  }
}
"""
import os

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("autoqa-guardian")

GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


@mcp.tool()
def get_pipeline_status(quantidade: int = 5) -> str:
    """Retorna o status das últimas execuções do workflow AutoQA Guardian."""
    if not GITHUB_REPO or not GITHUB_TOKEN:
        return "Configure GITHUB_REPO e GITHUB_TOKEN nas variáveis de ambiente."

    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    resposta = requests.get(url, headers=headers, params={"per_page": quantidade})
    resposta.raise_for_status()

    execucoes = resposta.json().get("workflow_runs", [])
    linhas = []
    for execucao in execucoes:
        linhas.append(
            f"- PR/branch: {execucao['head_branch']} | "
            f"status: {execucao['status']} / {execucao['conclusion']} | "
            f"data: {execucao['created_at']} | "
            f"link: {execucao['html_url']}"
        )
    return "\n".join(linhas) if linhas else "Nenhuma execução encontrada."


@mcp.tool()
def get_run_summary(run_id: int) -> str:
    """Retorna os logs resumidos de uma execução específica pelo ID."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}/jobs"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    resposta = requests.get(url, headers=headers)
    resposta.raise_for_status()

    jobs = resposta.json().get("jobs", [])
    linhas = [f"{j['name']}: {j['conclusion']}" for j in jobs]
    return "\n".join(linhas) if linhas else "Execução não encontrada."


if __name__ == "__main__":
    mcp.run()
