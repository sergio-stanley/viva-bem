# Viva Bem — quiz de hábitos saudáveis em Pygame, pronto para o pygbag (laço principal com async).
import asyncio
import sys

import pygame

import telas
from ui import Layout, carregar_fontes, criar_fundo

NO_NAVEGADOR = sys.platform == "emscripten"
if NO_NAVEGADOR:
    import platform     # no pygbag, dá acesso ao navegador (window, document)


def ajustar_proporcao():
    """O pygbag calcula o tamanho de exibição antes do set_mode; pede para recalcular (evita imagem esticada)."""
    if NO_NAVEGADOR:
        platform.window.window_resize()


async def main():
    pygame.init()
    lay = Layout(960, 600)
    sup = pygame.display.set_mode((lay.W, lay.H))
    pygame.display.set_caption("Viva Bem")
    relogio = pygame.time.Clock()
    fontes = carregar_fontes(lay)
    fundo = criar_fundo(lay)
    est = telas.Estado()
    quadro = 0

    while True:
        clique, teclas = None, []
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                clique = ev.pos
            elif ev.type == pygame.KEYDOWN:
                teclas.append(ev)
        ent = telas.Entrada(pygame.mouse.get_pos(), clique, teclas, pygame.time.get_ticks())
        telas.desenhar(sup, lay, fontes, fundo, est, ent)
        pygame.display.flip()
        quadro += 1
        if quadro in (2, 60):
            ajustar_proporcao()
        relogio.tick(60)
        await asyncio.sleep(0)   # obrigatório no pygbag: devolve o controle ao navegador


asyncio.run(main())
