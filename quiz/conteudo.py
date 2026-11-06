"""Textos do quiz Viva Bem: perguntas, orientações e dicas.

O grupo edita ESTE arquivo quando atualizar as orientações com base nos artigos de referência.
Não importa pygame (pode ser testado sozinho).
"""

AREAS = ["Sono", "Água", "Exercício", "Alimentação"]

# Cada opção: (texto, pontos). Pontos: 2 = ótimo, 1 = médio, 0 = precisa melhorar.
PERGUNTAS = [
    ("Sono", "Quantas horas você costuma dormir por noite?",
     [("7 a 9 horas", 2), ("5 a 6 horas", 1), ("Menos de 5 horas", 0)]),
    ("Sono", "Você dorme e acorda em horários parecidos todos os dias?",
     [("Quase sempre", 2), ("Às vezes", 1), ("Quase nunca", 0)]),
    ("Água", "Quanta água você bebe por dia?",
     [("Mais de 2 litros", 2), ("Entre 1 e 2 litros", 1), ("Menos de 1 litro", 0)]),
    ("Água", "Você toma água ao longo do dia, mesmo sem sentir sede?",
     [("Sim, sempre", 2), ("Às vezes", 1), ("Só quando tenho sede", 0)]),
    ("Exercício", "Quantos dias por semana você faz atividade física?",
     [("4 dias ou mais", 2), ("1 a 3 dias", 1), ("Nenhum", 0)]),
    ("Exercício", "Quanto tempo você passa sentado(a) por dia?",
     [("Menos de 4 horas", 2), ("De 4 a 8 horas", 1), ("Mais de 8 horas", 0)]),
    ("Alimentação", "Com que frequência você come frutas e verduras?",
     [("Todos os dias", 2), ("Algumas vezes por semana", 1), ("Raramente", 0)]),
    ("Alimentação", "Com que frequência você come fast food, doces ou refrigerante?",
     [("Raramente", 2), ("Algumas vezes por semana", 1), ("Quase todo dia", 0)]),
]

# Orientações por área e faixa (0 = precisa melhorar, 1 = bom começo, 2 = ótimo).
ORIENTACOES = {
    "Sono": [
        "Tente dormir de 7 a 9 horas e manter horários fixos. Evite telas 1 hora antes de deitar.",
        "Seu sono está razoável. Fixe o horário de dormir e acordar para ficar mais constante.",
        "Ótimo sono! Continue mantendo a rotina de horários."],
    "Água": [
        "Deixe uma garrafa de água por perto e beba aos poucos ao longo do dia.",
        "Bom começo. Aumente aos poucos e crie lembretes para beber água.",
        "Ótima hidratação! Continue assim."],
    "Exercício": [
        "Comece com caminhadas de 20 a 30 minutos, 3 vezes por semana, e levante a cada hora.",
        "Bom começo. Tente chegar a cerca de 150 minutos de atividade moderada por semana.",
        "Ótimo! Você já se movimenta bastante. Mantenha a regularidade."],
    "Alimentação": [
        "Inclua uma fruta ou verdura em cada refeição e reduza refrigerante e doces.",
        "Bom começo. Aumente as frutas e verduras e deixe os ultraprocessados para ocasiões.",
        "Ótima alimentação! Continue variando os alimentos."],
}

# Dicas curtas usadas no acompanhamento (quem já fez o quiz antes).
DICAS = {
    "Sono": "durma e acorde no mesmo horário",
    "Água": "deixe uma garrafa de água por perto",
    "Exercício": "faça uma caminhada curta hoje",
    "Alimentação": "coloque uma fruta ou verdura em cada refeição",
}
ACOMPANHAMENTO = [
    ("Sono", "Nos últimos 2 dias, você seguiu a orientação de SONO?"),
    ("Água", "Nos últimos 2 dias, você seguiu a orientação de ÁGUA?"),
    ("Exercício", "Nos últimos 2 dias, você seguiu a orientação de EXERCÍCIO?"),
    ("Alimentação", "Nos últimos 2 dias, você seguiu a orientação de ALIMENTAÇÃO?"),
]
OPCOES_ACOMP = [("Sim, segui", 2), ("Segui em parte", 1), ("Não consegui", 0)]
FEEDBACK_ACOMP = {
    2: "Parabéns, você manteve o cuidado! Continue assim.",
    1: "Bom progresso. Tente ser mais constante.",
    0: "Sem problema, recomece com um passo pequeno:",
}

AVISO_SAUDE = "Orientações gerais não substituem a avaliação de um profissional de saúde."

# Rótulo mostrado ao lado de cada área no resultado (índice = faixa 0, 1 ou 2).
ROTULO_FAIXA = ["Precisa melhorar", "Bom começo", "Ótimo!"]
