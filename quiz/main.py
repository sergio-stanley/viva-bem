# Viva Bem — quiz de hábitos saudáveis em Pygame, pronto para o pygbag (laço principal com async).
import asyncio
import sys

import pygame

import telas
from formulario_web import FormularioWeb, eh_toque
from ui import Layout, carregar_fontes, criar_fundo

NO_NAVEGADOR = sys.platform == "emscripten"
if NO_NAVEGADOR:
    import platform     # no pygbag, dá acesso ao navegador (window, document)

TAMANHO_PC = (960, 600)          # deitado: computador / projetor
TAMANHO_CELULAR = (540, 1080)    # em pé: celular (sempre, mesmo se girar)


def ajustar_proporcao():
    """O pygbag calcula o tamanho de exibição antes do set_mode; pede para recalcular (evita imagem esticada)."""
    if NO_NAVEGADOR:
        platform.document.body.style.background = "#07161f"   # faixas ao redor do jogo na cor do tema
        platform.window.window_resize()


async def main():
    pygame.init()
    celular = eh_toque()
    lay = Layout(*(TAMANHO_CELULAR if celular else TAMANHO_PC))
    form = FormularioWeb() if celular else None
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
        # no celular não existe "passar o mouse": sem isso o último toque deixa um botão destacado
        mouse = (-1, -1) if celular else pygame.mouse.get_pos()
        ent = telas.Entrada(mouse, clique, teclas, pygame.time.get_ticks())
        telas.desenhar(sup, lay, fontes, fundo, est, ent, form)
        pygame.display.flip()
        quadro += 1
        if quadro in (2, 60):
            ajustar_proporcao()
        relogio.tick(60)
        await asyncio.sleep(0)   # obrigatório no pygbag: devolve o controle ao navegador


asyncio.run(main())
