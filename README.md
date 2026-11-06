# Viva Bem — quiz de hábitos saudáveis

Quiz sobre **sono, água, exercício e alimentação**, feito em **Python + Pygame** e rodando no
navegador com **pygbag**. Trabalho de extensão do curso de Análise e Desenvolvimento de Sistemas
(Belém/PA).

- Dois modos: **Primeira vez** (quiz completo) e **Já fiz antes** (acompanhamento a cada 2 dias).
- Resultado por área (vermelho/amarelo/verde) com orientações, e cálculo do IMC.
- **Nenhum dado é guardado.** As orientações são gerais e **não substituem a avaliação de um
  profissional de saúde**.

**Link do site:** <https://viva-bem-seven.vercel.app/>
**Repositório:** <https://github.com/sergio-stanley/viva-bem>

## Estrutura

```
quiz/            código do jogo (só isto vai empacotado pelo pygbag)
  main.py
  build/web/     gerado pelo pygbag — é o que a Vercel publica
publicar.ps1     build + commit + push
vercel.json      diz à Vercel para servir quiz/build/web sem build
docs/            design e plano de implementação
```

> Não coloque na pasta `quiz/` nada que não seja do jogo: o pygbag empacota a pasta inteira e
> tudo ali fica disponível para download no site.

## Como rodar

| O quê | Comando (no terminal, na pasta do projeto) |
|---|---|
| Rodar no PC | `py quiz/main.py` |
| Testar no navegador | `py -m pygbag quiz` e abrir <http://localhost:8000> (Ctrl+C para parar) |
| Publicar no site | `.\publicar.ps1 "texto do que mudou"` |

O `publicar.ps1` gera o build, faz o commit e envia ao GitHub. Cerca de 1 minuto depois a Vercel
publica a versão nova sozinha.

### Se o PowerShell bloquear o script

Se aparecer "a execução de scripts foi desabilitada neste sistema", rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Isso libera scripts locais só para o seu usuário.
