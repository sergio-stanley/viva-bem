"""Regras do quiz Viva Bem (lógica pura, sem pygame): pontuação, IMC, validação e datas."""
import datetime
import math
from typing import NamedTuple

from conteudo import AREAS, ORIENTACOES, FEEDBACK_ACOMP, DICAS

LIMITE_NOME = 20


def faixa(pontos: int, maximo: int) -> int:
    """0 = precisa melhorar, 1 = bom começo, 2 = ótimo."""
    if pontos <= maximo * 0.25:
        return 0
    return 2 if pontos == maximo else 1


def pontos_por_area(respostas: list) -> dict:
    total = {area: 0 for area in AREAS}
    for area, pontos in respostas:
        total[area] += pontos
    return total


def avaliar_area(area: str, pontos: int, modo: str) -> tuple:
    """Devolve (faixa 0–2, mensagem) para uma área. modo: "quiz" ou "acomp"."""
    if modo == "quiz":
        f = faixa(pontos, 4)
        return f, ORIENTACOES[area][f]
    msg = FEEDBACK_ACOMP[pontos]
    if pontos == 0:
        msg += " " + DICAS[area] + "."
    return pontos, msg


class Imc(NamedTuple):
    valor: float
    classificacao: str
    observacao: str
    nivel: str          # "ok" | "atencao" | "info"


_OBS_BAIXO = "Vale conversar com um profissional de saúde sobre alimentação."
_OBS_OK = "Continue com os bons hábitos."
_OBS_SOBRE = "Pequenas mudanças de hábito ajudam. Um profissional pode orientar."


def classificar_imc(imc: float, idade: int) -> tuple:
    """(classificação, observação, nível). Adultos: OMS; 60+: SISVAN; menores de 18: só aviso."""
    if idade < 18:
        return ("", "Para menores de 18 anos o IMC usa tabelas próprias. "
                    "Converse com um profissional de saúde.", "info")
    if idade >= 60:
        ref = " (Referência para 60 anos ou mais.)"
        if imc < 22:
            return "baixo peso", _OBS_BAIXO + ref, "atencao"
        if imc <= 27:
            return "peso adequado", _OBS_OK + ref, "ok"
        return "sobrepeso", _OBS_SOBRE + ref, "atencao"
    if imc < 18.5:
        return "abaixo do peso", _OBS_BAIXO, "atencao"
    if imc < 25:
        return "peso adequado", _OBS_OK, "ok"
    if imc < 30:
        return "sobrepeso", _OBS_SOBRE, "atencao"
    return "obesidade", "Procure um profissional de saúde para uma avaliação completa.", "atencao"


def calcular_imc(peso_kg: int, altura_cm: int, idade: int) -> Imc:
    valor = peso_kg / ((altura_cm / 100) ** 2)
    return Imc(valor, *classificar_imc(valor, idade))


def formatar_decimal(v: float) -> str:
    return f"{v:.1f}".replace(".", ",")


def _numero_entre(texto: str, minimo: int, maximo: int) -> bool:
    texto = texto.strip()
    # isascii: "²" e outros dígitos especiais passam em isdigit() mas quebram int()
    return texto.isascii() and texto.isdigit() and minimo <= int(texto) <= maximo


def validar_dados(nome: str, idade: str, altura: str, peso: str):
    """None se tudo certo; senão a primeira mensagem de erro (idade → altura → peso)."""
    if not _numero_entre(idade, 1, 120):
        return "Informe sua idade (1 a 120 anos)"
    if not _numero_entre(altura, 100, 250):
        return "Altura em centímetros, entre 100 e 250 (ex.: 170)"
    if not _numero_entre(peso, 20, 300):
        return "Peso em kg, entre 20 e 300"
    return None


def limpar_nome(nome: str) -> str:
    return nome.strip()[:LIMITE_NOME]


def titulo(nome: str, modo: str) -> str:
    nome = limpar_nome(nome)
    if modo == "quiz":
        return f"Resultado de {nome}" if nome else "Seu resultado"
    return f"Acompanhamento de {nome}" if nome else "Seu acompanhamento"


def data_retorno(hoje: datetime.date) -> str:
    return (hoje + datetime.timedelta(days=2)).strftime("%d/%m")


def energia(respostas: list) -> float:
    """0 a 1: pontos obtidos ÷ pontos possíveis das perguntas respondidas (0,5 se nenhuma)."""
    if not respostas:
        return 0.5
    return sum(p for _, p in respostas) / (2 * len(respostas))


def aproximar(atual: float, alvo: float, dt_ms: int, tau_ms: float = 130.0) -> float:
    """Aproxima suavemente `atual` de `alvo` (usado nas animações)."""
    return atual + (alvo - atual) * (1 - math.exp(-dt_ms / tau_ms))


def aceita_clique(ms_desde_troca: int) -> bool:
    """Ignora toques logo após trocar de tela: um toque/clique duplo (até ~300 ms) não pode
    responder a próxima pergunta nem apertar "Voltar ao início" no resultado."""
    return ms_desde_troca >= 400
