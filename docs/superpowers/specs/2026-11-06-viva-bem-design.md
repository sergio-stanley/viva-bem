# Viva Bem — Design (quiz de hábitos saudáveis)

**Data:** 06/11/2026 · **Apresentação:** 16/11/2026
**Autor da parte:** responsável pelo quiz e pelo deploy (trabalho de extensão em grupo, ADS — Belém/PA)

## 1. Objetivo

Publicar o quiz "Viva Bem" (Python + Pygame, rodando no navegador via pygbag) num link da Vercel,
usável **igualmente no celular e no computador/projetor**, com identidade visual atraente.
Na apresentação, o público acessa pelo link/QR code.

**Critérios de sucesso**
- O link `*.vercel.app` abre o quiz no PC (Brave) e em celulares Android e iPhone.
- No celular, os dados são digitados com o **teclado do próprio celular** (numérico para idade/altura/peso).
- Atualizar o site exige só: editar, testar, rodar `publicar.ps1`.
- O grupo consegue trocar perguntas/orientações editando apenas `conteudo.py`.

**Fora do escopo:** guardar dados (decisão do grupo: dado de saúde/LGPD), contas de usuário,
IA externa, build automático na nuvem.

## 2. Funcionalidades (mantidas do main.py atual)

- Tela inicial com dois modos: **Primeira vez** (8 perguntas, 2 por área: Sono, Água, Exercício,
  Alimentação) e **Já fiz antes** (acompanhamento: 4 perguntas "seguiu a orientação?").
- Tela de dados: nome, idade, altura (cm), peso (kg). Nada é guardado.
- Resultado por área com cor vermelho/amarelo/verde + orientação; IMC; aviso de que não substitui
  profissional de saúde. Regras fixas no código (sem serviço externo).

**Mudanças de regra**
- **Nome passa a ser opcional.** Sem nome, o título vira "Seu resultado" / "Seu acompanhamento".
- **IMC para 60+:** classificar pelas faixas do SISVAN/Ministério da Saúde para idosos:
  `< 22` baixo peso · `22 a 27` adequado · `> 27` sobrepeso.
- **IMC para < 18:** mantém só o número + aviso (classificação depende das curvas da OMS).
- **IMC 18–59:** mantém as faixas atuais (18,5 / 25 / 30).
- **Lembrete de retorno** no resultado: "Volte dia DD/MM para o acompanhamento" (hoje + 2 dias,
  calculado na hora, nada guardado).
- **Mensagem de validação** na tela de dados explicando o limite que falta
  (idade 1–120, altura 100–250 cm, peso 20–300 kg).

## 3. Estrutura do repositório

```
Trabalho-IOT-hábitos saudáveis/      → repositório GitHub "viva-bem"
├── quiz/                 # SÓ o que vai empacotado no jogo (pygbag empacota a pasta inteira)
│   ├── main.py           # só o laço async (pygbag executa este arquivo)
│   ├── telas.py          # estado do quiz + desenho/entrada de cada tela
│   ├── conteudo.py       # PERGUNTAS, ORIENTACOES, DICAS, ACOMPANHAMENTO, textos (o grupo edita)
│   ├── regras.py         # lógica pura: IMC, faixas, pontuação, validação, data de retorno
│   ├── ui.py             # fundo, cards, botões, ícones, campos, animações, layout
│   ├── formulario_web.py # ponte com o navegador: formulário HTML no celular
│   ├── boneco.py         # desenho e animação do boneco de energia (só PC)
│   ├── assets/           # Nunito (Regular/Bold, licença OFL) + QR code (PNG)
│   └── build/web/        # GERADO pelo pygbag e versionado; é o que a Vercel publica
├── testes/               # pytest para regras.py (fora de quiz/, não vai no pacote)
├── docs/superpowers/specs/
├── publicar.ps1          # build + git add + commit + push
├── vercel.json           # sem build; outputDirectory = quiz/build/web
├── README.md             # como rodar, testar, publicar + checklist manual
└── .gitignore            # .superpowers/, quiz/build/web-cache/, __pycache__/
```

Dependências entre módulos: `main → telas`; `telas → ui, boneco, regras, conteudo, formulario_web`; `boneco → (pygame)`; `ui → (pygame)`;
`regras` e `conteudo` não importam pygame (testáveis isoladamente).

