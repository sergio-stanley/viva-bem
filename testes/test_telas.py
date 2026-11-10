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
    tocar(est, "continuar")
    assert est.tela == "retorno"
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
    passo(est, clique=rects["opcao0"].center, agora=T + 400)
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
        assert "continuar" in passo(est)
        est.tela = "retorno"
        assert "voltar" in passo(est)


def test_resultado_sem_nome():
    est = Estado(tela="resultado", idade="30", altura="170", peso="65",
                 respostas=[("Sono", 1)] * 2 + [("Água", 1)] * 2 + [("Exercício", 1)] * 2 + [("Alimentação", 1)] * 2)
    passo(est)


def test_todas_as_telas_desenham_sem_erro():
    for tela in ("inicio", "dados", "quiz", "acomp", "retorno"):
        passo(Estado(tela=tela, idade="30", altura="170", peso="65"))


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


# ------------------------------------------------------------ modo celular (Task 6)
class FormularioFalso:
    """Mesma interface do FormularioWeb, sem navegador."""

    def __init__(self):
        self.chamadas = []
        self.proxima_acao = None
        self.dados = ("", "", "", "")

    def abrir(self, erro=""):
        self.chamadas.append("abrir")

    def acao(self):
        a, self.proxima_acao = self.proxima_acao, None
        return a

    def valores(self):
        return self.dados

    def mostrar_erro(self, msg):
        self.chamadas.append(("erro", msg))

    def fechar(self):
        self.chamadas.append("fechar")


LAY_R = Layout(540, 1080)
F_R = carregar_fontes(LAY_R)
FUNDO_R = criar_fundo(LAY_R)
SUP_R = pygame.Surface((540, 1080))
RET = dict(lay=LAY_R, fontes=F_R, fundo=FUNDO_R, sup=SUP_R)


def test_dados_com_formulario_abre_uma_vez_e_continua():
    form = FormularioFalso()
    est = Estado()
    tocar(est, "primeira_vez", form=form, **RET)
    for _ in range(3):
        passo(est, form=form, **RET)
    assert form.chamadas.count("abrir") == 1
    form.dados = (" Ana ", "23", "170", "65")
    form.proxima_acao = "ok"
    passo(est, form=form, **RET)
    assert "fechar" in form.chamadas
    assert est.tela == "quiz" and (est.nome, est.idade, est.altura, est.peso) == ("Ana", "23", "170", "65")


def test_dados_com_formulario_invalido_mostra_erro():
    form = FormularioFalso()
    est = Estado()
    tocar(est, "primeira_vez", form=form, **RET)
    form.dados = ("", "23", "1,70", "65")
    form.proxima_acao = "ok"
    passo(est, form=form, **RET)
    assert ("erro", "Altura em centímetros, entre 100 e 250 (ex.: 170)") in form.chamadas
    assert est.tela == "dados" and "fechar" not in form.chamadas


def test_dados_com_formulario_voltar():
    form = FormularioFalso()
    est = Estado()
    tocar(est, "primeira_vez", form=form, **RET)
    passo(est, form=form, **RET)
    form.proxima_acao = "voltar"
    passo(est, form=form, **RET)
    assert est.tela == "inicio" and "fechar" in form.chamadas


def test_formulario_reabre_ao_entrar_de_novo():
    form = FormularioFalso()
    est = Estado()
    tocar(est, "primeira_vez", form=form, **RET)
    passo(est, form=form, **RET)
    form.proxima_acao = "voltar"
    passo(est, form=form, **RET)
    tocar(est, "ja_fiz", form=form, **RET)
    passo(est, form=form, **RET)
    assert form.chamadas.count("abrir") == 2


def test_layout_retrato_sem_erro():
    A = ["Sono", "Água", "Exercício", "Alimentação"]
    for tela in ("inicio", "dados", "quiz", "acomp"):
        passo(Estado(tela=tela), **RET)
    for tela, n in (("resultado", 8), ("feedback", 4)):
        est = Estado(tela=tela, modo="quiz" if n == 8 else "acomp", nome="W" * 20,
                     idade="65", altura="100", peso="300", respostas=[(A[i % 4], 0) for i in range(n)])
        assert passo(est, **RET)["continuar"].bottom <= 1080
        est.tela = "retorno"
        assert passo(est, **RET)["voltar"].bottom <= 1080


