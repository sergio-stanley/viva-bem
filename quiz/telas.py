"""Estado do quiz e desenho/entrada de cada tela do Viva Bem (PC deitado e celular em pé).

Visual "Cores de Belém": cada área pinta a tela com a sua cor (ui.COR_AREA); as telas sem área usam o
fundo claro. Nada de degradê, brilho, sombra ou borda fina.
"""
import datetime
from dataclasses import dataclass, field

import pygame

from conteudo import AREAS, PERGUNTAS, ACOMPANHAMENTO, OPCOES_ACOMP, AVISO_SAUDE, ROTULO_FAIXA, SITE
from regras import (avaliar_area, pontos_por_area, calcular_imc, formatar_decimal, validar_dados,
                    titulo, data_retorno, aceita_clique, energia, aproximar, LIMITE_NOME)
import ui
from boneco import desenhar_boneco
from ui import BRANCO, TINTA, CLARO, AGUA, COR_AREA, COR_FAIXA, COR_NIVEL


@dataclass
class Entrada:
    mouse: tuple
    clique: object          # (x, y) ou None
    teclas: list
    agora_ms: int


@dataclass
class Estado:
    tela: str = "inicio"    # inicio | dados | quiz | acomp | resultado | feedback | retorno
    modo: str = "quiz"      # quiz | acomp
    indice: int = 0
    respostas: list = field(default_factory=list)
    nome: str = ""
    idade: str = ""
    altura: str = ""
    peso: str = ""
    campo: int = 0
    ms_troca: int = 0
    energia_vista: float = 0.5      # energia mostrada pelo boneco (anda suavemente até o alvo)
    ms_ultimo: int = 0              # instante do quadro anterior (para animar)
    form_aberto: bool = False
    hoje: datetime.date = field(default_factory=datetime.date.today)


def trocar(est: Estado, tela: str, agora_ms: int):
    if tela == "dados":
        est.nome = est.idade = est.altura = est.peso = ""
        est.campo = 0
    if tela in ("quiz", "acomp"):
        est.indice, est.respostas = 0, []
    if tela == "inicio":
        est.energia_vista = 0.5
    est.tela, est.ms_troca = tela, agora_ms
    est.form_aberto = False


def desenhar(sup, lay, fontes, fundo, est: Estado, ent: Entrada, form=None) -> dict:
    """Desenha a tela atual e trata a entrada. `form`: FormularioWeb no celular (ou None no PC)."""
    sup.blit(fundo, (0, 0))
    dt = max(0, min(100, ent.agora_ms - est.ms_ultimo))
    est.ms_ultimo = ent.agora_ms
    com_respostas = ("quiz", "acomp", "resultado", "feedback", "retorno")
    alvo = energia(est.respostas) if est.tela in com_respostas else 0.5
    est.energia_vista = aproximar(est.energia_vista, alvo, dt)
    clique = ent.clique if aceita_clique(ent.agora_ms - est.ms_troca) else None
    ent = Entrada(ent.mouse, clique, ent.teclas, ent.agora_ms)
    if est.tela == "dados" and form is not None:
        rects = _dados_formulario(sup, lay, fontes, est, ent, form)
    else:
        tela = {"inicio": _inicio, "dados": _dados, "quiz": _perguntas, "acomp": _perguntas,
                "resultado": _resultado, "feedback": _resultado, "retorno": _retorno}[est.tela]
        rects = tela(sup, lay, fontes, est, ent)
    ui.fade(sup, ent.agora_ms - est.ms_troca, sup.get_at((0, 0))[:3])    # entra na cor da própria tela
    return rects


def _clicou(ent, rect):
    return ent.clique is not None and rect.collidepoint(ent.clique)


def _rotulo_energia(e):
    if e < 0.35:
        return "Sem energia"
    if e < 0.7:
        return "Energia ok"
    return "Cheio de energia!"


