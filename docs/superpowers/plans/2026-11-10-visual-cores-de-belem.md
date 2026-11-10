# Visual "Cores de Belém" — plano de construção

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trocar o visual "Noite serena" do quiz pelo "Cores de Belém" (cor chapada por área, letra grande, sem os tiques de IA), dividir o resultado em duas telas, deixar os botões mais leves, escalar conforme a tela e atualizar os slides.

**Architecture:** Só a camada de desenho muda: `ui.py` (paleta, fontes, peças), `telas.py` (composição de cada tela, nova tela `retorno`), `boneco.py` (sem aura), `formulario_web.py` (CSS do formulário do celular) e `main.py` (escala). Regras, conteúdo e fluxo de dados ficam como estão.

**Tech Stack:** Python 3 + pygame-ce 2.5 via pygbag 0.9.3, pytest, fonttools (só para gerar as fontes estáticas), Vercel estático.

**Spec:** `docs/superpowers/specs/2026-11-10-visual-cores-de-belem-design.md`

## Global Constraints

- Python + Pygame no navegador via pygbag; publicado na Vercel com `publicar.ps1`.
- Prazo: publicado até **13/11/2026**.
- Fontes só OFL, `.ttf` estáticos em `quiz/assets/` com o arquivo de licença.
- Texto branco sobre as cores das áreas com contraste ≥ 4,5:1.
- Avaliação de cada área continua com semáforo (vermelho / amarelo / verde).
- Proibido: degradê, brilho, sombra, borda de 1 px, cartões repetidos em grade, ícone dentro de bolinha, rótulo pequeno em maiúsculas espaçadas.
- Nada de rolagem; letra grande vale mais que caber tudo numa tela.
- Medidas sempre via `lay.s()` (escala); base 960×600 (PC) e 540×1080 (celular).
- Meta de fluidez: ≥ 30 quadros/s no celular simulado; abaixo disso a escala fica em 2×.
- Ordem de corte se apertar: Task 5 (escala conforme a tela) cai primeiro.

## Decisões deste plano (do Claude, cabem na margem que o spec deixou)

- Paleta: `SONO #1F2A5A`, `AGUA #0B5F8A`, `EXERCICIO #1E6B3A`, `ALIMENTACAO #4B1D4F`, neutro claro `CLARO #EEF2F1`, tinta `TINTA #10202A`, `BRANCO #FFFFFF`; semáforo `RUIM #E5484D`, `MEDIO #F2B705`, `BOM #2FA65A` (selo sólido com texto `TINTA`).
- Fonte: Bricolage Grotesque (OFL), instâncias estáticas ExtraBold (títulos/botões) e Regular (texto). Nunito sai.
- Ícones das áreas saem (eram a "bolinha com ícone"); o nome da área grande identifica a área.
- Botões: pílula (raio = metade da altura), cor chapada. Respostas: fundo = cor da área clareada 16% com texto branco; ao passar o mouse, fundo branco com texto na cor da área. Ação principal: fundo `TINTA` (sobre claro) ou `BRANCO` (sobre cor).
- "Sempre a versão mais nova": a Vercel já responde `Cache-Control: public, max-age=0, must-revalidate` para `/` e `/quiz.apk` (conferido em 10/11), então não há código; só a conferência da Task 6.

## Review Focus

- Nome de 20 letras no título do resultado: quebra em no máximo 2 linhas e não invade as faixas → teste na Task 3.
- Pergunta mais longa de `conteudo.py`: o texto termina acima da primeira resposta, no PC e no celular → teste na Task 3.
- Toque duplo em "Continuar" do resultado: não pula a tela de retorno direto para o início → teste na Task 3.
- Modo acompanhamento: a tela de retorno não mostra IMC e não quebra → teste na Task 3.
- Orientações mais longas nas quatro faixas: cabem acima do botão "Continuar" no PC e no celular, em 1× e 2× → teste na Task 3.

---

### Task 1: Paleta, fontes e peças novas em `ui.py`

