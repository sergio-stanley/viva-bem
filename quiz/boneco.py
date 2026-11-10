"""Boneco de energia do Viva Bem (só no PC): reage às respostas mudando a disposição, nunca o corpo.

energia 0 → cinza, curvado, braços caídos, olheiras e "z z"
energia 0,5 → amarelo, em pé, braços ao lado
energia 1 → verde, braços para cima, sorriso e estrelinhas
"""
import math

import pygame

from ui import MEDIO as WARN, BOM as OK, BRANCO, TINTA, mistura

PERNA, ACC, MUTE = mistura(BRANCO, TINTA, 0.25), BRANCO, mistura(BRANCO, TINTA, 0.35)   # claros: o fundo é a cor da área

CINZA = (91, 107, 117)
PELE_CANSADA, PELE = (217, 180, 154), (246, 201, 168)
OLHO = (7, 22, 31)

# posições das mãos (desenho base de 90 x 150): energia 0 / 0,5 / 1
_MAOS = [((20, 94), (70, 94)), ((22, 90), (68, 90)), ((12, 28), (78, 28))]
_fontes = {}


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def _ponto(chaves, e):
    """Interpola entre os quadros-chave de energia 0, 0,5 e 1."""
    if e <= 0.5:
        return _mix(chaves[0], chaves[1], e / 0.5)
    return _mix(chaves[1], chaves[2], (e - 0.5) / 0.5)


def _cor_corpo(e):
    return _mix(CINZA, WARN, e / 0.5) if e <= 0.5 else _mix(WARN, OK, (e - 0.5) / 0.5)


def _fonte(tam):
    if tam not in _fontes:
        _fontes[tam] = pygame.font.Font(None, tam)
    return _fontes[tam]


def desenhar_boneco(sup, centro, altura, energia, t_ms):
    """Desenha o boneco com o tronco centrado em `centro`. `altura` = altura total em pixels."""
    e = max(0.0, min(1.0, energia))
    u = altura / 150

    def P(x, y):
        return int(x * u), int(y * u)

    cam = pygame.Surface((int(90 * u) + 2, int(150 * u) + 2), pygame.SRCALPHA)
    cor = _cor_corpo(e)

    for x in (31, 47):                            # pernas
        pygame.draw.rect(cam, PERNA, (*P(x, 100), int(12 * u), int(40 * u)), border_radius=int(5 * u))
    esq, dir_ = _ponto([m[0] for m in _MAOS], e), _ponto([m[1] for m in _MAOS], e)
    for ombro, mao in ((P(30, 56), P(*esq)), (P(60, 56), P(*dir_))):     # braços
        pygame.draw.line(cam, cor, ombro, mao, max(2, int(8 * u)))
        pygame.draw.circle(cam, cor, mao, max(2, int(4 * u)))
    pygame.draw.rect(cam, cor, (*P(28, 48), int(34 * u), int(54 * u)), border_radius=int(14 * u))  # tronco

    pele = _mix(PELE_CANSADA, PELE, e)
    pygame.draw.circle(cam, pele, P(45, 28), int(16 * u))                 # cabeça
    if e < 0.3:                                   # olhos cansados com olheiras
        for x in (39, 51):
            pygame.draw.line(cam, OLHO, P(x - 3, 27), P(x + 3, 27), max(1, int(2 * u)))
            pygame.draw.arc(cam, MUTE, (*P(x - 4, 28), int(8 * u), int(4 * u)), math.pi, 2 * math.pi, 1)
    else:
        for x in (39, 51):
            pygame.draw.circle(cam, OLHO, P(x, 26), max(1, int(2 * u)))
    curva = -3 + 8 * e                            # boca: triste → neutra → sorriso
    boca = [P(45 + x, 35 + curva * (1 - (x / 7) ** 2) - curva * 0.3) for x in range(-7, 8)]
    pygame.draw.lines(cam, OLHO, False, boca, max(1, int(2 * u)))

    if e < 0.3:                                   # z z
        img = _fonte(max(10, int(13 * u))).render("z z", True, MUTE)
        img.set_alpha(int(255 * (0.3 - e) / 0.3))
        cam.blit(img, P(60, 2 + 2 * math.sin(t_ms / 500)))
    if e > 0.75:                                  # estrelinhas
        brilho = 0.6 + 0.4 * math.sin(t_ms / 300)
        for x, y, r in ((10, 16, 4), (80, 12, 3)):
            rr = r * u * brilho
            cx, cy = P(x, y)
            pygame.draw.polygon(cam, ACC, [(cx, cy - rr), (cx + rr * 0.4, cy), (cx, cy + rr), (cx - rr * 0.4, cy)])
            pygame.draw.polygon(cam, ACC, [(cx - rr, cy), (cx, cy - rr * 0.4), (cx + rr, cy), (cx, cy + rr * 0.4)])

    inclinacao = 8 * (1 - min(1.0, e / 0.5))     # graus; curvado quando cansado
    if inclinacao > 0.01:
        cam = pygame.transform.rotate(cam, -inclinacao)
    respira = math.sin(t_ms / 600) * altura * 0.015
    sup.blit(cam, cam.get_rect(center=(centro[0], int(centro[1] + respira))))
