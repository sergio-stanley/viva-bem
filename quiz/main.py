# Quiz de hábitos saudáveis em Pygame, pronto para o pygbag (laço principal com async).
import asyncio
import pygame

W, H = 900, 700
BG = (7, 22, 31); CARD = (14, 38, 51); LINE = (31, 74, 94)
INK = (232, 246, 244); MUTE = (143, 181, 189)
ACC = (45, 212, 191); OK = (74, 222, 128); WARN = (250, 204, 21); BAD = (248, 113, 113)

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


def quebrar(texto, fonte, largura):
    """Quebra o texto em linhas que cabem na largura."""
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if fonte.size(teste)[0] <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def desenhar_texto(tela, texto, fonte, cor, x, y, largura, espaco=4):
    for linha in quebrar(texto, fonte, largura):
        tela.blit(fonte.render(linha, True, cor), (x, y))
        y += fonte.get_linesize() + espaco
    return y


def botao(tela, fonte, rect, texto, mouse, cor=None):
    sobre = rect.collidepoint(mouse)
    pygame.draw.rect(tela, (20, 58, 76) if sobre else CARD, rect, border_radius=12)
    pygame.draw.rect(tela, cor or (ACC if sobre else LINE), rect, 2, border_radius=12)
    img = fonte.render(texto, True, INK)
    tela.blit(img, img.get_rect(center=rect.center))


def faixa(pontos, maximo):
    return 0 if pontos <= maximo * 0.25 else (2 if pontos == maximo else 1)


def calcular_imc(peso_kg, altura_cm, idade_anos):
    """Retorna (imc, classificação, observação, cor). Só classifica adultos de 18 a 59 anos."""
    imc = peso_kg / ((altura_cm / 100) ** 2)
    if idade_anos < 18:
        return imc, "", "Para menores de 18 anos o IMC usa tabelas próprias. Converse com um profissional de saúde.", ACC
    if idade_anos >= 60:
        return imc, "", "Para pessoas com 60 anos ou mais a referência é diferente. Converse com um profissional de saúde.", ACC
    if imc < 18.5:
        return imc, "abaixo do peso", "Vale conversar com um profissional de saúde sobre alimentação.", WARN
    if imc < 25:
        return imc, "peso adequado", "Continue com os bons hábitos.", OK
    if imc < 30:
        return imc, "sobrepeso", "Pequenas mudanças de hábito ajudam. Um profissional pode orientar.", WARN
    return imc, "obesidade", "Procure um profissional de saúde para uma avaliação completa.", WARN


def cor_faixa(f):
    return (BAD, WARN, OK)[f]


