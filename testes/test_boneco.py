import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import pytest

pygame.init()

from boneco import desenhar_boneco

CENTRO = (150, 220)


def _foto(energia, t_ms=0):
    sup = pygame.Surface((300, 400))
    sup.fill((0, 0, 0))
    desenhar_boneco(sup, CENTRO, 300, energia, t_ms)
    return sup


@pytest.mark.parametrize("energia", [0, 0.25, 0.5, 0.75, 1])
@pytest.mark.parametrize("t_ms", [0, 1234])
def test_desenha_sem_erro(energia, t_ms):
    _foto(energia, t_ms)


@pytest.mark.parametrize("energia", [-1, 2])
def test_energia_fora_da_faixa_e_limitada(energia):
    limite = 0 if energia < 0 else 1
    assert pygame.image.tobytes(_foto(energia), "RGB") == pygame.image.tobytes(_foto(limite), "RGB")


def test_cor_do_tronco_muda_com_a_energia():
    # centro do tronco: cinza com energia baixa, verde com energia alta
    pos = (CENTRO[0], CENTRO[1] + 10)
    baixo, alto = _foto(0).get_at(pos)[:3], _foto(1).get_at(pos)[:3]
    assert baixo != alto
    assert alto[1] > alto[0] and alto[1] > alto[2]        # verde predominante


def test_respira_com_o_tempo():
    assert pygame.image.tobytes(_foto(0.5, 0), "RGB") != pygame.image.tobytes(_foto(0.5, 900), "RGB")


def test_sem_brilho_semitransparente():
    sup = pygame.Surface((200, 300), pygame.SRCALPHA)
    desenhar_boneco(sup, (100, 150), 240, 1.0, 0)
    alfas = {sup.get_at((x, y))[3] for x in range(200) for y in range(300)}
    assert alfas <= {0, 255}


# ------------------------------------------------------------ humor animado
def _topo(sup):
    """Linha do pixel mais alto que não é o fundo preto."""
    for y in range(sup.get_height()):
        for x in range(0, sup.get_width(), 2):
            if sup.get_at((x, y))[:3] != (0, 0, 0):
                return y
    return None


def _foto_r(energia, t_ms=0, reacao=0.0):
    sup = pygame.Surface((300, 400))
    sup.fill((0, 0, 0))
    desenhar_boneco(sup, CENTRO, 300, energia, t_ms, reacao)
    return sup


def test_feliz_pula_bem_mais_que_o_normal():
    def amplitude(e):
        topos = [_topo(_foto_r(e, t)) for t in range(0, 1600, 50)]
        return max(topos) - min(topos)
    assert amplitude(1.0) >= 3 * max(1, amplitude(0.5))


def test_triste_balanca_de_um_lado_para_o_outro():
    def centro_x(sup):
        xs = [x for x in range(sup.get_width()) for y in range(0, sup.get_height(), 4)
              if sup.get_at((x, y))[:3] != (0, 0, 0)]
        return sum(xs) / len(xs)
    lados = [centro_x(_foto_r(0.0, t)) for t in range(0, 6000, 250)]
    assert max(lados) - min(lados) >= 4


def test_triste_fica_mais_baixo_que_o_feliz_parado():
    # cabeça baixa: o topo do boneco triste fica abaixo do topo do feliz no mesmo instante de repouso
    assert _topo(_foto_r(0.0, 0)) > _topo(_foto_r(1.0, 0))


def test_reacao_boa_pula_e_ruim_murcha():
    base = _topo(_foto_r(0.5, 0))
    assert _topo(_foto_r(0.5, 0, reacao=1.0)) < base - 10
    assert _topo(_foto_r(0.5, 0, reacao=-1.0)) > base + 3