## 4. Publicação (GitHub + Vercel)

**Abordagem escolhida:** build local, `quiz/build/web` versionado no Git, Vercel apenas serve
arquivos estáticos (sem build na nuvem). Motivo: o que é testado em `localhost:8000` é exatamente
o que vai ao ar; evita configurar Python/pygbag na Vercel.

**Configuração única**
1. ✅ Identidade do Git corrigida para "Sergio Stanley" e `git init` feito (06/11).
2. Criar repositório `viva-bem` no site do GitHub, `git remote add origin` + `git push -u origin main`.
3. Vercel: Add New → Project → importar `viva-bem`. `vercel.json` define framework nenhum,
   sem comando de build e `outputDirectory: "quiz/build/web"`.
4. Obter o link `viva-bem.vercel.app` (ou similar) e gerar o QR code.

**Fluxo de atualização**
1. Editar código → 2. `py -m pygbag quiz` e testar em `localhost:8000` →
3. `.\publicar.ps1 "mensagem"` → 4. Vercel publica em ~1 min.

`publicar.ps1`: roda `py -m pygbag --build quiz`, para se o build falhar, depois
`git add -A`, `git commit -m <mensagem>`, `git push`. Se o Windows bloquear scripts, documentar
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` ou oferecer `publicar.bat`.

O site no AWS Amplify pode ser mantido ou removido; não interfere.

## 5. Plataforma e layout

**Detecção ao abrir** (no navegador, via `platform.window`):
- Tela de toque (`matchMedia("(pointer: coarse)")`) → **modo celular**: sempre **em pé, 540×1080** (proporção ~1:2 dos celulares atuais),
  mesmo se o aparelho estiver deitado (o pygbag apenas reduz a imagem).
- Caso contrário → **modo PC**: **deitado, 960×600**.
- Fora do navegador (`py main.py`) → modo PC.

As posições deixam de ser números fixos: `ui.py` expõe um objeto de layout com `W`, `H`, margens
e `retrato: bool`; cada tela calcula posições a partir dele.

**Telas**
- **Início:** logo "Viva Bem", botões "Primeira vez" e "Já fiz antes", aviso de saúde.
  No modo PC, painel com **QR code** do link do site (para o público escanear).
- **Dados (PC):** campos desenhados no Pygame (nome opcional; idade/altura/peso com unidade dentro
  do campo), digitação pelo teclado físico, Tab/Enter avançam, card lateral "Por que pedimos isso?",
  botão "Continuar ›" habilitado só com dados válidos, mensagem de validação em amarelo.
  **Sem teclado desenhado na tela.**
- **Dados (celular):** formulário HTML sobreposto ao canvas (ver seção 6).
- **Perguntas / acompanhamento:** no modo PC, painel à direita com o **boneco de energia** (seção 7.1); barra de progresso, área + "Pergunta X de N", texto, 3 botões
  grandes empilhados (bons para o dedo).
- **Resultado / feedback:** 4 cards de área (ícone, nome, rótulo da faixa, barra colorida,
  orientação) — **empilhados** no celular, **grade 2×2** no PC (com o boneco no estado final ao lado); card do IMC (só no resultado);
  lembrete de retorno; aviso de saúde; "Voltar ao início".

## 6. Entrada de dados no celular (formulário HTML)

Só no modo celular, ao entrar na tela de dados, `formulario_web.py` injeta via `platform.window`
um `<div>` fixo de tela cheia com o visual "Noite serena" (CSS), contendo:
- `<input>` nome (opcional, `maxlength=20`);
- `<input inputmode="numeric">` para idade, altura, peso (abre o teclado numérico do celular);
- texto "Seus dados não são guardados", mensagem de validação, botão "Continuar".

O Python verifica a cada quadro se o botão foi tocado; ao confirmar, lê os valores, valida com
`regras.py`, remove o `<div>` e segue para o quiz. Botão "Voltar" remove o formulário e retorna
ao início. O canvas Pygame continua rodando por trás (fundo).

**Risco e reserva:** é a parte mais incerta no pygbag. **Primeira tarefa da implementação:**
protótipo descartável testado no celular real (teclado abre? valores chegam ao Python?).
Se falhar → **reserva B:** `window.prompt()` por campo (teclado nativo garantido, visual do sistema).

## 7. Identidade visual "Noite serena"

- Paleta: fundo `#07161F` com degradê radial para `#0F4C5C` (superfície gerada uma vez);
  cards `#0E2633` com borda `#1F4A5E`; texto `#E8F6F4`; secundário `#8FB5BD`;
  destaque `#2DD4BF`; faixas: vermelho `#F87171`, amarelo `#FACC15`, verde `#4ADE80`.