**Files:**
- Modify: `quiz/ui.py` (inteiro: cores, `carregar_fontes`, `criar_fundo`, `botao`; remover `card`, `campo` mantém, `barra`, `icone`, `HOVER`, `BG2`, `LINE`)
- Create: `quiz/assets/BricolageGrotesque-ExtraBold.ttf`, `quiz/assets/BricolageGrotesque-Regular.ttf`; substituir `quiz/assets/OFL.txt` pela licença da Bricolage; apagar os dois `Nunito-*.ttf`
- Test: `testes/test_ui.py`

**Interfaces:**
- Produces: constantes `SONO, AGUA, EXERCICIO, ALIMENTACAO, CLARO, TINTA, BRANCO, RUIM, MEDIO, BOM` (tuplas RGB); `COR_AREA: dict[str, tuple]` com chaves `"Sono","Água","Exercício","Alimentação"`; `COR_FAIXA = (RUIM, MEDIO, BOM)`; `COR_NIVEL = {"ok": BOM, "atencao": MEDIO, "info": TINTA}`; `mistura(a, b, t) -> tuple` (renomear `_mistura`, agora pública); `criar_fundo(lay, cor=CLARO) -> Surface` (cor chapada); `botao(sup, fonte, rect, texto, mouse, ativo=True, cor=TINTA, cor_texto=BRANCO, k=1)` pílula; `campo(...)` igual, nas cores novas; `Layout`, `carregar_fontes`, `quebrar`, `desenhar_texto`, `imagem`, `fade` com as mesmas assinaturas de hoje.

- [ ] **Step 1: Gerar as fontes estáticas**

Baixar `BricolageGrotesque[opsz,wdth,wght].ttf` e `OFL.txt` de `github.com/google/fonts/tree/main/ofl/bricolagegrotesque`; gerar com `py -m fontTools.varLib.instancer <var>.ttf wght=800 opsz=48 wdth=100 -o quiz/assets/BricolageGrotesque-ExtraBold.ttf` e `wght=400 opsz=14 wdth=100 -o ...Regular.ttf` (instalar `fonttools` só para isso, fora do projeto).
Expected: os dois arquivos abrem com `pygame.font.Font(caminho, 20)`.

- [ ] **Step 2: Testes que falham**

```python
def _lum(c):
    f = [x / 255 for x in c]
    f = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in f]
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]

def test_branco_legivel_sobre_as_cores_das_areas():
    for cor in COR_AREA.values():
        assert (1.05) / (_lum(cor) + 0.05) >= 4.5

def test_cores():
    assert set(COR_AREA) == {"Sono", "Água", "Exercício", "Alimentação"}
    assert COR_FAIXA == (RUIM, MEDIO, BOM)

def test_fundo_chapado():
    s = criar_fundo(Layout(960, 600), AGUA)
    assert s.get_at((0, 0))[:3] == AGUA and s.get_at((959, 599))[:3] == AGUA

def test_fontes_tem_os_simbolos_usados():   # ‹ › · — e acentos
    f = carregar_fontes(Layout(960, 600))
    for ch in "‹›·—ÁáâãçéêíóôõúÚ":
        assert f["txt"].metrics(ch)[0] is not None

def test_botao_ativo_nao_cria_camada(monkeypatch):
    import ui
    criadas = []
    real = ui.pygame.Surface
    monkeypatch.setattr(ui.pygame, "Surface", lambda *a, **k: criadas.append(a) or real(*a, **k))
    f = carregar_fontes(Layout(960, 600))
    ui.botao(real((300, 80)), f["txt"], (0, 0, 300, 80), "Ok", (-1, -1))
    assert criadas == []
```
Ajustar `test_desenha_sem_erro`/`test_pecas_desenham_com_escala` para as peças que ficam (sem `card`, `barra`, `icone`).

- [ ] **Step 3: Rodar e ver falhar** — `py -m pytest testes/test_ui.py -q` → FAIL (nomes novos não existem).

- [ ] **Step 4: Implementar em `quiz/ui.py`** — `botao` desenha direto em `sup` (`pygame.draw.rect` com `border_radius=rect.h // 2`); só o botão inativo usa camada com alpha. Sem sombra, sem borda.