def test_fluxo_quiz_completo_retrato():
    est = Estado()
    tocar(est, "primeira_vez", **RET)
    preencher(est)
    tocar(est, "continuar", **RET)
    for _ in range(8):
        tocar(est, "opcao2", **RET)
    assert est.tela == "resultado"


def _pior_caso(tela):
    A = ["Sono", "Água", "Exercício", "Alimentação"]
    n = 8 if tela == "resultado" else 4
    return Estado(tela=tela, modo="quiz" if n == 8 else "acomp", nome="Wanderleia Cristina",
                  idade="65", altura="160", peso="80", respostas=[(A[i % 4], 0) for i in range(n)])


@pytest.mark.parametrize("tela", ["resultado", "feedback"])
@pytest.mark.parametrize("retrato", [False, True])
def test_resultado_pior_caso_nao_sobrepoe_rodape(tela, retrato):
    kw = RET if retrato else {}
    est = _pior_caso(tela)
    est.tela = "retorno"
    rects = passo(est, **kw)
    altura = (kw.get("lay") or LAY).H
    assert rects["conteudo"].bottom <= rects["rodape"].top
    assert rects["rodape"].bottom <= altura


# ------------------------------------------------------------ boneco de energia (Task 7)
def test_energia_do_boneco_sobe_com_respostas_boas():
    est = Estado()
    tocar(est, "primeira_vez")
    preencher(est)
    tocar(est, "continuar")
    assert est.energia_vista == pytest.approx(0.5)
    for _ in range(3):
        tocar(est, "opcao0")          # 2 pontos cada
    for _ in range(30):
        passo(est)
    assert est.energia_vista > 0.9


def test_energia_do_boneco_cai_com_respostas_ruins_e_volta_ao_neutro_no_inicio():
    est = Estado()
    tocar(est, "ja_fiz")
    preencher(est)
    tocar(est, "continuar")
    for _ in range(4):
        tocar(est, "opcao2")          # 0 pontos cada
    for _ in range(30):
        passo(est)
    assert est.tela == "feedback" and est.energia_vista < 0.1
    tocar(est, "continuar")
    tocar(est, "voltar")
    assert est.energia_vista == pytest.approx(0.5)


def test_resultado_pc_reserva_coluna_do_boneco():
    rects = passo(_pior_caso("resultado"))
    assert rects["conteudo"].right <= LAY.W - LAY.margem - 190


# ------------------------------------------------------------ QR code (Task 8)
def test_inicio_pc_mostra_qr_quando_existe(tmp_path, monkeypatch):
    import ui
    qr = pygame.Surface((50, 50))
    qr.fill((255, 255, 255))
    pygame.image.save(qr, str(tmp_path / "qrcode.png"))
    monkeypatch.setattr(ui, "PASTA_ASSETS", str(tmp_path))
    rects = passo(Estado())
    assert "qr" in rects and LAY.W // 2 < rects["qr"].centerx < LAY.W


def test_inicio_pc_sem_arquivo_de_qr_nao_quebra(tmp_path, monkeypatch):
    import ui
    monkeypatch.setattr(ui, "PASTA_ASSETS", str(tmp_path))
    rects = passo(Estado())
    assert "qr" not in rects and "primeira_vez" in rects


def test_inicio_celular_nao_mostra_qr():
    assert "qr" not in passo(Estado(), **RET)


# ------------------------------------------------------------ correções da revisão final
def test_tecla_sobrescrito_e_ignorada():
    est = Estado()
    tocar(est, "primeira_vez")
    est.campo = 1
    passo(est, teclas=[tecla("²"), tecla("2")])
    assert est.idade == "2"


def _responder_tudo(est, kw):
    while est.tela in ("quiz", "acomp"):
        tocar(est, "opcao2", **kw)


