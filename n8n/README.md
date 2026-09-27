# Fluxo n8n — AutoQA Guardian

Fecha o ciclo de automação: recebe o resultado do pipeline e decide a próxima ação, sem intervenção humana quando possível.

## Nós do fluxo

1. **Webhook** — recebe o POST enviado pelo GitHub Actions ao final de cada execução (`pr`, `status`, `repo`).
2. **IF** — verifica o valor de `status`:
   - `success` → segue para o nó **Slack/Discord** com mensagem de aprovação.
   - `failure` → segue para o nó **Slack/Discord** com alerta + nó **Create Issue** (abre um chamado automático linkando o PR).
3. **Slack/Discord** — posta um resumo curto: repositório, número do PR, status, link para o resumo de riscos gerado pela IA.
4. **Create Issue** (apenas no caminho de falha) — usa o nó do GitHub para abrir uma Issue automaticamente, atribuída ao autor do PR.

## Importando

1. No n8n, vá em **Workflows → Import from File**.
2. Use o arquivo `workflow.json` desta pasta como ponto de partida (ajuste as credenciais de Slack/Discord/GitHub para as suas).
3. Copie a URL gerada pelo nó Webhook e cole no secret `N8N_WEBHOOK_URL` do repositório no GitHub (**Settings → Secrets and variables → Actions**).

> Nota: o arquivo `workflow.json` não está incluído aqui de propósito — exporte o seu próprio fluxo do n8n depois de montá-lo, já que ele carrega suas credenciais e IDs específicos de canal/webhook.
