import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import pytest

pygame.init()

from ui import Layout, carregar_fontes, criar_fundo
from telas import Estado, Entrada, desenhar

LAY = Layout(960, 600)
F = carregar_fontes(LAY)
FUNDO = criar_fundo(LAY)
SUP = pygame.Surface((LAY.W, LAY.H))


class Relogio:
    t = 10_000


def passo(est, clique=None, teclas=(), agora=None, lay=LAY, fontes=F, fundo=FUNDO, sup=SUP, **kw):
    if agora is None:
        Relogio.t += 1000
        agora = Relogio.t
    ent = Entrada(mouse=(0, 0), clique=clique, teclas=list(teclas), agora_ms=agora)
    return desenhar(sup, lay, fontes, fundo, est, ent, **kw)


def tocar(est, nome, **kw):
    rects = passo(est, **kw)
    assert nome in rects, f"{nome} não está em {sorted(rects)}"
    return passo(est, clique=rects[nome].center, **kw)


def tecla(ch, key=None):
    return pygame.event.Event(pygame.KEYDOWN, key=key if key is not None else ord(ch), unicode=ch, mod=0)


def preencher(est, idade="23", altura="170", peso="65"):
    est.idade, est.altura, est.peso = idade, altura, peso


def test_fluxo_quiz_completo():
    est = Estado()
    tocar(est, "primeira_vez")
    assert est.tela == "dados"
    preencher(est)
    tocar(est, "continuar")
    assert est.tela == "quiz"
    for _ in range(8):
        tocar(est, "opcao0")
    assert est.tela == "resultado" and len(est.respostas) == 8
    tocar(est, "voltar")
    assert est.tela == "inicio"


def test_fluxo_acompanhamento():
    est = Estado()
    tocar(est, "ja_fiz")
    preencher(est)
    tocar(est, "continuar")
    assert est.tela == "acomp"
    for _ in range(4):
        tocar(est, "opcao1")
    assert est.tela == "feedback" and len(est.respostas) == 4


def test_continuar_inativo_com_dados_invalidos():
    est = Estado()
    tocar(est, "primeira_vez")
    preencher(est, altura="90")
    tocar(est, "continuar")
    assert est.tela == "dados"


def test_clique_logo_apos_troca_e_ignorado():
    est = Estado()
    tocar(est, "primeira_vez")
    preencher(est)
    rects = passo(est)
    T = Relogio.t + 1000
    passo(est, clique=rects["continuar"].center, agora=T)
    assert est.tela == "quiz"
    rects = passo(est, agora=T + 10)
    passo(est, clique=rects["opcao0"].center, agora=T + 50)
    assert est.indice == 0
    passo(est, clique=rects["opcao0"].center, agora=T + 200)
    assert est.indice == 1


def test_digitacao_teclado():
    est = Estado()
    tocar(est, "primeira_vez")
    est.campo = 1
    passo(est, teclas=[tecla("2"), tecla("3"), tecla("a")])
    assert est.idade == "23"
    passo(est, teclas=[tecla("\t", pygame.K_TAB)])
    assert est.campo == 2
    passo(est, teclas=[tecla("", pygame.K_BACKSPACE)])
    est.campo = 0
    passo(est, teclas=[tecla("A"), tecla("n"), tecla("a")])
    assert est.nome == "Ana"


def test_tocar_campo_muda_foco():
    est = Estado()
    tocar(est, "primeira_vez")
    tocar(est, "campo3")
    assert est.campo == 3


@pytest.mark.parametrize("idade", ["1", "120"])
@pytest.mark.parametrize("pts", [0, 2])
def test_resultado_valores_extremos(idade, pts):
    for tela in ("resultado", "feedback"):
        est = Estado(tela=tela, modo="quiz" if tela == "resultado" else "acomp",
                     nome="W" * 20, idade=idade, altura="100", peso="300")
        n = 8 if tela == "resultado" else 4
        areas = ["Sono", "Água", "Exercício", "Alimentação"]
        est.respostas = [(areas[i % 4], pts) for i in range(n)]
        rects = passo(est)
        assert "voltar" in rects


def test_resultado_sem_nome():
    est = Estado(tela="resultado", idade="30", altura="170", peso="65",
                 respostas=[("Sono", 1)] * 2 + [("Água", 1)] * 2 + [("Exercício", 1)] * 2 + [("Alimentação", 1)] * 2)
    passo(est)


def test_todas_as_telas_desenham_sem_erro():
    for tela in ("inicio", "dados", "quiz", "acomp"):
        passo(Estado(tela=tela))


def test_enter_no_ultimo_campo_continua_se_valido():
    est = Estado()
    tocar(est, "primeira_vez")
    preencher(est)
    est.campo = 3
    passo(est, teclas=[tecla("\r", pygame.K_RETURN)])
    assert est.tela == "quiz"


def test_enter_no_ultimo_campo_nao_continua_se_invalido():
    est = Estado()
    tocar(est, "primeira_vez")
    preencher(est, peso="5")
    est.campo = 3
    passo(est, teclas=[tecla("\r", pygame.K_RETURN)])
    assert est.tela == "dados"