@pytest.mark.parametrize("retrato", [False, True])
def test_toque_duplo_na_ultima_resposta_nao_apaga_resultado(retrato):
    kw = RET if retrato else {}
    est = Estado()
    tocar(est, "primeira_vez", **kw)
    preencher(est)
    tocar(est, "continuar", **kw)
    for _ in range(7):
        tocar(est, "opcao2", **kw)
    rects = passo(est, **kw)
    T = Relogio.t + 1000
    passo(est, clique=rects["opcao2"].center, agora=T, **kw)
    assert est.tela == "resultado"
    passo(est, clique=rects["opcao2"].center, agora=T + 200, **kw)     # segundo toque do "toque duplo"
    assert est.tela == "resultado"


def test_clique_duplo_em_continuar_nao_responde_a_pergunta_1():
    est = Estado()
    tocar(est, "primeira_vez")
    preencher(est)
    rects = passo(est)
    T = Relogio.t + 1000
    passo(est, clique=rects["continuar"].center, agora=T)
    passo(est, clique=rects["continuar"].center, agora=T + 250)
    assert est.tela == "quiz" and est.indice == 0


def test_dados_pc_tem_voltar():
    est = Estado()
    tocar(est, "primeira_vez")
    tocar(est, "voltar")
    assert est.tela == "inicio"


def test_dados_pc_esc_volta_ao_inicio():
    est = Estado()
    tocar(est, "ja_fiz")
    passo(est, teclas=[tecla("\x1b", pygame.K_ESCAPE)])
    assert est.tela == "inicio"


# ------------------------------------------------------------ escala 2x (nitidez em telas de alta densidade)
LAY_2 = Layout(1920, 1200, 2)
PC2 = dict(lay=LAY_2, fontes=carregar_fontes(LAY_2), fundo=criar_fundo(LAY_2), sup=pygame.Surface((1920, 1200)))
LAY_R2 = Layout(1080, 2160, 2)
RET2 = dict(lay=LAY_R2, fontes=carregar_fontes(LAY_R2), fundo=criar_fundo(LAY_R2), sup=pygame.Surface((1080, 2160)))


def _estados_para_comparar():
    A = ["Sono", "Água", "Exercício", "Alimentação"]
    resp = [(A[i % 4], i % 3) for i in range(8)]
    return [Estado(), Estado(tela="dados", idade="23", altura="170", peso="65"),
            Estado(tela="quiz", indice=3, respostas=resp[:3]), Estado(tela="acomp", indice=1),
            Estado(tela="resultado", nome="Ana", idade="23", altura="165", peso="60", respostas=resp),
            Estado(tela="feedback", modo="acomp", idade="23", altura="165", peso="60", respostas=resp[:4]),
            Estado(tela="retorno", nome="Ana", idade="23", altura="165", peso="60", respostas=resp),
            Estado(tela="retorno", modo="acomp", idade="23", altura="165", peso="60", respostas=resp[:4])]


@pytest.mark.parametrize("retrato", [False, True])
def test_escala_2x_desenha_a_mesma_tela_no_dobro_do_tamanho(retrato):
    """Com escala 2, cada botão/área fica no mesmo lugar, só que com o dobro de pixels (mais nítido)."""
    kw1, kw2 = (RET, RET2) if retrato else ({}, PC2)
    for est in _estados_para_comparar():
        r1 = passo(Estado(**{k: getattr(est, k) for k in ("tela", "modo", "indice", "nome", "idade", "altura", "peso")},
                          respostas=list(est.respostas)), **kw1)
        r2 = passo(est, **kw2)
        assert r1.keys() == r2.keys(), est.tela
        for nome in r1:
            a, b = r1[nome], r2[nome]
            for v1, v2 in ((a.x, b.x), (a.y, b.y), (a.w, b.w), (a.h, b.h)):
                assert abs(2 * v1 - v2) <= 12, (est.tela, nome, a, b)


@pytest.mark.parametrize("tela", ["resultado", "feedback"])
@pytest.mark.parametrize("retrato", [False, True])
def test_escala_2x_pior_caso_nao_sobrepoe_rodape(tela, retrato):
    kw = RET2 if retrato else PC2
    est = _pior_caso(tela)
    est.tela = "retorno"
    rects = passo(est, **kw)
    assert rects["conteudo"].bottom <= rects["rodape"].top
    assert rects["rodape"].bottom <= kw["lay"].H


def test_escala_2x_fluxo_completo_no_celular():
    est = Estado()
    tocar(est, "primeira_vez", **RET2)
    preencher(est)
    tocar(est, "continuar", **RET2)
    for _ in range(8):
        tocar(est, "opcao1", **RET2)
    assert est.tela == "resultado"


