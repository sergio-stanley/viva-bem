"""Peças visuais do Viva Bem — identidade "Cores de Belém": cada área tem uma cor chapada da cidade."""
import os
from dataclasses import dataclass

import pygame


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


SONO, AGUA = _hex("#1F2A5A"), _hex("#0B5F8A")              # azul-noite, azul do rio
EXERCICIO, ALIMENTACAO = _hex("#1E6B3A"), _hex("#4B1D4F")  # verde das mangueiras, roxo do açaí
CLARO, TINTA, BRANCO = _hex("#EEF2F1"), _hex("#10202A"), _hex("#FFFFFF")
RUIM, MEDIO, BOM = _hex("#E5484D"), _hex("#F2B705"), _hex("#2FA65A")   # semáforo da avaliação
COR_AREA = {"Sono": SONO, "Água": AGUA, "Exercício": EXERCICIO, "Alimentação": ALIMENTACAO}
COR_FAIXA = (RUIM, MEDIO, BOM)
COR_NIVEL = {"ok": BOM, "atencao": MEDIO, "info": TINTA}

PASTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@dataclass
class Layout:
    """Tamanho real da tela em pixels. `k` é a escala: as medidas do desenho foram pensadas para
    960x600 (PC) e 540x1080 (celular); com k=2 tudo é desenhado no dobro, para ficar nítido em telas
    de alta densidade (celular, monitor Full HD) em vez de o navegador esticar uma imagem pequena."""
    W: int
    H: int
    k: float = 1

    def s(self, n) -> int:
        """Converte uma medida do desenho base para pixels reais."""
        return int(round(n * self.k))

    @property
    def retrato(self) -> bool:
        return self.H > self.W

    @property
    def margem(self) -> int:
        return self.s(28 if self.retrato else 40)


def _fonte(arquivo, tamanho):
    caminho = os.path.join(PASTA_ASSETS, arquivo)
    try:
        return pygame.font.Font(caminho, tamanho)
    except (FileNotFoundError, OSError):
        return pygame.font.Font(None, int(tamanho * 1.25))


def carregar_fontes(lay: Layout) -> dict:
    t = (96, 52, 38, 26, 21) if lay.retrato else (72, 44, 32, 22, 17)
    t = [lay.s(x) for x in t]
    forte, normal = "BricolageGrotesque-ExtraBold.ttf", "BricolageGrotesque-Regular.ttf"
    return {"grande": _fonte(forte, t[0]), "tit": _fonte(forte, t[1]), "perg": _fonte(forte, t[2]),
            "txt": _fonte(normal, t[3]), "peq": _fonte(normal, t[4])}


def imagem(nome):
    """Carrega uma imagem de assets/ (None se o arquivo não existir)."""
    caminho = os.path.join(PASTA_ASSETS, nome)
    if not os.path.exists(caminho):
        return None
    return pygame.image.load(caminho)


def mistura(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def criar_fundo(lay: Layout, cor=CLARO) -> pygame.Surface:
    fundo = pygame.Surface((lay.W, lay.H))
    fundo.fill(cor)
    return fundo


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


def _px(n, k):
    return max(1, int(round(n * k)))


def botao(sup, fonte, rect, texto, mouse, ativo=True, cor=TINTA, cor_texto=BRANCO, k=1):
    """Botão pílula de cor chapada. Ao passar o mouse, troca fundo e texto."""
    rect = pygame.Rect(rect)
    if ativo and rect.collidepoint(mouse):
        cor, cor_texto = cor_texto, cor
    if not ativo:       # sem camada transparente: só lava as cores na direção do fundo claro
        cor, cor_texto = mistura(cor, CLARO, 0.6), mistura(cor_texto, CLARO, 0.6)
    pygame.draw.rect(sup, cor, rect, border_radius=rect.h // 2)
    img = fonte.render(texto, True, cor_texto)
    sup.blit(img, img.get_rect(center=rect.center))


def campo(sup, fontes, rect, rotulo, valor, unidade, focado, k=1):
    rect = pygame.Rect(rect)
    sup.blit(fontes["peq"].render(rotulo, True, TINTA),
             (rect.x + _px(2, k), rect.y - fontes["peq"].get_linesize() - _px(4, k)))
    pygame.draw.rect(sup, BRANCO, rect, border_radius=_px(12, k))
    if focado:          # foco: faixa grossa embaixo, não uma borda fina
        pygame.draw.rect(sup, AGUA, (rect.x, rect.bottom - _px(4, k), rect.w, _px(4, k)))
    cursor = "|" if focado and (pygame.time.get_ticks() // 500) % 2 == 0 else ""
    img = fontes["txt"].render(valor + cursor, True, TINTA)
    sup.blit(img, img.get_rect(midleft=(rect.x + _px(14, k), rect.centery)))
    if unidade:
        u = fontes["peq"].render(unidade, True, TINTA)
        sup.blit(u, u.get_rect(midright=(rect.right - _px(12, k), rect.centery)))


def fade(sup, ms_desde_troca, cor=CLARO):
    """Cobre a tela logo após trocar de tela e vai sumindo em 200 ms."""
    alfa = int(255 * (1 - ms_desde_troca / 200))
    if alfa <= 0:
        return
    veu = pygame.Surface(sup.get_size())
    veu.fill(cor)
    veu.set_alpha(min(255, alfa))
    sup.blit(veu, (0, 0))
