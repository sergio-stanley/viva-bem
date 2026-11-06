"""Estado do quiz e desenho/entrada de cada tela do Viva Bem."""
import datetime
from dataclasses import dataclass, field

import pygame

from conteudo import AREAS, PERGUNTAS, ACOMPANHAMENTO, OPCOES_ACOMP, AVISO_SAUDE, ROTULO_FAIXA
from regras import (avaliar_area, pontos_por_area, calcular_imc, formatar_decimal, validar_dados,
                    titulo, data_retorno, aceita_clique, LIMITE_NOME)
import ui
from ui import ACC, INK, MUTE, WARN, LINE, BG, COR_FAIXA, COR_NIVEL


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
    energia_vista: float = 0.5
    hoje: datetime.date = field(default_factory=datetime.date.today)


def trocar(est: Estado, tela: str, agora_ms: int):
    if tela == "dados":
        est.nome = est.idade = est.altura = est.peso = ""
        est.campo = 0
    if tela in ("quiz", "acomp"):
        est.indice, est.respostas = 0, []
    est.tela, est.ms_troca = tela, agora_ms


def desenhar(sup, lay, fontes, fundo, est: Estado, ent: Entrada) -> dict:
    sup.blit(fundo, (0, 0))
    clique = ent.clique if aceita_clique(ent.agora_ms - est.ms_troca) else None
    ent = Entrada(ent.mouse, clique, ent.teclas, ent.agora_ms)
    tela = {"inicio": _inicio, "dados": _dados, "quiz": _perguntas, "acomp": _perguntas,
            "resultado": _resultado, "feedback": _resultado}[est.tela]
    rects = tela(sup, lay, fontes, est, ent)
    ui.fade(sup, ent.agora_ms - est.ms_troca)
    return rects


def _clicou(ent, rect):
    return ent.clique is not None and rect.collidepoint(ent.clique)