async def main():
    pygame.init()
    tela = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Quiz de Hábitos Saudáveis")
    relogio = pygame.time.Clock()
    f_tit, f_perg = pygame.font.Font(None, 48), pygame.font.Font(None, 36)
    f_txt, f_peq = pygame.font.Font(None, 28), pygame.font.Font(None, 22)

    estado = "inicio"          # inicio | dados | quiz | resultado | acomp | feedback
    indice, respostas = 0, []  # respostas: lista de (area, pontos)
    nome, idade, altura, peso, campo, modo = "", "", "", "", 0, "quiz"   # dados da pessoa (não são guardados)

    while True:
        mouse = pygame.mouse.get_pos()
        clique = None
        teclas = []
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                clique = ev.pos
            if ev.type == pygame.KEYDOWN:
                teclas.append(ev)

        tela.fill(BG)
        pygame.draw.rect(tela, CARD, (30, 30, W - 60, H - 60), border_radius=18)
        pygame.draw.rect(tela, LINE, (30, 30, W - 60, H - 60), 2, border_radius=18)

        if estado == "inicio":
            tela.blit(f_tit.render("Quiz de Hábitos Saudáveis", True, ACC), (70, 80))
            y = desenhar_texto(tela, "Responda algumas perguntas sobre sono, água, exercício e "
                               "alimentação e receba orientações para melhorar sua rotina. "
                               "Refaça a cada 2 dias para acompanhar seu progresso.",
                               f_txt, MUTE, 70, 150, W - 140)
            b1 = pygame.Rect(70, 330, W - 140, 70)
            b2 = pygame.Rect(70, 430, W - 140, 70)
            botao(tela, f_perg, b1, "Primeira vez: começar o quiz", mouse)
            botao(tela, f_perg, b2, "Já fiz antes: acompanhamento", mouse)
            if clique and b1.collidepoint(clique):
                estado, modo, nome, idade, altura, peso, campo = "dados", "quiz", "", "", "", "", 0
            elif clique and b2.collidepoint(clique):
                estado, modo, nome, idade, altura, peso, campo = "dados", "acomp", "", "", "", "", 0

        elif estado == "dados":
            tela.blit(f_tit.render("Antes de começar", True, ACC), (70, 70))
            tela.blit(f_peq.render("Seus dados não são guardados: servem só para personalizar o resultado.", True, MUTE), (70, 120))
            caixas = [pygame.Rect(70, 200, W - 140, 60), pygame.Rect(70, 320, 180, 60),
                      pygame.Rect(290, 320, 180, 60), pygame.Rect(510, 320, 180, 60)]
            rotulos = ["Nome (pode ser só o primeiro)", "Idade (anos)", "Altura (cm)", "Peso (kg)"]
            valores = [nome, idade, altura, peso]
            for i, (cx, rot, val) in enumerate(zip(caixas, rotulos, valores)):
                tela.blit(f_peq.render(rot, True, MUTE), (cx.x, cx.y - 26))
                pygame.draw.rect(tela, BG, cx, border_radius=10)
                pygame.draw.rect(tela, ACC if campo == i else LINE, cx, 2, border_radius=10)
                cursor = "|" if campo == i and (pygame.time.get_ticks() // 500) % 2 == 0 else ""
                tela.blit(f_perg.render(val + cursor, True, INK), (cx.x + 14, cx.y + 16))
            valido = (bool(nome.strip()) and idade.isdigit() and 1 <= int(idade) <= 120
                      and altura.isdigit() and 100 <= int(altura) <= 250
                      and peso.isdigit() and 20 <= int(peso) <= 300)
            bc = pygame.Rect(70, 460, 260, 64)
            botao(tela, f_perg, bc, "Continuar", mouse, cor=ACC if valido else LINE)
            for ev in teclas:
                if ev.key == pygame.K_TAB:
                    campo = (campo + 1) % 4
                elif ev.key == pygame.K_BACKSPACE:
                    if campo == 0: nome = nome[:-1]
                    elif campo == 1: idade = idade[:-1]
                    elif campo == 2: altura = altura[:-1]
                    else: peso = peso[:-1]
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if campo < 3: campo += 1
                    elif valido: clique = bc.center
                elif ev.unicode and ev.unicode.isprintable():
                    if campo == 0 and len(nome) < 20:
                        nome += ev.unicode
                    elif campo == 1 and ev.unicode.isdigit() and len(idade) < 3:
                        idade += ev.unicode
                    elif campo == 2 and ev.unicode.isdigit() and len(altura) < 3:
                        altura += ev.unicode
                    elif campo == 3 and ev.unicode.isdigit() and len(peso) < 3:
                        peso += ev.unicode
            if clique:
                for i, cx in enumerate(caixas):
                    if cx.collidepoint(clique): campo = i
                if bc.collidepoint(clique) and valido:
                    estado, indice, respostas = modo, 0, []

        elif estado in ("quiz", "acomp"):
            lista = PERGUNTAS if estado == "quiz" else ACOMPANHAMENTO
            area, texto = lista[indice][0], lista[indice][1]
            opcoes = lista[indice][2] if estado == "quiz" else OPCOES_ACOMP
            pygame.draw.rect(tela, BG, (70, 70, W - 140, 12), border_radius=6)
            pygame.draw.rect(tela, ACC, (70, 70, int((W - 140) * indice / len(lista)), 12), border_radius=6)
            tela.blit(f_peq.render(f"{area.upper()}  |  Pergunta {indice + 1} de {len(lista)}", True, MUTE), (70, 100))
            desenhar_texto(tela, texto, f_perg, INK, 70, 150, W - 140)
            botoes = []
            for i, (t, p) in enumerate(opcoes):
                r = pygame.Rect(70, 290 + i * 100, W - 140, 80)
                botao(tela, f_perg, r, t, mouse)
                botoes.append((r, p))
            if clique:
                for r, p in botoes:
                    if r.collidepoint(clique):
                        respostas.append((area, p))
                        indice += 1
                        if indice >= len(lista):
                            estado = "resultado" if estado == "quiz" else "feedback"
                        break

        elif estado in ("resultado", "feedback"):
            titulo = "Resultado de " if estado == "resultado" else "Acompanhamento de "
            tela.blit(f_tit.render(titulo + nome.strip(), True, ACC), (70, 55))
            tela.blit(f_peq.render(f"{idade} anos", True, MUTE), (W - 150, 70))
            y = 110
            for area in AREAS:
                pts = sum(p for a, p in respostas if a == area)
                if estado == "resultado":
                    f = faixa(pts, 4)
                    msg = ORIENTACOES[area][f]
                else:
                    f = pts
                    msg = FEEDBACK_ACOMP[pts]
                    if pts == 0:
                        msg += " " + DICAS[area] + "."
                tela.blit(f_txt.render(area, True, cor_faixa(f)), (70, y))
                pygame.draw.rect(tela, BG, (230, y + 6, 200, 14), border_radius=7)
                pygame.draw.rect(tela, cor_faixa(f), (230, y + 6, 200 * (f + 1) // 3, 14), border_radius=7)
                desenhar_texto(tela, msg, f_peq, INK, 70, y + 34, W - 140, espaco=2)
                y += 104
            if estado == "resultado":
                imc, cls, obs, cor = calcular_imc(int(peso), int(altura), int(idade))
                tela.blit(f_txt.render(f"IMC: {imc:.1f}" + (f" ({cls})" if cls else ""), True, cor), (70, y))
                desenhar_texto(tela, obs, f_peq, INK, 70, y + 30, W - 140, espaco=2)
            desenhar_texto(tela, "O IMC é só uma referência. Orientações gerais não substituem a avaliação de um profissional de saúde.",
                           f_peq, MUTE, 70, 590, W - 140)
            b = pygame.Rect(W - 330, 615, 260, 44)
            botao(tela, f_txt, b, "Voltar ao início", mouse)
            if clique and b.collidepoint(clique):
                estado = "inicio"

        pygame.display.flip()
        relogio.tick(60)
        await asyncio.sleep(0)   # obrigatório no pygbag: devolve o controle ao navegador


asyncio.run(main())
