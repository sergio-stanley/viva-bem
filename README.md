# Viva Bem — quiz de hábitos saudáveis

Quiz sobre **sono, água, exercício e alimentação**, feito em **Python + Pygame** e rodando no
navegador com **pygbag**. Trabalho de extensão do curso de Análise e Desenvolvimento de Sistemas
(Belém/PA).

- Dois modos: **Primeira vez** (8 perguntas) e **Já fiz antes** (acompanhamento a cada 2 dias).
- Resultado por área (vermelho/amarelo/verde) com orientações, IMC e lembrete de retorno.
- **PC/projetor:** tela deitada, teclado físico, boneco de energia e QR code do site.
- **Celular:** tela em pé e formulário com o **teclado do próprio celular**.
- **Nenhum dado é guardado.** As orientações são gerais e **não substituem a avaliação de um
  profissional de saúde**.

**Link do site:** <https://viva-bem-seven.vercel.app/>
**Repositório:** <https://github.com/sergio-stanley/viva-bem>

## Estrutura

```
quiz/                  código do jogo (só isto vai empacotado pelo pygbag)
  main.py              laço principal (async, exigido pelo pygbag)
  telas.py             estado do quiz e cada tela (início, dados, perguntas, resultado)
  conteudo.py          perguntas, orientações e dicas  ← o grupo edita aqui
  regras.py            IMC, pontuação, validação, datas (sem pygame)
  ui.py                visual "Noite serena": fundo, fontes, cards, botões, ícones
  boneco.py            boneco de energia (só no PC)
  formulario_web.py    formulário HTML no celular (abre o teclado do aparelho)
  assets/              fonte Nunito (licença OFL) e qrcode.png
  build/web/           gerado pelo pygbag — é o que a Vercel publica
testes/                testes automáticos (pytest)
ferramentas/gerar_qr.py  gera o QR code do site
publicar.ps1           build + commit + push
vercel.json            diz à Vercel para servir quiz/build/web sem build
docs/                  design, plano e notas
```

> Não coloque na pasta `quiz/` nada que não seja do jogo: o pygbag empacota a pasta inteira e
> tudo ali fica disponível para download no site.

## Como rodar

| O quê | Comando (no terminal, na pasta do projeto) |
|---|---|
| Rodar no PC | `py quiz/main.py` |
| Testes automáticos | `py -m pytest -q` (instale uma vez: `py -m pip install pytest`) |
| Testar no navegador | `py -m pygbag quiz` e abrir <http://localhost:8000> (Ctrl+C para parar) |
| Publicar no site | `.\publicar.ps1 "texto do que mudou"` |
| Refazer o QR code | `py ferramentas/gerar_qr.py https://viva-bem-seven.vercel.app` (instale uma vez: `py -m pip install "qrcode[pil]"`) |

O `publicar.ps1` gera o build, faz o commit e envia ao GitHub. Cerca de 1 minuto depois a Vercel
publica a versão nova sozinha.

### Se o PowerShell bloquear o script

Se aparecer "a execução de scripts foi desabilitada neste sistema", rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Isso libera scripts locais só para o seu usuário.

## Mudar perguntas e orientações

Edite só `quiz/conteudo.py`, rode `py -m pytest -q` (os testes conferem se nada quebrou) e publique.
Cada pergunta tem 3 opções com pontos 2 (ótimo), 1 (médio) e 0 (precisa melhorar); cada área tem
2 perguntas. As orientações têm 3 textos por área: precisa melhorar / bom começo / ótimo.

## Checklist antes da apresentação

No celular, a primeira abertura pode levar **até 1 minuto** (o navegador baixa o Python, ~22 MB).
Peça para a turma abrir o link uns minutos antes.

- [ ] `py -m pytest -q` passa
- [ ] `py quiz/main.py` no Windows: fluxo completo nos dois modos
- [ ] `localhost:8000` no Brave: fluxo completo, imagem sem distorção
- [ ] Link da Vercel no PC: QR code aparece na tela inicial, boneco reage às respostas
- [ ] Link da Vercel no **Android** (pelo QR code): tela em pé, teclado numérico em idade/altura/peso
- [ ] Link da Vercel no **iPhone** (pelo QR code): idem
- [ ] No celular: "1,70" na altura mostra a mensagem amarela; "Voltar" e entrar de novo não duplica o formulário
- [ ] Aviso de saúde visível no início e no resultado
