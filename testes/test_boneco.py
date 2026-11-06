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
