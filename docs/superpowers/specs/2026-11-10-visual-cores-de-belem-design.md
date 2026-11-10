# Viva Bem — novo visual "Cores de Belém"

Data: 10/11/2026 · Apresentação: 16/11/2026 · Autor da decisão: Sergio Stanley

## Por que

O quiz funciona, mas o grupo e o professor disseram que ele tem "cara de inteligência artificial". O
visual atual ("Noite serena") usa exatamente o molde que quase todo site gerado por IA usa: fundo escuro
com degradê verde-água, brilho nas barras, cartões arredondados de borda fina todos iguais, ícones
dentro de bolinhas. O professor disse que o trabalho não pode ter essa cara. Também houve reclamação de
texto embaçado no celular; no celular do Sergio e na simulação já está nítido desde a escala 2×
(commit `74bec7c`), então o mais provável é que o grupo tenha visto a versão antiga guardada no
navegador.

Sucesso: a turma e o professor olham o quiz e não reconhecem um modelo pronto; ele parece feito para
Belém e para este tema. Nada que funciona hoje para de funcionar.

## O que muda (decidido com o Sergio)

Direção escolhida entre três rascunhos: **B · Cores de Belém**.

- **Cada área tem a sua cor e pinta a tela inteira** na tela de pergunta. Ao passar de área, a tela
  muda de cor — é assim que a pessoa sente o avanço.
  - Sono: azul-noite
  - Água: azul do rio
  - Exercício: verde das mangueiras
  - Alimentação: roxo do açaí
- **Letras grandes e fortes, uma família só** (no rascunho: Bricolage Grotesque, peso extra-negrito
  para títulos e regular para texto). Nome da área bem grande no topo da tela de pergunta.
- **Respostas em botões largos e totalmente arredondados (pílula)**, fáceis de tocar com o polegar.
- **Tela inicial:** as quatro cores lado a lado em faixas, como uma bandeira do Viva Bem, com o nome
  grande e os dois botões ("Primeira vez" e "Já fiz antes").
- **Resultado em duas telas (PC e celular):**
  1. **Áreas:** cada área vira uma faixa na própria cor, com a avaliação escrita grande ("Ótimo!",
     "Bom começo", "Precisa melhorar") e a orientação embaixo; um botão "Continuar" leva à segunda tela.
  2. **IMC e retorno:** IMC (no modo quiz), aviso de saúde, lembrete de retorno e botão "Voltar ao
     início". No modo acompanhamento, que não tem IMC, a segunda tela mostra só o lembrete, o aviso e o
     botão.
  Letra grande vale mais que caber tudo numa tela (o projetor é lido de longe); nada de rolagem.
- **Boneco de energia (só PC):** continua, redesenhado no estilo novo — formas chapadas, sem brilho
  nem aura com degradê. Continua mudando de disposição com as respostas (cansado → animado), nunca o
  corpo.
- **Sai tudo o que denuncia o molde de IA:** degradês, brilhos, sombras, bordas finas de 1 px,
  cartões repetidos em grade, ícones dentro de bolinhas, letras pequenas em maiúsculas espaçadas.

## O que não muda

- Python + Pygame rodando no navegador via pygbag (exigência do professor), publicado na Vercel.
- Perguntas, opções, pontuação, regras, IMC por idade (OMS / referência 60+ / aviso para menores de
  18), validações, os dois modos (quiz e acompanhamento), data de retorno, aviso de saúde, "nenhum dado
  é guardado".
- No celular: tela sempre em pé, formulário HTML que abre o teclado do aparelho, proteção contra toque
  duplo. No PC: teclado físico, Tab/Enter/Esc, botão Voltar, QR code na tela inicial.
- Escala 2× (nitidez) e todos os testes atuais que não dependem da aparência.
- Os textos de conteúdo (`quiz/conteudo.py`).

## Junto com o visual (decidido)

1. **O navegador sempre baixa a versão mais nova** do site depois de uma publicação (evitar o
   "ainda está embaçado" de quem guardou a versão antiga).
2. **Botões mais leves de desenhar:** hoje cada botão cria uma camada transparente nova a cada quadro;
   no tamanho 2× isso derrubou a fluidez de 60 para cerca de 36 quadros por segundo na simulação.
3. **Escala conforme a tela real do aparelho** (densidade × largura), com limite de 3×, em vez de 2×
   fixo — para celulares de tela mais densa (ex.: 1440 de largura) também ficarem nítidos. Fazer junto
   com o item 2, porque escala maior pesa mais.

**Ordem e corte (decisão do Claude):** primeiro o visual novo, depois "sempre a versão mais nova",
depois os botões leves; a escala conforme a tela vem por último e é a primeira coisa a cair se 13/11
apertar. Meta de fluidez: pelo menos 30 quadros por segundo no celular simulado; se a escala maior
derrubar abaixo disso, fica no 2× fixo.

4. **Slides da apresentação** (`apresentacao/`): trocar as imagens do visual antigo pelas telas novas
   e gerar de novo o .pptx e o .pdf, depois que o visual estiver pronto.

## Restrições

- Pronto e publicado até **13/11** para dar tempo de o Sergio testar em Android e iPhone antes do dia 16.
- Fontes só com licença livre (OFL), embutidas em `quiz/assets/` com o arquivo de licença. O Pygame
  precisa de arquivos .ttf estáticos (um por peso).
- Contraste legível: texto branco sobre as cores das áreas com contraste de pelo menos 4,5:1.
- O resultado precisa continuar mostrando a avaliação de cada área com as cores de semáforo
  (vermelho / amarelo / verde) — é um requisito original do trabalho. A cor da área identifica a área;
  o semáforo identifica a avaliação.
- O projetor da apresentação mostra o PC: a versão deitada (960×600 base) precisa ficar tão boa quanto a
  do celular.

## Deixado para quem construir

- Os tons exatos das quatro cores (respeitando o nome de cada uma e o contraste) e a cor neutra das
  telas sem área (dados, faixa do IMC).
- Se a fonte do rascunho não puder virar .ttf estático, escolher outra grotesca forte com licença OFL.
- Como o semáforo aparece na faixa de resultado (ex.: um selo sólido com a palavra), desde que não
  vire brilho, borda fina nem bolinha com ícone.
- Se os ícones das áreas continuam (sem a bolinha de fundo) ou saem.
- A composição exata de cada tela no PC e no celular, dentro das regras acima.
- Como mostrar a tela de dados (PC) e o formulário HTML do celular no estilo novo.