- Fonte Nunito (Regular e Bold) em `quiz/assets/`; textos renderizados com cache.
- Ícones desenhados com `pygame.draw`: lua (Sono), gota (Água), halter (Exercício), maçã (Alimentação).
  Sem emoji (não é confiável no Pygame).
- Animações: fade de ~0,2 s ao trocar de tela; botões com estado hover/pressionado; barras do
  resultado enchem em ~0,6 s com brilho na cor da faixa.
- Tela a 60 fps; `await asyncio.sleep(0)` a cada quadro (exigência do pygbag).

### 7.1 Boneco de energia (sugestão do professor, adaptada) — só no modo PC

Um personagem desenhado com formas (`pygame.draw`) que reflete a **energia/disposição** da pessoa
conforme as respostas. **Não muda o peso/corpo** (decisão do grupo: evitar a mensagem
"gordo = ruim" e porque sono/água não alteram peso).

- **Energia** (0 a 1) = pontos acumulados ÷ pontos máximos das perguntas já respondidas;
  começa em 0,5 (neutro) antes da primeira resposta. Função pura em `regras.py` (testada).
- **Aparência interpolada continuamente pela energia:**
  - baixa (≈0): corpo cinza, inclinado/curvado, braços caídos, olhos semicerrados com olheiras,
    boca para baixo, "z z" flutuando;
  - média (≈0,5): corpo amarelo, em pé, braços ao lado, boca neutra;
  - alta (≈1): corpo verde, ereto, braços para cima, sorriso, brilho/aura e estrelinhas.
- **Animação:** a energia exibida se aproxima do valor-alvo em ~0,4 s após cada resposta;
  leve "respiração" (sobe e desce) contínua para parecer vivo.
- **Onde aparece:** painel direito nas telas de perguntas e acompanhamento, e ao lado dos cards
  no resultado/feedback (estado final). **Não aparece no modo celular.**

## 8. Conteúdo

`conteudo.py` concentra perguntas, opções/pontos, orientações por faixa, dicas e textos de aviso.
Quando o grupo escolher os artigos de referência, as orientações serão revisadas com base neles
(etapa separada, dias 14–15/11), sem mexer nos outros arquivos.

## 9. Testes

**Automáticos (pytest, `testes/`)** sobre `regras.py`:
- IMC adulto: 18,4 → abaixo; 18,5 e 24,9 → adequado; 25 → sobrepeso; 30 → obesidade.
- IMC 60+: 21,9 → baixo peso; 22 e 27 → adequado; 27,1 → sobrepeso.
- IMC < 18: sem classificação, com aviso.
- Faixa por área, mantendo a regra atual do main.py: 0–1 ponto → 0 (precisa melhorar), 2–3 → 1 (bom começo), 4 → 2 (ótimo); acompanhamento usa os pontos direto (0/1/2).
- Validação: limites de idade/altura/peso, campos vazios, nome opcional.
- Data de retorno (hoje + 2, formato DD/MM, virada de mês).
- Energia do boneco: sem respostas → 0,5; todas 2 pontos → 1; todas 0 → 0; mistas → proporção.

**Manuais (checklist no README):** `py main.py` no Windows; `localhost:8000` no Brave;
link da Vercel no PC; link da Vercel em Android e iPhone (via QR code) — fluxo completo nos
dois modos, teclado do celular abrindo, layout em pé.

## 10. Cronograma

| Dias | Entrega |
|---|---|
| 06–07/11 | Git/GitHub/Vercel com a versão atual no ar; protótipo do formulário no celular |
| 08–10/11 | Divisão em módulos, layouts PC/celular, formulário HTML, regras + testes |
| 11–13/11 | Identidade visual (fonte, ícones, animações, boneco de energia, QR code) |
| 14–15/11 | Orientações baseadas nos artigos, testes finais em celulares do grupo |
| 16/11 | Apresentação |
