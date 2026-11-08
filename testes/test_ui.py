import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import pytest

pygame.init()

from ui import (Layout, carregar_fontes, criar_fundo, card, botao, campo, barra, icone, fade,
                COR_FAIXA, COR_NIVEL, OK, WARN, BAD, ACC)


def test_layout():
    assert Layout(540, 960).retrato is True
    assert Layout(960, 600).retrato is False
    assert Layout(540, 960).margem == 28 and Layout(960, 600).margem == 40


@pytest.mark.parametrize("lay", [Layout(540, 960), Layout(960, 600)])
def test_fontes_com_acentos(lay):
    f = carregar_fontes(lay)
    assert set(f) == {"tit", "perg", "txt", "peq"}
    assert f["txt"].size("Ação, água e coração")[0] > 0


def test_fontes_tamanho_maior_no_retrato():
    assert carregar_fontes(Layout(540, 960))["txt"].get_height() > \
        carregar_fontes(Layout(960, 600))["txt"].get_height()


def test_cores():
    assert COR_FAIXA == (BAD, WARN, OK)
    assert COR_NIVEL == {"ok": OK, "atencao": WARN, "info": ACC}


def test_fundo_tamanho():
    assert criar_fundo(Layout(960, 600)).get_size() == (960, 600)
    assert criar_fundo(Layout(540, 960)).get_size() == (540, 960)


def test_desenha_sem_erro():
    lay = Layout(960, 600)
    f = carregar_fontes(lay)
    sup = pygame.Surface((960, 600))
    r = pygame.Rect(40, 40, 300, 60)
    card(sup, r)
    for kw in ({}, {"ativo": False}, {"primario": True}):
        botao(sup, f["txt"], r, "Continuar ›", (50, 50), **kw)
    for focado in (True, False):
        campo(sup, f, r, "Altura", "170", "cm", focado)
    for fr in (0, 0.5, 1):
        barra(sup, pygame.Rect(40, 200, 200, 12), fr, OK)
    for area in ("Sono", "Água", "Exercício", "Alimentação"):
        icone(sup, area, (100, 300), 18, ACC)
    for ms in (0, 100, 300):
        fade(sup, ms)


def test_fade_some_depois_de_200ms():
    sup = pygame.Surface((10, 10))
    sup.fill((255, 255, 255))
    fade(sup, 300)
    assert sup.get_at((5, 5))[:3] == (255, 255, 255)
    fade(sup, 0)
    assert sup.get_at((5, 5))[:3] != (255, 255, 255)


def test_botao_inativo_mais_apagado():
    lay = Layout(960, 600)
    f = carregar_fontes(lay)
    a = pygame.Surface((300, 80)); b = pygame.Surface((300, 80))
    r = pygame.Rect(0, 0, 300, 80)
    botao(a, f["txt"], r, "X", (-1, -1), primario=True)
    botao(b, f["txt"], r, "X", (-1, -1), primario=True, ativo=False)
    assert sum(a.get_at((150, 10))[:3]) > sum(b.get_at((150, 10))[:3])


# ------------------------------------------------------------ escala (nitidez em telas de alta densidade)
def test_layout_com_escala_dobra_margem_e_medidas():
    lay = Layout(1920, 1200, 2)
    assert lay.k == 2 and lay.s(28) == 56 and lay.margem == 80
    assert Layout(1080, 2160, 2).margem == 56
    assert Layout(960, 600).k == 1 and Layout(960, 600).s(28) == 28


def test_fontes_acompanham_a_escala():
    base = carregar_fontes(Layout(960, 600))["txt"].get_height()
    dobro = carregar_fontes(Layout(1920, 1200, 2))["txt"].get_height()
    assert 1.8 * base <= dobro <= 2.2 * base


def test_pecas_desenham_com_escala():
    lay = Layout(1920, 1200, 2)
    f = carregar_fontes(lay)
    sup = pygame.Surface((1920, 1200))
    r = pygame.Rect(80, 80, 600, 120)
    card(sup, r, k=2)
    botao(sup, f["txt"], r, "Continuar ›", (90, 90), k=2)
    campo(sup, f, r, "Altura", "170", "cm", True, k=2)
    barra(sup, pygame.Rect(80, 400, 400, 24), 0.5, OK, k=2)
    icone(sup, "Exercício", (200, 600), 36, ACC, k=2)