def _painel_boneco(sup, lay, f, painel, est, ent, legenda=True, cor_txt=BRANCO):
    """Boneco de energia centralizado numa região (só no PC)."""
    S = lay.s
    altura = min(S(300), painel.h - S(90))
    centro = (painel.centerx, painel.y + S(30) + altura // 2)
    desenhar_boneco(sup, centro, altura, est.energia_vista, ent.agora_ms)
    if legenda:
        img = f["txt"].render(_rotulo_energia(est.energia_vista), True, cor_txt)
        sup.blit(img, img.get_rect(midtop=(painel.centerx, centro[1] + altura // 2 + S(12))))


def _selo(sup, f, texto, cor, pos, lay, ancora="midright"):
    """Selo sólido com a avaliação (semáforo). Devolve o retângulo."""
    img = f["peq"].render(texto, True, TINTA)
    r = img.get_rect().inflate(lay.s(24), lay.s(10))
    setattr(r, ancora, pos)
    pygame.draw.rect(sup, cor, r, border_radius=r.h // 2)
    sup.blit(img, img.get_rect(center=r.center))
    return r


def _faixas_de_cor(sup, regiao, vertical):
    """As quatro cores das áreas lado a lado, como uma bandeira. Devolve as faixas."""
    faixas = []
    for i, area in enumerate(AREAS):
        if vertical:
            x0, x1 = regiao.x + regiao.w * i // 4, regiao.x + regiao.w * (i + 1) // 4
            r = pygame.Rect(x0, regiao.y, x1 - x0, regiao.h)
        else:
            y0, y1 = regiao.y + regiao.h * i // 4, regiao.y + regiao.h * (i + 1) // 4
            r = pygame.Rect(regiao.x, y0, regiao.w, y1 - y0)
        sup.fill(COR_AREA[area], r)
        faixas.append((area, r))
    return faixas


# ---------------------------------------------------------------- início
def _inicio(sup, lay, f, est, ent):
    M, S, k = lay.margem, lay.s, lay.k
    texto = ("Responda 8 perguntas sobre sono, água, exercício e alimentação e receba "
             "orientações para melhorar sua rotina. Refaça a cada 2 dias para acompanhar seu progresso.")
    aviso = AVISO_SAUDE + " Nenhum dado é guardado."
    extras = {}
    if lay.retrato:
        largura = lay.W - 2 * M
        for area, r in _faixas_de_cor(sup, pygame.Rect(0, 0, lay.W, S(360)), vertical=False):
            img = f["txt"].render(area, True, BRANCO)
            sup.blit(img, img.get_rect(midleft=(M, r.centery)))
        y = S(392)
        sup.blit(f["grande"].render("Viva Bem", True, TINTA), (M, y))
        y = ui.desenhar_texto(sup, texto, f["txt"], TINTA, M, y + f["grande"].get_linesize(), largura,
                              espaco=S(4))
        r1 = pygame.Rect(M, lay.H - S(330), largura, S(84))
        r2 = pygame.Rect(M, lay.H - S(230), largura, S(84))
        fonte_bt = f["txt"]
        ui.desenhar_texto(sup, aviso, f["peq"], TINTA, M, lay.H - M - S(56), largura, espaco=0)
    else:
        regiao = pygame.Rect(int(lay.W * 0.58), 0, lay.W - int(lay.W * 0.58), lay.H)
        _faixas_de_cor(sup, regiao, vertical=True)
        col_w = regiao.x - 2 * M
        sup.blit(f["grande"].render("Viva Bem", True, TINTA), (M, S(48)))
        ui.desenhar_texto(sup, texto, f["txt"], TINTA, M, S(48) + f["grande"].get_linesize() + S(8), col_w,
                          espaco=S(4))
        r1 = pygame.Rect(M, S(330), col_w, S(64))
        r2 = pygame.Rect(M, S(410), col_w, S(64))
        fonte_bt = f["txt"]
        ui.desenhar_texto(sup, aviso, f["peq"], TINTA, M, lay.H - M - S(44), col_w, espaco=S(2))
        qr = ui.imagem("qrcode.png")
        y = S(48)
        if qr is not None:      # para o público escanear durante a apresentação
            # ampliado/reduzido sem suavizar (transform.scale): o QR continua com bordas nítidas
            lado = min(regiao.w - S(80), S(qr.get_width()))
            if lado != qr.get_width():
                qr = pygame.transform.scale(qr, (lado, lado))
            r_qr = qr.get_rect(midtop=(regiao.centerx, y))
            sup.blit(qr, r_qr)
            y = r_qr.bottom + S(12)
            for linha in ("Aponte a câmera do celular", SITE):
                img = f["peq"].render(linha, True, BRANCO)
                sup.blit(img, img.get_rect(midtop=(regiao.centerx, y)))
                y += f["peq"].get_linesize()
            extras["qr"] = r_qr
        _painel_boneco(sup, lay, f, pygame.Rect(regiao.x, y + S(8), regiao.w, lay.H - y - S(8)),
                       est, ent, legenda=False)
    ui.botao(sup, fonte_bt, r1, "Primeira vez: começar o quiz", ent.mouse, k=k)
    ui.botao(sup, fonte_bt, r2, "Já fiz antes: acompanhamento", ent.mouse, cor=BRANCO, cor_texto=TINTA, k=k)
    if _clicou(ent, r1):
        est.modo = "quiz"
        trocar(est, "dados", ent.agora_ms)
    elif _clicou(ent, r2):
        est.modo = "acomp"
        trocar(est, "dados", ent.agora_ms)
    rects = {"primeira_vez": r1, "ja_fiz": r2}
    rects.update(extras)
    return rects


# ---------------------------------------------------------------- dados (teclado físico)
def _dados(sup, lay, f, est, ent):
    M, S, k = lay.margem, lay.s, lay.k
    col_w = lay.W - 2 * M if lay.retrato else int((lay.W - 2 * M) * 0.6)
    sup.blit(f["tit"].render("Antes de começar", True, TINTA), (M, S(40)))
    y_sub = ui.desenhar_texto(sup, "Seus dados não são guardados — servem só para o resultado.",
                              f["peq"], TINTA, M, S(40) + f["tit"].get_linesize(), col_w, espaco=S(4))
    y_cx = max(S(170), y_sub + f["peq"].get_linesize() + S(12))
    caixas = [pygame.Rect(M, y_cx, col_w, S(52))]
    w3 = (col_w - S(32)) // 3
    caixas += [pygame.Rect(M + i * (w3 + S(16)), y_cx + S(100), w3, S(52)) for i in range(3)]
    rotulos = ["Nome (opcional)", "Idade", "Altura", "Peso"]
    unidades = ["", "anos", "cm", "kg"]
    valores = [est.nome, est.idade, est.altura, est.peso]
    for i in range(4):
        ui.campo(sup, f, caixas[i], rotulos[i], valores[i], unidades[i], est.campo == i, k=k)
    erro = validar_dados(est.nome, est.idade, est.altura, est.peso)
    valido = erro is None
    if erro and (est.idade or est.altura or est.peso):
        ui.desenhar_texto(sup, erro, f["peq"], ui.mistura(ui.RUIM, TINTA, 0.35), M, caixas[1].bottom + S(12), col_w,
                          espaco=S(4))
    if lay.retrato:
        bc = pygame.Rect(M, lay.H - M - S(72), col_w, S(72))
        lado = pygame.Rect(0, caixas[1].bottom + S(80), lay.W, S(200))
    else:
        bc = pygame.Rect(M, lay.H - M - S(64), S(220), S(64))
        lado = pygame.Rect(M + col_w + S(32), 0, lay.W - (M + col_w + S(32)), lay.H)
    ui.botao(sup, f["perg"], bc, "Continuar ›", ent.mouse, ativo=valido, k=k)
    if lay.retrato:
        bvolta = pygame.Rect(M, bc.y - S(84), col_w, S(72))
    else:
        bvolta = pygame.Rect(bc.right + S(16), bc.y, S(160), bc.h)
    ui.botao(sup, f["txt"], bvolta, "‹ Voltar", ent.mouse, cor=BRANCO, cor_texto=TINTA, k=k)
    sup.fill(AGUA, lado)        # bloco de cor chapada, encostado na borda
    tx = lado.x + (M if lado.x == 0 else S(28))
    ty = lado.y + (S(24) if lay.retrato else S(170))
    largura_txt = lado.right - tx - (M if lado.x == 0 else S(28))
    y = ui.desenhar_texto(sup, "Por que pedimos isso?", f["perg"], BRANCO, tx, ty, largura_txt, espaco=0)
    y = ui.desenhar_texto(sup, "Idade, altura e peso servem para calcular seu IMC. "
                          "O nome só personaliza o título.", f["peq"], BRANCO, tx, y + S(4), largura_txt, espaco=S(4))
    ui.desenhar_texto(sup, "Tab ou Enter: próximo campo · Esc: voltar", f["peq"], BRANCO,
                      tx, y + S(14), largura_txt, espaco=0)

    for ev in ent.teclas:
        if ev.key == pygame.K_ESCAPE:
            trocar(est, "inicio", ent.agora_ms)
            return {}
        if _tecla_dados(est, ev) and valido:
            trocar(est, est.modo, ent.agora_ms)
            return {}
    if ent.clique:
        for i, cx in enumerate(caixas):
            if cx.collidepoint(ent.clique):
                est.campo = i
        if _clicou(ent, bc) and valido:
            trocar(est, est.modo, ent.agora_ms)
        elif _clicou(ent, bvolta):
            trocar(est, "inicio", ent.agora_ms)
    rects = {"continuar": bc, "voltar": bvolta}
    rects.update({f"campo{i}": c for i, c in enumerate(caixas)})
    return rects


def _dados_formulario(sup, lay, f, est, ent, form):
    """Celular: os dados são digitados num formulário HTML (abre o teclado do próprio celular)."""
    sup.blit(f["tit"].render("Antes de começar", True, TINTA), (lay.margem, lay.s(60)))
    if not est.form_aberto:
        form.abrir()
        est.form_aberto = True
    acao = form.acao()
    if acao == "ok":
        nome, idade, altura, peso = (v.strip() for v in form.valores())
        erro = validar_dados(nome, idade, altura, peso)
        if erro:
            form.mostrar_erro(erro)
        else:
            form.fechar()
            trocar(est, est.modo, ent.agora_ms)
            est.nome, est.idade, est.altura, est.peso = nome[:LIMITE_NOME], idade, altura, peso
    elif acao == "voltar":
        form.fechar()
        trocar(est, "inicio", ent.agora_ms)
    return {}


_ATRIBUTOS = ["nome", "idade", "altura", "peso"]


def _tecla_dados(est, ev) -> bool:
    """Aplica uma tecla aos campos. Devolve True se foi Enter no último campo (pedido de continuar)."""
    attr = _ATRIBUTOS[est.campo]
    valor = getattr(est, attr)
    if ev.key == pygame.K_TAB:
        est.campo = (est.campo + 1) % 4
    elif ev.key == pygame.K_BACKSPACE:
        setattr(est, attr, valor[:-1])
    elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        if est.campo == 3:
            return True
        est.campo += 1
    elif ev.unicode and ev.unicode.isprintable():
        if est.campo == 0 and len(valor) < LIMITE_NOME:
            setattr(est, attr, valor + ev.unicode)
        elif est.campo > 0 and ev.unicode.isascii() and ev.unicode.isdigit() and len(valor) < 3:
            setattr(est, attr, valor + ev.unicode)
    return False


# ---------------------------------------------------------------- perguntas
def _perguntas(sup, lay, f, est, ent):
    M, S, k = lay.margem, lay.s, lay.k
    lista = PERGUNTAS if est.tela == "quiz" else ACOMPANHAMENTO
    area, texto = lista[est.indice][0], lista[est.indice][1]
    opcoes = lista[est.indice][2] if est.tela == "quiz" else OPCOES_ACOMP
    cor = COR_AREA[area]
    sup.fill(cor)
    col_w = lay.W - 2 * M if lay.retrato else int((lay.W - 2 * M) * 0.62)

    y = S(56) if lay.retrato else S(32)
    fonte_area = f["grande"] if f["grande"].size(area)[0] <= col_w else f["tit"]
    sup.blit(fonte_area.render(area, True, BRANCO), (M, y))
    y += fonte_area.get_linesize()
    sup.blit(f["txt"].render(f"Pergunta {est.indice + 1} de {len(lista)}", True, BRANCO), (M, y))
    y0_texto = y + f["txt"].get_linesize() + S(40 if lay.retrato else 20)
    y_fim = ui.desenhar_texto(sup, texto, f["perg"], BRANCO, M, y0_texto, col_w, espaco=S(4))

    altura_op, gap = (S(92), S(18)) if lay.retrato else (S(64), S(12))
    y0 = lay.H - M - (3 * altura_op + 2 * gap)
    rects = {"texto": pygame.Rect(M, y0_texto, col_w, y_fim - y0_texto)}
    clara = ui.mistura(cor, BRANCO, 0.16)
    for i, (t, p) in enumerate(opcoes):
        r = pygame.Rect(M, y0 + i * (altura_op + gap), col_w, altura_op)
        ui.botao(sup, f["txt"], r, t, ent.mouse, cor=clara, cor_texto=BRANCO, k=k)
        rects[f"opcao{i}"] = r
        if _clicou(ent, r):
            est.respostas.append((area, p))
            est.indice += 1
            if est.indice >= len(lista):
                trocar(est, "resultado" if est.tela == "quiz" else "feedback", ent.agora_ms)
            else:
                est.ms_troca = ent.agora_ms
            break
    if not lay.retrato:
        x = M + col_w + S(32)
        _painel_boneco(sup, lay, f, pygame.Rect(x, S(40), lay.W - M - x, lay.H - S(80)), est, ent)
    return rects


# ---------------------------------------------------------------- resultado (tela 1: as áreas)
def _titulo_resultado(sup, lay, f, texto, x, y, largura):
    """Título grande em até 2 linhas; se uma palavra não couber, usa a fonte menor. Devolve o retângulo."""
    fonte = f["tit"]
    if any(fonte.size(linha)[0] > largura for linha in ui.quebrar(texto, fonte, largura)):
        fonte = f["perg"]
    fim = ui.desenhar_texto(sup, texto, fonte, TINTA, x, y, largura, espaco=0)
    return pygame.Rect(x, y, largura, fim - y)


def _selo_ao_lado(lay, f, area, fx, largura):
    selo_w = f["peq"].size(ROTULO_FAIXA[fx])[0] + lay.s(24)
    return f["perg"].size(area)[0] + lay.s(16) + selo_w <= largura


def _altura_faixa(lay, f, area, fx, msg, largura, fonte):
    S = lay.s
    extra = 0 if _selo_ao_lado(lay, f, area, fx, largura) else f["peq"].get_linesize() + S(16)
    return (S(14) + f["perg"].get_linesize() + extra + len(ui.quebrar(msg, f[fonte], largura)) * f[fonte].get_linesize()
            + S(16))


def _faixa_area(sup, lay, f, r, area, fx, msg, pad_x, fonte):
    """Uma área do resultado: bloco na cor da área, nome, selo do semáforo e a orientação."""
    S = lay.s
    sup.fill(COR_AREA[area], r)
    largura = r.w - 2 * pad_x
    x, y = r.x + pad_x, r.y + S(14)
    img = f["perg"].render(area, True, BRANCO)
    sup.blit(img, (x, y))
    y += f["perg"].get_linesize()
    if _selo_ao_lado(lay, f, area, fx, largura):
        _selo(sup, f, ROTULO_FAIXA[fx], COR_FAIXA[fx], (r.right - pad_x, r.y + S(14) + img.get_height() // 2), lay)
    else:
        sel = _selo(sup, f, ROTULO_FAIXA[fx], COR_FAIXA[fx], (x, y), lay, ancora="topleft")
        y = sel.bottom + S(8)
    ui.desenhar_texto(sup, msg, f[fonte], BRANCO, x, y, largura, espaco=0)


def _resultado(sup, lay, f, est, ent):
    M, S, k = lay.margem, lay.s, lay.k
    modo = "quiz" if est.tela == "resultado" else "acomp"
    largura = lay.W - 2 * M
    grade_w = largura if lay.retrato else largura - S(210)
    r_tit = _titulo_resultado(sup, lay, f, titulo(est.nome, modo), M, S(24), grade_w)
    y = r_tit.bottom + S(16)

    pontos = pontos_por_area(est.respostas)
    avaliacoes = [(area,) + avaliar_area(area, pontos[area], modo) for area in AREAS]
    rects = {"titulo": r_tit}
    topo = y
    bc_h = S(72) if lay.retrato else S(56)
    livre = lay.H - M - bc_h - S(24) - topo        # altura disponível para as faixas
    if lay.retrato:     # faixas de ponta a ponta, uma embaixo da outra
        larg = lay.W - 2 * M
        fonte = "txt" if sum(_altura_faixa(lay, f, a, fx, m, larg, "txt") for a, fx, m in avaliacoes) <= livre else "peq"
        alturas = [_altura_faixa(lay, f, a, fx, m, larg, fonte) for a, fx, m in avaliacoes]
        sobra = max(0, livre - sum(alturas)) // 4
        for (area, fx, msg), h in zip(avaliacoes, alturas):
            r = pygame.Rect(0, y, lay.W, h + sobra)
            _faixa_area(sup, lay, f, r, area, fx, msg, M, fonte)
            rects[f"faixa_{area}"] = r
            y = r.bottom
    else:               # 2x2 encostadas, como a bandeira da tela inicial
        meia = (M + grade_w) // 2
        larg = meia - M - S(20)

        def maior(fonte):
            return max(_altura_faixa(lay, f, a, fx, m, larg, fonte) for a, fx, m in avaliacoes)
        fonte = "txt" if 2 * maior("txt") <= livre else "peq"
        h = max(maior(fonte), livre // 2)
        for i, (area, fx, msg) in enumerate(avaliacoes):
            r = pygame.Rect((i % 2) * meia, y + (i // 2) * h, meia, h)
            _faixa_area(sup, lay, f, r, area, fx, msg, S(20) if i % 2 else M, fonte)
            rects[f"faixa_{area}"] = r
        y += 2 * h
    rects["conteudo"] = pygame.Rect(0, topo, lay.W if lay.retrato else M + grade_w, y - topo)

    if lay.retrato:
        bc = pygame.Rect(M, lay.H - M - S(72), largura, S(72))
    else:
        coluna = pygame.Rect(M + grade_w + S(16), S(40), lay.W - M - (M + grade_w + S(16)), S(380))
        _painel_boneco(sup, lay, f, coluna, est, ent, cor_txt=TINTA)
        bc = pygame.Rect(lay.W - M - S(240), lay.H - M - S(56), S(240), S(56))
    ui.botao(sup, f["perg"] if lay.retrato else f["txt"], bc, "Continuar ›", ent.mouse, k=k)
    if _clicou(ent, bc):
        trocar(est, "retorno", ent.agora_ms)
    rects["continuar"] = bc
    return rects


# ---------------------------------------------------------------- retorno (tela 2: IMC e quando voltar)
def _retorno(sup, lay, f, est, ent):
    M, S, k = lay.margem, lay.s, lay.k
    largura = lay.W - 2 * M
    col_w = largura if lay.retrato else largura - S(250)
    y = S(56) if lay.retrato else S(40)
    rects = {}
    if est.modo == "quiz":
        imc = calcular_imc(int(est.peso), int(est.altura), int(est.idade))
        sup.blit(f["tit"].render("Seu IMC", True, TINTA), (M, y))
        y += f["tit"].get_linesize()
        valor = f["grande"].render(formatar_decimal(imc.valor), True, TINTA)
        sup.blit(valor, (M, y))
        if imc.classificacao:
            _selo(sup, f, imc.classificacao, COR_NIVEL[imc.nivel],
                  (M + valor.get_width() + S(20), y + valor.get_height() // 2), lay, ancora="midleft")
        y += f["grande"].get_linesize()
        y = ui.desenhar_texto(sup, imc.observacao + " O IMC é só uma referência.", f["txt"], TINTA, M, y,
                              col_w, espaco=S(4))
        rects["imc"] = pygame.Rect(M, S(40), col_w, y - S(40))
    else:
        sup.blit(f["tit"].render("Até a próxima!", True, TINTA), (M, y))
        y += f["tit"].get_linesize()
        y = ui.desenhar_texto(sup, "Você revisou os quatro hábitos hoje. Siga as orientações e volte em 2 dias "
                              "para ver como foi.", f["txt"], TINTA, M, y, col_w, espaco=S(4))
    rects["conteudo"] = pygame.Rect(M, 0, col_w, y)

    retorno = f"Volte dia {data_retorno(est.hoje)} para o acompanhamento."
    bv_h = S(72) if lay.retrato else S(56)
    bv = pygame.Rect(M, lay.H - M - bv_h, largura if lay.retrato else S(240), bv_h)
    n_ret = len(ui.quebrar(retorno, f["perg"], col_w))
    n_av = len(ui.quebrar(AVISO_SAUDE, f["peq"], col_w))
    topo = bv.y - S(24) - n_ret * f["perg"].get_linesize() - n_av * f["peq"].get_linesize()
    y2 = ui.desenhar_texto(sup, retorno, f["perg"], TINTA, M, topo, col_w, espaco=0)
    ui.desenhar_texto(sup, AVISO_SAUDE, f["peq"], TINTA, M, y2, col_w, espaco=0)
    if lay.retrato and topo - y > S(160):     # a bandeira preenche o meio da tela
        _faixas_de_cor(sup, pygame.Rect(0, y + S(40), lay.W, topo - y - S(80)), vertical=False)
    if not lay.retrato:     # a bandeira volta na coluna da direita, com o boneco
        regiao = pygame.Rect(M + col_w + S(40), 0, lay.W - (M + col_w + S(40)), lay.H)
        _faixas_de_cor(sup, regiao, vertical=False)
        _painel_boneco(sup, lay, f, regiao.inflate(0, -S(60)), est, ent)
    ui.botao(sup, f["txt"], bv, "Voltar ao início", ent.mouse, k=k)
    if _clicou(ent, bv):
        trocar(est, "inicio", ent.agora_ms)
    rects["voltar"] = bv
    rects["rodape"] = pygame.Rect(M, topo, lay.W - 2 * M, lay.H - M - topo)
    return rects
