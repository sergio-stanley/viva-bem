"""Estado do quiz e desenho/entrada de cada tela do Viva Bem (PC deitado e celular em pé)."""
import datetime
from dataclasses import dataclass, field

import pygame

from conteudo import AREAS, PERGUNTAS, ACOMPANHAMENTO, OPCOES_ACOMP, AVISO_SAUDE, ROTULO_FAIXA, SITE
from regras import (avaliar_area, pontos_por_area, calcular_imc, formatar_decimal, validar_dados,
                    titulo, data_retorno, aceita_clique, energia, aproximar, LIMITE_NOME)
import ui
from boneco import desenhar_boneco
from ui import ACC, INK, MUTE, WARN, BG, COR_FAIXA, COR_NIVEL


@dataclass
class Entrada:
    mouse: tuple
    clique: object          # (x, y) ou None
    teclas: list
    agora_ms: int


@dataclass
class Estado:
    tela: str = "inicio"    # inicio | dados | quiz | acomp | resultado | feedback
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
    alvo = energia(est.respostas) if est.tela in ("quiz", "acomp", "resultado", "feedback") else 0.5
    est.energia_vista = aproximar(est.energia_vista, alvo, dt)
    clique = ent.clique if aceita_clique(ent.agora_ms - est.ms_troca) else None
    ent = Entrada(ent.mouse, clique, ent.teclas, ent.agora_ms)
    if est.tela == "dados" and form is not None:
        rects = _dados_formulario(sup, lay, fontes, est, ent, form)
    else:
        tela = {"inicio": _inicio, "dados": _dados, "quiz": _perguntas, "acomp": _perguntas,
                "resultado": _resultado, "feedback": _resultado}[est.tela]
        rects = tela(sup, lay, fontes, est, ent)
    ui.fade(sup, ent.agora_ms - est.ms_troca)
    return rects


def _clicou(ent, rect):
    return ent.clique is not None and rect.collidepoint(ent.clique)


def _rotulo_energia(e):
    if e < 0.35:
        return "Sem energia", ui.BAD
    if e < 0.7:
        return "Energia ok", WARN
    return "Cheio de energia!", ui.OK


