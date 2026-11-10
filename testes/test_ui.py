import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import pytest

pygame.init()

from ui import (Layout, carregar_fontes, criar_fundo, botao, campo, fade, escala_da_tela, COR_AREA, COR_FAIXA, COR_NIVEL,
                RUIM, MEDIO, BOM, AGUA, TINTA, BRANCO)


def test_layout():
    assert Layout(540, 960).retrato is True
    assert Layout(960, 600).retrato is False
    assert Layout(540, 960).margem == 28 and Layout(960, 600).margem == 40


@pytest.mark.parametrize("lay", [Layout(540, 960), Layout(960, 600)])
def test_fontes_com_acentos(lay):
    f = carregar_fontes(lay)
    assert set(f) == {"grande", "tit", "perg", "txt", "peq"}
    assert f["txt"].size("Ação, água e coração")[0] > 0


def test_fontes_tem_os_simbolos_usados():
    f = carregar_fontes(Layout(960, 600))
    for nome in ("tit", "txt"):
        for ch in "‹›·—ÁáâãçéêíóôõúÚ":
            assert f[nome].metrics(ch)[0] is not None, (nome, ch)


def test_fontes_tamanho_maior_no_retrato():
    assert carregar_fontes(Layout(540, 960))["txt"].get_height() > \
        carregar_fontes(Layout(960, 600))["txt"].get_height()


def _lum(c):
    f = [x / 255 for x in c]
    f = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in f]
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]


def test_branco_legivel_sobre_as_cores_das_areas():
    for area, cor in COR_AREA.items():
        assert 1.05 / (_lum(cor) + 0.05) >= 4.5, area


def test_cores():
    assert set(COR_AREA) == {"Sono", "Água", "Exercício", "Alimentação"}
    assert COR_FAIXA == (RUIM, MEDIO, BOM)
    assert set(COR_NIVEL) == {"ok", "atencao", "info"}


def test_fundo_chapado():
    s = criar_fundo(Layout(960, 600), AGUA)
    assert s.get_size() == (960, 600)
    assert s.get_at((0, 0))[:3] == AGUA and s.get_at((959, 599))[:3] == AGUA


def test_desenha_sem_erro():
    lay = Layout(960, 600)
    f = carregar_fontes(lay)
    sup = pygame.Surface((960, 600))
    r = pygame.Rect(40, 40, 300, 60)
    for kw in ({}, {"ativo": False}, {"cor": BRANCO, "cor_texto": AGUA}):
        botao(sup, f["txt"], r, "Continuar ›", (50, 50), **kw)
    for focado in (True, False):
        campo(sup, f, r, "Altura", "170", "cm", focado)
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
    f = carregar_fontes(Layout(960, 600))
    a = pygame.Surface((300, 80)); b = pygame.Surface((300, 80))
    a.fill(BRANCO); b.fill(BRANCO)
    r = pygame.Rect(0, 0, 300, 80)
    botao(a, f["txt"], r, "X", (-1, -1))
    botao(b, f["txt"], r, "X", (-1, -1), ativo=False)
    assert sum(a.get_at((150, 10))[:3]) < sum(b.get_at((150, 10))[:3])     # inativo: cor mais lavada


def test_botao_ativo_nao_cria_camada(monkeypatch):
    import ui
    real = ui.pygame.Surface
    f = carregar_fontes(Layout(960, 600))
    sup = real((300, 80))
    criadas = []
    monkeypatch.setattr(ui.pygame, "Surface", lambda *a, **k: criadas.append(a) or real(*a, **k))
    ui.botao(sup, f["txt"], (0, 0, 300, 80), "Ok", (-1, -1))
    assert criadas == []


def test_botao_e_pilula_sem_borda():
    f = carregar_fontes(Layout(960, 600))
    sup = pygame.Surface((300, 80)); sup.fill(BRANCO)
    botao(sup, f["txt"], (0, 0, 300, 80), "", (-1, -1), cor=TINTA)
    assert sup.get_at((1, 1))[:3] == BRANCO          # canto arredondado
    assert sup.get_at((150, 2))[:3] == TINTA          # sem borda de outra cor


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
    botao(sup, f["txt"], r, "Continuar ›", (90, 90), k=2)
    campo(sup, f, r, "Altura", "170", "cm", True, k=2)


@pytest.mark.parametrize("dpr,css,base,esperado", [
    (3, 390, 540, 2.25), (3.5, 412, 540, 2.5), (1, 1280, 960, 2), (2, 1920, 960, 2.5), (1, 1, 540, 2)])
def test_escala_da_tela(dpr, css, base, esperado):
    assert escala_da_tela(dpr, css, base) == esperado


def test_fonte_reaproveita_o_texto_ja_desenhado():
    f = carregar_fontes(Layout(960, 600))["txt"]
    a = f.render("Viva Bem", True, (1, 2, 3))
    assert f.render("Viva Bem", True, (1, 2, 3)) is a
    assert f.render("Viva Bem", True, (9, 9, 9)) is not a


def test_imagem_carregada_uma_vez():
    import ui
    assert ui.imagem("qrcode.png") is ui.imagem("qrcode.png")
