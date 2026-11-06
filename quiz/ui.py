"""Peças visuais do Viva Bem — identidade "Noite serena" (fundo, fontes, cards, botões, ícones)."""
import math
import os
from dataclasses import dataclass

import pygame


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


BG, BG2 = _hex("#07161F"), _hex("#0F4C5C")
CARD, LINE = _hex("#0E2633"), _hex("#1F4A5E")
INK, MUTE, ACC = _hex("#E8F6F4"), _hex("#8FB5BD"), _hex("#2DD4BF")
BAD, WARN, OK = _hex("#F87171"), _hex("#FACC15"), _hex("#4ADE80")
HOVER = (20, 58, 76)
COR_FAIXA = (BAD, WARN, OK)
COR_NIVEL = {"ok": OK, "atencao": WARN, "info": ACC}

PASTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@dataclass
class Layout:
    W: int
    H: int

    @property
    def retrato(self) -> bool:
        return self.H > self.W

    @property
    def margem(self) -> int:
        return 28 if self.retrato else 40


def _fonte(arquivo, tamanho):
    caminho = os.path.join(PASTA_ASSETS, arquivo)
    try:
        return pygame.font.Font(caminho, tamanho)
    except (FileNotFoundError, OSError):
        return pygame.font.Font(None, int(tamanho * 1.25))


def carregar_fontes(lay: Layout) -> dict:
    t = (46, 32, 26, 20) if lay.retrato else (40, 28, 22, 17)
    return {"tit": _fonte("Nunito-ExtraBold.ttf", t[0]), "perg": _fonte("Nunito-ExtraBold.ttf", t[1]),
            "txt": _fonte("Nunito-Regular.ttf", t[2]), "peq": _fonte("Nunito-Regular.ttf", t[3])}