- [ ] **Step 5: Rodar** — `py -m pytest testes/test_ui.py -q` → PASS. (`test_telas.py` vai quebrar até a Task 3; tudo bem.)

- [ ] **Step 6: Commit** — `git add quiz/ui.py quiz/assets testes/test_ui.py && git commit -m "Paleta Cores de Belém, fonte Bricolage e botão pílula"`

### Task 2: Boneco sem aura

**Files:**
- Modify: `quiz/boneco.py:11,54-58,61` (sem `aura`; pernas numa cor clara que aparece sobre as cores das áreas)
- Test: `testes/test_boneco.py`

**Interfaces:**
- Consumes: `ui.BRANCO`, `ui.TINTA`, `ui.MEDIO`, `ui.BOM` (Task 1). `desenhar_boneco(sup, centro, altura, energia, t_ms)` igual.

- [ ] **Step 1: Teste que falha**

```python
def test_sem_brilho_semitransparente():
    sup = pygame.Surface((200, 300), pygame.SRCALPHA)
    desenhar_boneco(sup, (100, 150), 240, 1.0, 0)
    alfas = {sup.get_at((x, y))[3] for x in range(200) for y in range(300)}
    assert alfas <= {0, 255}
```
- [ ] **Step 2:** `py -m pytest testes/test_boneco.py -q` → FAIL (aura com alpha 55).
- [ ] **Step 3:** remover o bloco da aura; trocar `LINE` das pernas por uma cor clara (ex.: `mistura(BRANCO, TINTA, 0.25)`); manter estrelinhas chapadas.
- [ ] **Step 4:** rodar → PASS.
- [ ] **Step 5: Commit** — `git commit -am "Boneco chapado, sem aura"`

### Task 3: Telas no visual novo e resultado em duas telas

**Files:**
- Modify: `quiz/telas.py` (todas as telas; nova tela `retorno`)
- Test: `testes/test_telas.py`

**Interfaces:**
- Consumes: tudo da Task 1; `desenhar_boneco` (Task 2).
- Produces: `Estado.tela` aceita `"retorno"`; `trocar(est, "retorno", agora)` mantém `respostas`. Rects devolvidos por tela:
  - `inicio`: `primeira_vez`, `ja_fiz` (+ `qr` no PC)
  - `dados`: `continuar`, `voltar`, `campo0..3`
  - `quiz`/`acomp`: `opcao0..2`, `texto` (área ocupada pela pergunta)
  - `resultado`/`feedback` (tela 1): `continuar`, `titulo`, `conteudo` (das faixas), `faixa_<area>`
  - `retorno` (tela 2): `voltar`, `conteudo`, `rodape` (+ `imc` só no modo `quiz`)

Composição (em `lay.s()`):
- **inicio:** quatro faixas verticais (PC) / horizontais (celular) nas cores das áreas ocupando o fundo; por cima, numa área `CLARO` (PC: coluna esquerda; celular: metade de baixo), "Viva Bem" grande, a frase de apresentação, os dois botões pílula e o aviso de saúde. PC: QR code sobre uma das faixas, com "Aponte a câmera do celular" e o endereço em branco, e o boneco.
- **dados (PC):** fundo `CLARO`, título "Antes de começar", campos nas cores novas, "Continuar ›" pílula `TINTA`, "‹ Voltar" pílula clara.
- **quiz/acomp:** fundo chapado `COR_AREA[area]`; nome da área bem grande em branco no topo, "Pergunta X de Y" em branco menor, a pergunta grande em branco, três respostas pílula. PC: coluna direita com o boneco sobre a mesma cor (sem cartão).
- **resultado/feedback (tela 1):** título ("Resultado de Ana"…) em `TINTA` sobre `CLARO`; quatro faixas de largura cheia, cada uma na cor da área: nome da área + selo de semáforo com a palavra (`ROTULO_FAIXA`) + orientação em branco. "Continuar ›" no fim. PC: boneco numa coluna à direita.
- **retorno (tela 2):** fundo `CLARO`; IMC grande (modo quiz) com a cor de `COR_NIVEL`, observação, "Volte dia DD/MM para o acompanhamento.", aviso de saúde, "Voltar ao início".