# ---------------------------------------------------------------- início
def _inicio(sup, lay, f, est, ent):
    M = lay.margem
    col_w = lay.W - 2 * M - 270
    sup.blit(f["tit"].render("Viva Bem", True, ACC), (M, 48))
    ui.desenhar_texto(sup, "Responda 8 perguntas sobre sono, água, exercício e alimentação e receba "
                      "orientações para melhorar sua rotina. Refaça a cada 2 dias para acompanhar "
                      "seu progresso.", f["txt"], MUTE, M, 112, col_w)
    r1 = pygame.Rect(M, 270, col_w, 72)
    r2 = pygame.Rect(M, 360, col_w, 72)
    ui.botao(sup, f["perg"], r1, "Primeira vez: começar o quiz", ent.mouse, primario=True)
    ui.botao(sup, f["perg"], r2, "Já fiz antes: acompanhamento", ent.mouse)
    ui.desenhar_texto(sup, AVISO_SAUDE + " Nenhum dado é guardado.", f["peq"], MUTE, M, lay.H - M - 22, col_w)
    painel = pygame.Rect(lay.W - M - 240, 48, 240, lay.H - 48 - M)
    ui.card(sup, painel)
    for i, area in enumerate(AREAS):
        cx = painel.x + 66 + (i % 2) * 108
        cy = painel.y + 120 + (i // 2) * 130
        ui.icone(sup, area, (cx, cy), 34, ACC)
        img = f["peq"].render(area, True, INK)
        sup.blit(img, img.get_rect(midtop=(cx, cy + 42)))
    if _clicou(ent, r1):
        est.modo = "quiz"
        trocar(est, "dados", ent.agora_ms)
    elif _clicou(ent, r2):
        est.modo = "acomp"
        trocar(est, "dados", ent.agora_ms)
    return {"primeira_vez": r1, "ja_fiz": r2}


# ---------------------------------------------------------------- dados
def _dados(sup, lay, f, est, ent):
    M = lay.margem
    col_w = int((lay.W - 2 * M) * 0.6)
    sup.blit(f["tit"].render("Antes de começar", True, ACC), (M, 40))
    sup.blit(f["peq"].render("Seus dados não são guardados — servem só para o resultado.", True, MUTE), (M, 96))
    caixas = [pygame.Rect(M, 170, col_w, 52)]
    w3 = (col_w - 32) // 3
    caixas += [pygame.Rect(M + i * (w3 + 16), 270, w3, 52) for i in range(3)]
    rotulos = ["Nome (opcional)", "Idade", "Altura", "Peso"]
    unidades = ["", "anos", "cm", "kg"]
    valores = [est.nome, est.idade, est.altura, est.peso]
    for i in range(4):
        ui.campo(sup, f, caixas[i], rotulos[i], valores[i], unidades[i], est.campo == i)
    erro = validar_dados(est.nome, est.idade, est.altura, est.peso)
    valido = erro is None
    if erro and (est.idade or est.altura or est.peso):
        sup.blit(f["peq"].render(erro, True, WARN), (M, 334))
    bc = pygame.Rect(M, lay.H - M - 64, 220, 64)
    ui.botao(sup, f["perg"], bc, "Continuar ›", ent.mouse, ativo=valido, primario=True)

    lado = pygame.Rect(M + col_w + 32, 170, lay.W - 2 * M - col_w - 32, 200)
    ui.card(sup, lado)
    sup.blit(f["txt"].render("Por que pedimos isso?", True, ACC), (lado.x + 18, lado.y + 16))
    y = ui.desenhar_texto(sup, "Idade, altura e peso servem para calcular seu IMC. "
                          "O nome só personaliza o título.", f["peq"], INK, lado.x + 18, lado.y + 56, lado.w - 36)
    sup.blit(f["peq"].render("Tab ou Enter: próximo campo", True, MUTE), (lado.x + 18, y + 14))

    for ev in ent.teclas:
        if _tecla_dados(est, ev) and valido:
            trocar(est, est.modo, ent.agora_ms)
            return {}
    if ent.clique:
        for i, cx in enumerate(caixas):
            if cx.collidepoint(ent.clique):
                est.campo = i
        if _clicou(ent, bc) and valido:
            trocar(est, est.modo, ent.agora_ms)
    rects = {"continuar": bc}
    rects.update({f"campo{i}": c for i, c in enumerate(caixas)})
    return rects


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
        elif est.campo > 0 and ev.unicode.isdigit() and len(valor) < 3:
            setattr(est, attr, valor + ev.unicode)
    return False


# ---------------------------------------------------------------- perguntas
def _perguntas(sup, lay, f, est, ent):
    M = lay.margem
    lista = PERGUNTAS if est.tela == "quiz" else ACOMPANHAMENTO
    area, texto = lista[est.indice][0], lista[est.indice][1]
    opcoes = lista[est.indice][2] if est.tela == "quiz" else OPCOES_ACOMP
    col_w = int((lay.W - 2 * M) * 0.62)

    pygame.draw.rect(sup, BG, (M, 40, col_w, 10), border_radius=5)
    pygame.draw.rect(sup, ACC, (M, 40, max(10, int(col_w * est.indice / len(lista))), 10), border_radius=5)
    ui.icone(sup, area, (M + 18, 88), 18, ACC)
    sup.blit(f["peq"].render(f"{area.upper()}   ·   Pergunta {est.indice + 1} de {len(lista)}", True, MUTE),
             (M + 46, 78))
    ui.desenhar_texto(sup, texto, f["perg"], INK, M, 130, col_w)

    altura_op, gap = 72, 16
    y0 = lay.H - M - (3 * altura_op + 2 * gap)
    rects = {}
    for i, (t, p) in enumerate(opcoes):
        r = pygame.Rect(M, y0 + i * (altura_op + gap), col_w, altura_op)
        ui.botao(sup, f["txt"], r, t, ent.mouse)
        rects[f"opcao{i}"] = r
        if _clicou(ent, r):
            est.respostas.append((area, p))
            est.indice += 1
            if est.indice >= len(lista):
                trocar(est, "resultado" if est.tela == "quiz" else "feedback", ent.agora_ms)
            else:
                est.ms_troca = ent.agora_ms
            break
    painel = pygame.Rect(M + col_w + 32, 40, lay.W - 2 * M - col_w - 32, lay.H - 40 - M)
    ui.card(sup, painel)
    return rects


# ---------------------------------------------------------------- resultado / feedback
def _resultado(sup, lay, f, est, ent):
    M = lay.margem
    modo = "quiz" if est.tela == "resultado" else "acomp"
    ms = ent.agora_ms - est.ms_troca
    t = f["tit"].render(titulo(est.nome, modo), True, ACC)
    sup.blit(t, (M, 24))
    sup.blit(f["peq"].render(f"{est.idade} anos", True, MUTE), (M + t.get_width() + 16, 24 + t.get_height() - 30))

    grade_w = lay.W - 2 * M - 210
    cw, ch = (grade_w - 12) // 2, 142
    pontos = pontos_por_area(est.respostas)
    for i, area in enumerate(AREAS):
        fx, msg = avaliar_area(area, pontos[area], modo)
        r = pygame.Rect(M + (i % 2) * (cw + 12), 84 + (i // 2) * (ch + 12), cw, ch)
        ui.card(sup, r)
        cor = COR_FAIXA[fx]
        ui.icone(sup, area, (r.x + 28, r.y + 26), 18, cor)
        sup.blit(f["txt"].render(area, True, INK), (r.x + 54, r.y + 12))
        rot = f["peq"].render(ROTULO_FAIXA[fx], True, cor)
        sup.blit(rot, rot.get_rect(midright=(r.right - 16, r.y + 60)))
        ui.barra(sup, (r.x + 16, r.y + 55, r.w - 44 - rot.get_width(), 10),
                 (fx + 1) / 3 * min(1.0, ms / 600), cor)
        ui.desenhar_texto(sup, msg, f["peq"], MUTE, r.x + 16, r.y + 74, r.w - 32, espaco=0)

    y = 84 + 2 * (ch + 12)
    aviso = AVISO_SAUDE
    if modo == "quiz":
        imc = calcular_imc(int(est.peso), int(est.altura), int(est.idade))
        r = pygame.Rect(M, y, grade_w, 64)
        cor = COR_NIVEL[imc.nivel]
        ui.card(sup, r, borda=cor)
        linha = f"IMC {formatar_decimal(imc.valor)}" + (f"  ·  {imc.classificacao}" if imc.classificacao else "")
        sup.blit(f["txt"].render(linha, True, cor), (r.x + 16, r.y + 8))
        sup.blit(f["peq"].render(imc.observacao, True, INK), (r.x + 16, r.y + 38))
        y += 76
        aviso = "O IMC é só uma referência. " + AVISO_SAUDE
    else:
        y += 8
    sup.blit(f["txt"].render(f"Volte dia {data_retorno(est.hoje)} para o acompanhamento.", True, INK), (M, y))
    bv = pygame.Rect(lay.W - M - 240, lay.H - M - 52, 240, 52)
    ui.desenhar_texto(sup, aviso, f["peq"], MUTE, M, lay.H - M - 44, bv.x - M - 24, espaco=0)
    ui.botao(sup, f["txt"], bv, "Voltar ao início", ent.mouse)
    if _clicou(ent, bv):
        trocar(est, "inicio", ent.agora_ms)
    return {"voltar": bv}
