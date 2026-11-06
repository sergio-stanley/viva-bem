# Notas do spike — formulário HTML no celular (Task 2)

**Data:** 06/11/2026 · Branch descartável `spike-formulario` (apagada depois do teste).

## Resultados

| Item | Chrome headless (PC, emulando celular) | iPhone real (Safari) |
|---|---|---|
| (a) `matchMedia("(pointer: coarse)").matches` | `True` no celular emulado | — (não reportado) |
| (b) formulário aparece por cima do canvas | ✅ | ✅ abriu |
| (c) Python lê "Continuar" e os valores | ✅ formulário fechou após `ok` | ✅ apareceu "OK! ..." |
| (d) toques voltam ao canvas; reabrir não duplica | ✅ (`querySelectorAll('#vb-form').length == 1`) | — |
| (e) `window.prompt()` | não testado no headless | — |

**Decisão: formulário HTML** (a reserva `prompt()` não é necessária).

## Descobertas que afetam a implementação

1. **Carregamento no celular é lento, não travado.** O runtime do pygbag baixa ~22 MB
   (`main.wasm` 13,4 MB + `main.data` 6,7 MB + pygame ~1,5 MB) e compila o wasm. No celular a tela
   fica em "Loading, please wait ..." por bastante tempo. Os primeiros testes foram abandonados antes
   de terminar. Com `#debug` no iPhone o quiz carregou até `default.tmpl: done`.
   → Na apresentação: pedir para abrirem o link alguns minutos antes. Considerar trocar o texto do
   infobox por algo como "Carregando… no celular pode levar até 1 minuto".
2. **Acentos quebram ao passar JS pelo `platform.window.eval`** ("formulário" virou "formulÃ¡rio").
   → No JS gerado pelo Python, escrever caracteres não-ASCII como entidades HTML (`&aacute;`,
   `&ccedil;` …) ou escapes `\uXXXX`. Solução simples: `texto.encode("ascii", "xmlcharrefreplace").decode()`
   para trechos HTML.
3. **Valor JS indefinido chega ao Python como `None`** (`window.vb_acao_nao_existe` → `None`).
4. **Links de prévia da Vercel exigem login** (Deployment Protection) e os arquivos do jogo não
   carregam assim. Testes em prévia exigem desligar "Vercel Authentication" temporariamente.

## Mecanismo validado (usar na Task 6)

```python
import platform                                   # só quando sys.platform == "emscripten"
platform.window.eval(JS_ABRIR)                    # cria <div id="vb-form"> (remove o antigo antes)
acao = platform.window.eval("window.vb_acao")     # '' / 'ok' / None
valor = platform.window.eval("document.getElementById('vb-idade').value")
platform.window.eval("var f=document.getElementById('vb-form'); if (f) f.remove(); window.vb_acao='';")
```

JS de abertura (resumo): remove `#vb-form` existente; `window.vb_acao=''`; cria `div` com
`position:fixed;inset:0;z-index:9999`; inputs com `font-size:20px` (evita zoom automático do iOS);
idade com `inputmode="numeric" pattern="[0-9]*" maxlength="3"`; botão com
`onclick = function(){ window.vb_acao = 'ok'; }`.

Código completo do spike: no histórico do GitHub, commit "spike: formulario html (descartável)"
(antes de a branch ser apagada) — não é necessário para a Task 6.