- [ ] **Step 1: Atualizar/escrever testes que falham** — trocar os testes que hoje leem `voltar/conteudo/rodape` no resultado para o novo fluxo, e acrescentar:

```python
def test_resultado_continua_para_retorno_e_volta_ao_inicio():
    est = _pior_caso("resultado")
    tocar(est, "continuar"); assert est.tela == "retorno" and len(est.respostas) == 8
    tocar(est, "voltar"); assert est.tela == "inicio"

def test_toque_duplo_em_continuar_nao_pula_o_retorno():
    est = _pior_caso("resultado")
    r = passo(est)
    passo(est, clique=r["continuar"].center, agora=Relogio.t + 1000)
    passo(est, clique=r["continuar"].center, agora=Relogio.t + 1150)
    assert est.tela == "retorno"

@pytest.mark.parametrize("modo,tem_imc", [("quiz", True), ("acomp", False)])
def test_retorno_so_mostra_imc_no_quiz(modo, tem_imc):
    est = _pior_caso("resultado" if modo == "quiz" else "feedback"); est.tela = "retorno"
    assert ("imc" in passo(est)) is tem_imc

@pytest.mark.parametrize("kw", ["PC", "RET", "PC2", "RET2"])
@pytest.mark.parametrize("tela", ["resultado", "feedback"])
def test_faixas_cabem_acima_do_continuar(kw, tela):    # orientações mais longas
    r = passo(_pior_caso(tela), **_KW[kw])
    assert r["conteudo"].bottom <= r["continuar"].top

@pytest.mark.parametrize("kw", ["PC", "RET"])
def test_nome_de_20_letras_quebra_em_ate_2_linhas(kw):
    est = _pior_caso("resultado"); est.nome = "W" * 20
    r = passo(est, **_KW[kw]); f = _KW[kw]["fontes"]
    assert r["titulo"].h <= 2 * f["tit"].get_linesize()
    assert r["titulo"].bottom <= r["conteudo"].top

@pytest.mark.parametrize("kw", ["PC", "RET"])
def test_pergunta_mais_longa_cabe_acima_das_respostas(kw):
    from conteudo import PERGUNTAS
    i = max(range(len(PERGUNTAS)), key=lambda j: len(PERGUNTAS[j][1]))
    r = passo(Estado(tela="quiz", indice=i), **_KW[kw])
    assert r["texto"].bottom <= r["opcao0"].top
```
(`_KW = {"PC": dict(lay=LAY, fontes=F, fundo=FUNDO, sup=SUP), "RET": RET, "PC2": PC2, "RET2": RET2}`; o `_pior_caso` usa as orientações de faixa 0, que são as mais longas.) Ajustar `test_escala_2x_desenha_a_mesma_tela_no_dobro_do_tamanho` para incluir `retorno`.

- [ ] **Step 2:** `py -m pytest -q` → FAIL nos testes novos.
- [ ] **Step 3:** reescrever as funções de desenho de `quiz/telas.py` com a composição acima; `desenhar` inclui `"retorno"` no dicionário de telas e no cálculo do alvo de energia; `_resultado` termina em `trocar(est, "retorno", ...)` ao clicar "continuar".
- [ ] **Step 4:** `py -m pytest -q` → todos PASS.
- [ ] **Step 5: Olhar as telas** — gerar PNG de todas as telas em PC e celular (script `telas_png.py` do scratchpad, agora incluindo `retorno`) e conferir: nada encostado, nada cortado, nenhum item da lista proibida, letra grande.
- [ ] **Step 6: Commit** — `git commit -am "Telas no visual Cores de Belém; resultado em duas telas"`

### Task 4: Formulário do celular no estilo novo

**Files:**
- Modify: `quiz/formulario_web.py:30-50` (só o CSS `_CSS`)
- Test: `testes/test_formulario_web.py`

