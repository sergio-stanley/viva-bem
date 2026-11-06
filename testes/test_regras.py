import datetime
import pytest
from regras import (faixa, pontos_por_area, avaliar_area, classificar_imc, calcular_imc,
                    formatar_decimal, validar_dados, limpar_nome, titulo, data_retorno,
                    energia, aproximar, aceita_clique)
from conteudo import ORIENTACOES, FEEDBACK_ACOMP, DICAS

@pytest.mark.parametrize("pts,esperado", [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2)])
def test_faixa_quiz(pts, esperado):
    assert faixa(pts, 4) == esperado

def test_pontos_por_area_inclui_todas():
    assert pontos_por_area([("Sono", 2), ("Sono", 1), ("Água", 0)]) == \
        {"Sono": 3, "Água": 0, "Exercício": 0, "Alimentação": 0}

def test_avaliar_area():
    assert avaliar_area("Sono", 4, "quiz") == (2, ORIENTACOES["Sono"][2])
    assert avaliar_area("Água", 2, "acomp") == (2, FEEDBACK_ACOMP[2])
    assert avaliar_area("Água", 0, "acomp") == (0, FEEDBACK_ACOMP[0] + " " + DICAS["Água"] + ".")

@pytest.mark.parametrize("imc,cls", [(18.4, "abaixo do peso"), (18.5, "peso adequado"),
    (24.9, "peso adequado"), (25.0, "sobrepeso"), (29.9, "sobrepeso"), (30.0, "obesidade")])
def test_imc_adulto(imc, cls):
    assert classificar_imc(imc, 30)[0] == cls

@pytest.mark.parametrize("imc,cls,nivel", [(21.9, "baixo peso", "atencao"),
    (22.0, "peso adequado", "ok"), (27.0, "peso adequado", "ok"), (27.1, "sobrepeso", "atencao")])
def test_imc_idoso_sisvan(imc, cls, nivel):
    c = classificar_imc(imc, 60)
    assert (c[0], c[2]) == (cls, nivel)

def test_imc_menor_sem_classificacao():
    cls, obs, nivel = classificar_imc(22.0, 17)
    assert cls == "" and nivel == "info" and "profissional" in obs

def test_calcular_imc():
    r = calcular_imc(70, 175, 25)
    assert round(r.valor, 1) == 22.9 and r.classificacao == "peso adequado" and r.nivel == "ok"

def test_formatar_decimal():
    assert formatar_decimal(22.43) == "22,4" and formatar_decimal(300.0) == "300,0"

def test_validar_ok_e_nome_opcional():
    assert validar_dados("", "23", "170", "65") is None
    assert validar_dados("Ana", "1", "100", "20") is None
    assert validar_dados("Ana", "120", "250", "300") is None

@pytest.mark.parametrize("idade,altura,peso,trecho", [
    ("", "170", "65", "idade"), ("0", "170", "65", "idade"), ("121", "170", "65", "idade"),
    ("23", "99", "65", "Altura"), ("23", "251", "65", "Altura"),
    ("23", "170", "19", "Peso"), ("23", "170", "301", "Peso")])
def test_validar_limites(idade, altura, peso, trecho):
    assert trecho in validar_dados("", idade, altura, peso)

@pytest.mark.parametrize("altura", ["1,70", "1.70", "-5", "abc"])
def test_validar_formatos_do_celular(altura):
    msg = validar_dados("", "23", altura, "65")
    assert msg == "Altura em centímetros, entre 100 e 250 (ex.: 170)"

def test_validar_aceita_espacos():
    assert validar_dados(" Ana ", " 23 ", "170 ", " 65") is None

def test_titulo():
    assert titulo("", "quiz") == "Seu resultado"
    assert titulo("   ", "acomp") == "Seu acompanhamento"
    assert titulo("Ana", "quiz") == "Resultado de Ana"
    assert titulo("W" * 30, "quiz") == "Resultado de " + "W" * 20

def test_data_retorno_virada_de_mes():
    assert data_retorno(datetime.date(2026, 11, 6)) == "08/11"
    assert data_retorno(datetime.date(2026, 11, 30)) == "02/12"

def test_energia():
    assert energia([]) == 0.5
    assert energia([("Sono", 2), ("Água", 2)]) == 1.0
    assert energia([("Sono", 0), ("Água", 0)]) == 0.0
    assert energia([("Sono", 2), ("Água", 1)]) == 0.75

def test_aproximar_chega_perto_em_400ms():
    v = 0.0
    for _ in range(24):          # 24 quadros de ~16,7 ms ≈ 400 ms
        v = aproximar(v, 1.0, 17)
    assert v > 0.95

def test_aceita_clique():
    assert not aceita_clique(399) and aceita_clique(400)


@pytest.mark.parametrize("idade", ["²", "١٢", "2³"])
def test_digitos_nao_ascii_nao_travam(idade):
    # "²".isdigit() é True mas int("²") dá erro — AltGr+2 no teclado ABNT2 digita "²"
    assert validar_dados("", idade, "170", "65") == "Informe sua idade (1 a 120 anos)"


def test_aceita_clique_ignora_toque_duplo():
    assert not aceita_clique(300) and aceita_clique(400)