def _mistura(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def criar_fundo(lay: Layout) -> pygame.Surface:
    """Degradê radial (BG2 no canto superior direito → BG). Calculado pequeno e ampliado."""
    pw, ph = max(lay.W // 6, 2), max(lay.H // 6, 2)
    peq = pygame.Surface((pw, ph))
    cx, cy, raio = pw * 0.85, 0, max(pw, ph) * 0.9
    for y in range(ph):
        for x in range(pw):
            t = min(1.0, math.hypot(x - cx, y - cy) / raio)
            peq.set_at((x, y), _mistura(BG2, BG, t ** 0.8))
    return pygame.transform.smoothscale(peq, (lay.W, lay.H))


def quebrar(texto, fonte, largura):
    """Quebra o texto em linhas que cabem na largura."""
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if fonte.size(teste)[0] <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def desenhar_texto(sup, texto, fonte, cor, x, y, largura, espaco=4):
    for linha in quebrar(texto, fonte, largura):
        sup.blit(fonte.render(linha, True, cor), (x, y))
        y += fonte.get_linesize() + espaco
    return y


def card(sup, rect, borda=LINE):
    pygame.draw.rect(sup, CARD, rect, border_radius=16)
    pygame.draw.rect(sup, borda, rect, 1, border_radius=16)


def botao(sup, fonte, rect, texto, mouse, ativo=True, primario=False):
    rect = pygame.Rect(rect)
    sobre = ativo and rect.collidepoint(mouse)
    camada = pygame.Surface(rect.size, pygame.SRCALPHA)
    local = camada.get_rect()
    if primario:
        pygame.draw.rect(camada, _mistura(ACC, INK, 0.25) if sobre else ACC, local, border_radius=14)
        cor_txt = BG
    else:
        pygame.draw.rect(camada, HOVER if sobre else CARD, local, border_radius=14)
        pygame.draw.rect(camada, ACC if sobre else LINE, local, 2, border_radius=14)
        cor_txt = INK
    img = fonte.render(texto, True, cor_txt)
    camada.blit(img, img.get_rect(center=local.center))
    if not ativo:
        camada.set_alpha(110)
    sup.blit(camada, rect)


def campo(sup, fontes, rect, rotulo, valor, unidade, focado):
    rect = pygame.Rect(rect)
    sup.blit(fontes["peq"].render(rotulo, True, MUTE), (rect.x + 2, rect.y - fontes["peq"].get_linesize() - 4))
    pygame.draw.rect(sup, BG, rect, border_radius=12)
    pygame.draw.rect(sup, ACC if focado else LINE, rect, 2, border_radius=12)
    cursor = "|" if focado and (pygame.time.get_ticks() // 500) % 2 == 0 else ""
    img = fontes["txt"].render(valor + cursor, True, INK)
    sup.blit(img, img.get_rect(midleft=(rect.x + 14, rect.centery)))
    if unidade:
        u = fontes["peq"].render(unidade, True, MUTE)
        sup.blit(u, u.get_rect(midright=(rect.right - 12, rect.centery)))


def barra(sup, rect, fracao, cor):
    rect = pygame.Rect(rect)
    fracao = max(0.0, min(1.0, fracao))
    raio = rect.h // 2
    pygame.draw.rect(sup, BG, rect, border_radius=raio)
    if fracao <= 0:
        return
    cheio = pygame.Rect(rect.x, rect.y, max(rect.h, int(rect.w * fracao)), rect.h)
    brilho = pygame.Surface((cheio.w + 16, cheio.h + 16), pygame.SRCALPHA)
    for i, alfa in ((8, 30), (4, 55)):
        pygame.draw.rect(brilho, cor + (alfa,), (8 - i, 8 - i, cheio.w + 2 * i, cheio.h + 2 * i),
                         border_radius=raio + i)
    sup.blit(brilho, (cheio.x - 8, cheio.y - 8))
    pygame.draw.rect(sup, cor, cheio, border_radius=raio)


def icone(sup, area, centro, r, cor):
    """Ícones simples desenhados com formas: lua, gota, halter e maçã."""
    x, y = centro
    pygame.draw.circle(sup, HOVER, centro, r)
    s = r * 0.55
    if area == "Sono":
        pygame.draw.circle(sup, cor, (x, y), int(s))
        pygame.draw.circle(sup, HOVER, (int(x + s * 0.45), int(y - s * 0.35)), int(s * 0.85))
    elif area == "Água":
        pygame.draw.circle(sup, cor, (x, int(y + s * 0.3)), int(s * 0.7))
        pygame.draw.polygon(sup, cor, [(x, int(y - s)), (int(x - s * 0.62), int(y + s * 0.15)),
                                       (int(x + s * 0.62), int(y + s * 0.15))])
    elif area == "Exercício":
        pygame.draw.rect(sup, cor, (int(x - s), int(y - s * 0.12), int(2 * s), max(2, int(s * 0.24))))
        for lado in (-1, 1):
            pygame.draw.rect(sup, cor, (int(x + lado * s * 0.8 - s * 0.2), int(y - s * 0.55),
                                        int(s * 0.4), int(s * 1.1)), border_radius=3)
    else:  # Alimentação
        pygame.draw.ellipse(sup, cor, (int(x - s * 0.8), int(y - s * 0.5), int(s * 1.6), int(s * 1.45)))
        pygame.draw.circle(sup, HOVER, (x, int(y - s * 0.5)), max(1, int(s * 0.18)))
        pygame.draw.line(sup, cor, (x, int(y - s * 0.45)), (int(x + s * 0.15), int(y - s * 0.95)), 2)
        pygame.draw.ellipse(sup, OK, (int(x + s * 0.2), int(y - s * 1.05), int(s * 0.6), int(s * 0.3)))


def fade(sup, ms_desde_troca):
    """Escurece a tela logo após trocar de tela e vai clareando em 200 ms."""
    alfa = int(255 * (1 - ms_desde_troca / 200))
    if alfa <= 0:
        return
    veu = pygame.Surface(sup.get_size())
    veu.fill(BG)
    veu.set_alpha(min(255, alfa))
    sup.blit(veu, (0, 0))