- [ ] **Step 1: Teste que falha**

```python
def test_formulario_usa_as_cores_novas():
    html = html_formulario()
    assert "#10202a" in html.lower() and "#eef2f1" in html.lower()
    assert "#2dd4bf" not in html.lower()
```
- [ ] **Step 2:** rodar → FAIL.
- [ ] **Step 3:** CSS: fundo `#EEF2F1`, texto `#10202A`, título forte, campos sem sombra, botão "Continuar" pílula `#10202A` com texto branco, "Voltar" pílula clara, erro em `#B4232A` (legível sobre claro). Fonte `system-ui` em peso 800 nos títulos. Manter `font-size: 18px` nos campos (iPhone não dá zoom).
- [ ] **Step 4:** rodar `py -m pytest -q` → PASS.
- [ ] **Step 5: Commit** — `git commit -am "Formulário do celular no visual novo"`

### Task 5: Escala conforme a tela (cai primeiro se o prazo apertar)

**Files:**
- Modify: `quiz/ui.py` (nova função), `quiz/main.py:16-30`
- Test: `testes/test_ui.py`

**Interfaces:**
- Produces: `escala_da_tela(dpr: float, largura_css: float, base_w: int) -> float` em `ui.py`: `dpr * largura_css / base_w`, limitado a [2, 3] e arredondado para múltiplo de 0,25.

- [ ] **Step 1: Teste que falha**

```python
@pytest.mark.parametrize("dpr,css,base,esperado", [
    (3, 390, 540, 2.25), (3.5, 412, 540, 2.75), (1, 1280, 960, 2), (2, 1920, 960, 3), (1, 1, 540, 2)])
def test_escala_da_tela(dpr, css, base, esperado):
    assert escala_da_tela(dpr, css, base) == esperado
```
- [ ] **Step 2:** rodar → FAIL.
- [ ] **Step 3:** implementar; em `main.py`, no navegador: `largura_css = min(window.innerWidth, window.innerHeight * base_w / base_h)` e `k = escala_da_tela(window.devicePixelRatio, largura_css, base_w)`; fora do navegador `k = 2`. `Layout(round(base_w * k), round(base_h * k), k)`.
- [ ] **Step 4:** rodar `py -m pytest -q` → PASS.
- [ ] **Step 5: Medir** — `py -m pygbag --build quiz`, servir `quiz/build/web` e rodar `medir.mjs` (scratchpad) no celular (390×844, dpr 3) e no PC. Expected: ampliação ≤ 1,1 e ≥ 30 quadros/s. Se < 30, voltar `main.py` para `k = 2` fixo e registrar no plano.
- [ ] **Step 6: Commit** — `git commit -am "Escala conforme a densidade da tela (limite 3x)"`

### Task 6: Publicar, conferir e atualizar os slides

**Files:**
- Modify: `apresentacao/Viva-Bem-apresentacao.pptx`, `.pdf` (regerados pelo `gerar_slides.js` do scratchpad com as imagens novas)

- [ ] **Step 1:** `py -m pytest -q` → todos PASS.
- [ ] **Step 2: Publicar** — `powershell -NoProfile -ExecutionPolicy Bypass -File .\publicar.ps1 "Visual Cores de Belém"`.
- [ ] **Step 3: Conferir no ar** — `curl -sI https://viva-bem-seven.vercel.app/quiz.apk` → `Cache-Control: public, max-age=0, must-revalidate`; `medir.mjs` no site publicado (celular) mostra o canvas no tamanho novo; print das telas confere com o visual.
- [ ] **Step 4: Slides** — gerar PNG das telas novas (PC: pergunta, resultado tela 1; celular: resultado tela 1), trocar as imagens no `gerar_slides.js`, regerar o `.pptx`, exportar o `.pdf` pelo PowerPoint, conferir os slides 1, 8 e 10 em imagem e copiar para `apresentacao/`.
- [ ] **Step 5: Commit e push** — `git add apresentacao && git commit -m "Slides com o visual novo" && git push`.
