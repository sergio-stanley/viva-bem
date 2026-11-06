# Publica o Viva Bem: gera o build do pygbag e envia para o GitHub (a Vercel atualiza sozinha).
# Uso:  .\publicar.ps1 "texto do que mudou"
param(
    [Parameter(Mandatory = $true)]
    [string]$Mensagem
)

Set-Location -Path $PSScriptRoot

Write-Host "1/3  Gerando o build do quiz (py -m pygbag --build quiz)..." -ForegroundColor Cyan
py -m pygbag --build quiz
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: o build falhou. Nada foi enviado. Leia a mensagem acima." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "quiz/build/web/index.html")) {
    Write-Host "ERRO: nao encontrei quiz/build/web/index.html depois do build." -ForegroundColor Red
    exit 1
}

Write-Host "2/3  Salvando as mudancas no Git (commit)..." -ForegroundColor Cyan
git add -A
$pendente = git status --porcelain
if (-not $pendente) {
    Write-Host "Nenhuma mudanca para publicar. Tudo ja esta no ar." -ForegroundColor Yellow
    exit 0
}
git commit -m $Mensagem
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: o commit falhou." -ForegroundColor Red
    exit 1
}

Write-Host "3/3  Enviando para o GitHub (push)..." -ForegroundColor Cyan
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: o envio falhou. Verifique a internet ou o login do GitHub e rode 'git push' de novo." -ForegroundColor Red
    exit 1
}

Write-Host "Pronto! Em cerca de 1 minuto a Vercel publica a nova versao." -ForegroundColor Green