def _painel_boneco(sup, lay, f, painel, est, ent, legenda=True):
    """Boneco de energia centralizado num painel (só no PC)."""
    S = lay.s
    altura = min(S(300), painel.h - S(90))
    centro = (painel.centerx, painel.y + S(30) + altura // 2)
    desenhar_boneco(sup, centro, altura, est.energia_vista, ent.agora_ms)
    if legenda:
        texto, cor = _rotulo_energia(est.energia_vista)
        img = f["txt"].render(texto, True, cor)
        sup.blit(img, img.get_rect(midtop=(painel.centerx, centro[1] + altura // 2 + S(12))))


# ---------------------------------------------------------------- início
def _inicio(sup, lay, f, est, ent):
    M, S, k = lay.margem, lay.s, lay.k
    texto = ("Responda 8 perguntas sobre sono, água, exercício e alimentação e receba "
             "orientações para melhorar sua rotina. Refaça a cada 2 dias para acompanhar seu progresso.")
    aviso = AVISO_SAUDE + " Nenhum dado é guardado."
    if lay.retrato:
        largura = lay.W - 2 * M
        sup.blit(f["tit"].render("Viva Bem", True, ACC), (M, S(80)))
        y = ui.desenhar_texto(sup, texto, f["txt"], MUTE, M, S(150), largura, espaco=S(4))
        passo = largura // 4
        for i, area in enumerate(AREAS):
            cx, cy = M + passo // 2 + i * passo, y + S(70)
            ui.icone(sup, area, (cx, cy), S(32), ACC, k=k)
            img = f["peq"].render(area, True, INK)
            sup.blit(img, img.get_rect(midtop=(cx, cy + S(40))))
        r1 = pygame.Rect(M, lay.H - S(330), largura, S(84))
        r2 = pygame.Rect(M, lay.H - S(230), largura, S(84))
        fonte_bt = f["txt"]
        ui.desenhar_texto(sup, aviso, f["peq"], MUTE, M, lay.H - M - S(56), largura, espaco=0)
    else:
        col_w = lay.W - 2 * M - S(270)
        sup.blit(f["tit"].render("Viva Bem", True, ACC), (M, S(48)))
        ui.desenhar_texto(sup, texto, f["txt"], MUTE, M, S(112), col_w, espaco=S(4))
        r1 = pygame.Rect(M, S(270), col_w, S(72))
        r2 = pygame.Rect(M, S(360), col_w, S(72))
        fonte_bt = f["perg"]
        ui.desenhar_texto(sup, aviso, f["peq"], MUTE, M, lay.H - M - S(22), col_w, espaco=S(4))
        painel = pygame.Rect(lay.W - M - S(240), S(48), S(240), lay.H - S(48) - M)
        ui.card(sup, painel, k=k)
        qr = ui.imagem("qrcode.png")
        if qr is not None:      # para o público escanear durante a apresentação
            # ampliado/reduzido sem suavizar (transform.scale): o QR continua com bordas nítidas
            lado = min(painel.w - S(40), S(qr.get_width()))
            if lado != qr.get_width():
                qr = pygame.transform.scale(qr, (lado, lado))
            r_qr = qr.get_rect(midtop=(painel.centerx, painel.y + S(20)))
            sup.blit(qr, r_qr)
            y = r_qr.bottom + S(10)
            for linha in ui.quebrar("Aponte a câmera do celular", f["peq"], painel.w - S(30)):
                img = f["peq"].render(linha, True, INK)
                sup.blit(img, img.get_rect(midtop=(painel.centerx, y)))
                y += f["peq"].get_linesize()
            site = f["peq"].render(SITE, True, ACC)
            sup.blit(site, site.get_rect(midtop=(painel.centerx, y + S(2))))
            _painel_boneco(sup, lay, f, pygame.Rect(painel.x, y + S(20), painel.w, painel.bottom - y - S(20)),
                           est, ent, legenda=False)
            extras = {"qr": r_qr}
        else:
            _painel_boneco(sup, lay, f, pygame.Rect(painel.x, painel.y, painel.w, S(330)), est, ent, legenda=False)
            for i, area in enumerate(AREAS):
                ui.icone(sup, area, (painel.x + S(36) + i * S(56), painel.bottom - S(60)), S(20), ACC, k=k)
            extras = {}
    ui.botao(sup, fonte_bt, r1, "Primeira vez: começar o quiz", ent.mouse, primario=True, k=k)
    ui.botao(sup, fonte_bt, r2, "Já fiz antes: acompanhamento", ent.mouse, k=k)
    if _clicou(ent, r1):
        est.modo = "quiz"
        trocar(est, "dados", ent.agora_ms)
    elif _clicou(ent, r2):
        est.modo = "acomp"
        trocar(est, "dados", ent.agora_ms)
    rects = {"primeira_vez": r1, "ja_fiz": r2}
    if not lay.retrato:
        rects.update(extras)
    return rects


# ---------------------------------------------------------------- dados (teclado físico)
def _dados(sup, lay, f, est, ent):
    M, S, k = lay.margem, lay.s, lay.k
    col_w = lay.W - 2 * M if lay.retrato else int((lay.W - 2 * M) * 0.6)
    sup.blit(f["tit"].render("Antes de começar", True, ACC), (M, S(40)))
    ui.desenhar_texto(sup, "Seus dados não são guardados — servem só para o resultado.",
                      f["peq"], MUTE, M, S(96), col_w, espaco=S(4))
    caixas = [pygame.Rect(M, S(170), col_w, S(52))]
    w3 = (col_w - S(32)) // 3
    caixas += [pygame.Rect(M + i * (w3 + S(16)), S(270), w3, S(52)) for i in range(3)]
    rotulos = ["Nome (opcional)", "Idade", "Altura", "Peso"]
    unidades = ["", "anos", "cm", "kg"]
    valores = [est.nome, est.idade, est.altura, est.peso]
    for i in range(4):
        ui.campo(sup, f, caixas[i], rotulos[i], valores[i], unidades[i], est.campo == i, k=k)
    erro = validar_dados(est.nome, est.idade, est.altura, est.peso)
    valido = erro is None
    if erro and (est.idade or est.altura or est.peso):
        ui.desenhar_texto(sup, erro, f["peq"], WARN, M, S(334), col_w, espaco=S(4))
    if lay.retrato:
        bc = pygame.Rect(M, lay.H - M - S(72), col_w, S(72))
        lado = pygame.Rect(M, S(400), col_w, S(200))
    else:
        bc = pygame.Rect(M, lay.H - M - S(64), S(220), S(64))
        lado = pygame.Rect(M + col_w + S(32), S(170), lay.W - 2 * M - col_w - S(32), S(224))
    ui.botao(sup, f["perg"], bc, "Continuar ›", ent.mouse, ativo=valido, primario=True, k=k)
    if lay.retrato:
        bvolta = pygame.Rect(M, bc.y - S(84), col_w, S(72))
    else:
        bvolta = pygame.Rect(bc.right + S(16), bc.y, S(160), bc.h)
    ui.botao(sup, f["txt"], bvolta, "‹ Voltar", ent.mouse, k=k)
    ui.card(sup, lado, k=k)
    sup.blit(f["txt"].render("Por que pedimos isso?", True, ACC), (lado.x + S(18), lado.y + S(16)))
    y = ui.desenhar_texto(sup, "Idade, altura e peso servem para calcular seu IMC. "
                          "O nome só personaliza o título.", f["peq"], INK, lado.x + S(18), lado.y + S(56),
                          lado.w - S(36), espaco=S(4))
    ui.desenhar_texto(sup, "Tab ou Enter: próximo campo · Esc: voltar", f["peq"], MUTE,
                      lado.x + S(18), y + S(14), lado.w - S(36), espaco=0)

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
    sup.blit(f["tit"].render("Antes de começar", True, ACC), (lay.margem, lay.s(60)))
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
    col_w = lay.W - 2 * M if lay.retrato else int((lay.W - 2 * M) * 0.62)

    pygame.draw.rect(sup, BG, (M, S(40), col_w, S(10)), border_radius=S(5))
    pygame.draw.rect(sup, ACC, (M, S(40), max(S(10), int(col_w * est.indice / len(lista))), S(10)),
                     border_radius=S(5))
    ui.icone(sup, area, (M + S(18), S(88)), S(18), ACC, k=k)
    sup.blit(f["peq"].render(f"{area.upper()}   ·   Pergunta {est.indice + 1} de {len(lista)}", True, MUTE),
             (M + S(46), S(78)))
    ui.desenhar_texto(sup, texto, f["perg"], INK, M, S(140 if lay.retrato else 130), col_w, espaco=S(4))

    altura_op, gap = (S(92), S(18)) if lay.retrato else (S(72), S(16))
    y0 = lay.H - M - (3 * altura_op + 2 * gap)
    rects = {}
    for i, (t, p) in enumerate(opcoes):
        r = pygame.Rect(M, y0 + i * (altura_op + gap), col_w, altura_op)
        ui.botao(sup, f["txt"], r, t, ent.mouse, k=k)
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
        painel = pygame.Rect(M + col_w + S(32), S(40), lay.W - 2 * M - col_w - S(32), lay.H - S(40) - M)
        ui.card(sup, painel, k=k)
        _painel_boneco(sup, lay, f, painel.inflate(0, -S(40)), est, ent)
    return rects


# ---------------------------------------------------------------- resultado / feedback
def _titulo_resultado(sup, lay, f, texto, x, y, largura):
    """Título grande; se não couber (nome longo / tela estreita), quebra em fonte menor. Devolve o y final."""
    img = f["tit"].render(texto, True, ACC)
    if img.get_width() <= largura:
        sup.blit(img, (x, y))
        return y + img.get_height()
    return ui.desenhar_texto(sup, texto, f["perg"], ACC, x, y + lay.s(6), largura, espaco=0)


def _card_area(sup, lay, f, r, area, fx, msg, progresso):
    S, k = lay.s, lay.k
    ui.card(sup, r, k=k)
    cor = COR_FAIXA[fx]
    ui.icone(sup, area, (r.x + S(28), r.y + S(26)), S(18), cor, k=k)
    sup.blit(f["txt"].render(area, True, INK), (r.x + S(54), r.y + S(26) - f["txt"].get_height() // 2))
    rot = f["peq"].render(ROTULO_FAIXA[fx], True, cor)
    sup.blit(rot, rot.get_rect(midright=(r.right - S(16), r.y + S(54))))
    ui.barra(sup, (r.x + S(16), r.y + S(49), r.w - S(44) - rot.get_width(), S(10)), (fx + 1) / 3 * progresso,
             cor, k=k)
    ui.desenhar_texto(sup, msg, f["peq"], MUTE, r.x + S(16), r.y + S(66), r.w - S(32), espaco=0)


def _altura_card(lay, f, msg, largura):
    S = lay.s
    return S(66) + len(ui.quebrar(msg, f["peq"], largura - S(32))) * f["peq"].get_linesize() + S(10)


def _resultado(sup, lay, f, est, ent):
    M, S, k = lay.margem, lay.s, lay.k
    modo = "quiz" if est.tela == "resultado" else "acomp"
    progresso = min(1.0, (ent.agora_ms - est.ms_troca) / 600)
    largura = lay.W - 2 * M
    grade_w = largura if lay.retrato else largura - S(210)
    y = _titulo_resultado(sup, lay, f, titulo(est.nome, modo), M, S(18), grade_w - S(90))
    idade = f["peq"].render(f"{est.idade} anos", True, MUTE)
    sup.blit(idade, idade.get_rect(bottomright=(M + grade_w, y - S(6))))
    y += S(8)

    pontos = pontos_por_area(est.respostas)
    lh = f["peq"].get_linesize()
    avaliacoes = [(area,) + avaliar_area(area, pontos[area], modo) for area in AREAS]
    if lay.retrato:
        for area, fx, msg in avaliacoes:
            ch = _altura_card(lay, f, msg, grade_w)
            _card_area(sup, lay, f, pygame.Rect(M, y, grade_w, ch), area, fx, msg, progresso)
            y += ch + S(10)
    else:
        cw = (grade_w - S(12)) // 2
        ch = max(_altura_card(lay, f, m, cw) for _, _, m in avaliacoes)
        for i, (area, fx, msg) in enumerate(avaliacoes):
            r = pygame.Rect(M + (i % 2) * (cw + S(12)), y + (i // 2) * (ch + S(10)), cw, ch)
            _card_area(sup, lay, f, r, area, fx, msg, progresso)
        y += 2 * (ch + S(10))

    if modo == "quiz":
        imc = calcular_imc(int(est.peso), int(est.altura), int(est.idade))
        cor = COR_NIVEL[imc.nivel]
        obs = imc.observacao + " O IMC é só uma referência."
        linhas = ui.quebrar(obs, f["peq"], grade_w - S(32))
        r = pygame.Rect(M, y, grade_w, S(42) + len(linhas) * lh)
        ui.card(sup, r, borda=cor, k=k)
        linha = f"IMC {formatar_decimal(imc.valor)}" + (f"  ·  {imc.classificacao}" if imc.classificacao else "")
        sup.blit(f["txt"].render(linha, True, cor), (r.x + S(16), r.y + S(6)))
        ui.desenhar_texto(sup, obs, f["peq"], INK, r.x + S(16), r.y + S(36), grade_w - S(32), espaco=0)
        y = r.bottom
    conteudo = pygame.Rect(M, 0, grade_w, y)
    if not lay.retrato:
        coluna = pygame.Rect(M + grade_w + S(16), S(70), lay.W - M - (M + grade_w + S(16)), S(380))
        _painel_boneco(sup, lay, f, coluna, est, ent)

    # rodapé fixo: lembrete de retorno + aviso de saúde + botão
    retorno = f"Volte dia {data_retorno(est.hoje)} para o acompanhamento."
    lh_txt = f["txt"].get_linesize()
    if lay.retrato:
        bv = pygame.Rect(M, lay.H - M - S(64), largura, S(64))
        n_ret = len(ui.quebrar(retorno, f["txt"], largura))
        n_av = len(ui.quebrar(AVISO_SAUDE, f["peq"], largura))
        topo = bv.y - S(12) - n_ret * lh_txt - n_av * lh
        y2 = ui.desenhar_texto(sup, retorno, f["txt"], INK, M, topo, largura, espaco=0)
        ui.desenhar_texto(sup, AVISO_SAUDE, f["peq"], MUTE, M, y2, largura, espaco=0)
    else:
        bv = pygame.Rect(lay.W - M - S(240), lay.H - M - S(56), S(240), S(56))
        topo = bv.y - S(4)
        sup.blit(f["txt"].render(retorno, True, INK), (M, topo))
        ui.desenhar_texto(sup, AVISO_SAUDE, f["peq"], MUTE, M, topo + lh_txt, bv.x - M - S(24), espaco=0)
    rodape = pygame.Rect(M, topo, lay.W - 2 * M, lay.H - M - topo)
    ui.botao(sup, f["txt"], bv, "Voltar ao início", ent.mouse, k=k)
    if _clicou(ent, bv):
        trocar(est, "inicio", ent.agora_ms)
    return {"voltar": bv, "conteudo": conteudo, "rodape": rodape}