def test_escala_2x_qr_fica_maior_e_nitido(tmp_path, monkeypatch):
    import ui
    qr = pygame.Surface((50, 50))
    qr.fill((255, 255, 255))
    qr.fill((0, 0, 0), pygame.Rect(0, 0, 25, 50))
    pygame.image.save(qr, str(tmp_path / "qrcode.png"))
    monkeypatch.setattr(ui, "PASTA_ASSETS", str(tmp_path))
    r1 = passo(Estado())["qr"]
    est = Estado()
    r2 = passo(est, **PC2)["qr"]
    assert r2.w == 2 * r1.w
    cores = {tuple(PC2["sup"].get_at((x, r2.centery)))[:3] for x in range(r2.x, r2.right)}
    assert cores <= {(0, 0, 0), (255, 255, 255)}      # ampliado sem suavizar: só preto e branco


# ------------------------------------------------------------ visual Cores de Belém: resultado em duas telas
_KW = {"PC": {}, "RET": RET, "PC2": PC2, "RET2": RET2}


def test_resultado_continua_para_retorno_e_volta_ao_inicio():
    est = _pior_caso("resultado")
    tocar(est, "continuar")
    assert est.tela == "retorno" and len(est.respostas) == 8
    tocar(est, "voltar")
    assert est.tela == "inicio"


def test_toque_duplo_em_continuar_nao_pula_o_retorno():
    est = _pior_caso("resultado")
    rects = passo(est)
    T = Relogio.t + 1000
    passo(est, clique=rects["continuar"].center, agora=T)
    passo(est, clique=rects["continuar"].center, agora=T + 150)
    assert est.tela == "retorno"


@pytest.mark.parametrize("modo,tem_imc", [("quiz", True), ("acomp", False)])
def test_retorno_so_mostra_imc_no_quiz(modo, tem_imc):
    est = _pior_caso("resultado" if modo == "quiz" else "feedback")
    est.tela = "retorno"
    assert ("imc" in passo(est)) is tem_imc


@pytest.mark.parametrize("kw", ["PC", "RET", "PC2", "RET2"])
@pytest.mark.parametrize("tela", ["resultado", "feedback"])
def test_faixas_cabem_acima_do_continuar(kw, tela):
    r = passo(_pior_caso(tela), **_KW[kw])      # faixa 0 = orientações mais longas
    assert r["conteudo"].bottom <= r["continuar"].top
    assert r["continuar"].bottom <= (_KW[kw].get("lay") or LAY).H


@pytest.mark.parametrize("kw", ["PC", "RET"])
def test_nome_de_20_letras_quebra_em_ate_2_linhas(kw):
    est = _pior_caso("resultado")
    est.nome = "W" * 20
    r = passo(est, **_KW[kw])
    f = _KW[kw].get("fontes") or F
    assert r["titulo"].h <= 2 * f["tit"].get_linesize()
    assert r["titulo"].bottom <= r["conteudo"].top


@pytest.mark.parametrize("kw", ["PC", "RET"])
@pytest.mark.parametrize("lista", ["quiz", "acomp"])
def test_pergunta_mais_longa_cabe_acima_das_respostas(kw, lista):
    from conteudo import PERGUNTAS, ACOMPANHAMENTO
    perguntas = PERGUNTAS if lista == "quiz" else ACOMPANHAMENTO
    i = max(range(len(perguntas)), key=lambda j: len(perguntas[j][1]))
    r = passo(Estado(tela=lista, indice=i), **_KW[kw])
    assert r["texto"].bottom <= r["opcao0"].top


@pytest.mark.parametrize("kw", ["PC", "RET"])
def test_pergunta_pinta_a_tela_com_a_cor_da_area(kw):
    from ui import COR_AREA
    sup = (_KW[kw].get("sup") or SUP)
    for i, area in ((0, "Sono"), (2, "Água"), (4, "Exercício"), (6, "Alimentação")):
        passo(Estado(tela="quiz", indice=i, ms_troca=-10_000), **_KW[kw])
        assert sup.get_at((2, sup.get_height() // 2))[:3] == COR_AREA[area]
