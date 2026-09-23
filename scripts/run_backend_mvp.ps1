param(
    [string]$HostAddress = $(if ($env:ARGUS_BACKEND_HOST) { $env:ARGUS_BACKEND_HOST } else { "127.0.0.1" }),
    [int]$Port = $(if ($env:ARGUS_BACKEND_PORT) { [int]$env:ARGUS_BACKEND_PORT } else { 8000 }),
    [switch]$SkipTests,
    [switch]$SkipDependencyInstall,
    [switch]$EnableTailscaleServe,
    [int]$TailscaleHttpsPort = 443,
    [switch]$Detached
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Get-RepoRoot {
    $scriptPath = Split-Path -Parent $PSCommandPath
    return (Resolve-Path (Join-Path $scriptPath "..")).Path
}

function Invoke-Native {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Comando falhou com exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

function Get-Python {
    param([string]$RepoRoot)

    $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        return $venvPython
    }

    $codexPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $codexPython) {
        Write-Step "Criando .venv local com Python 3.12 do Codex"
        & $codexPython -m venv (Join-Path $RepoRoot ".venv")
        return $venvPython
    }

    $pathPython = (Get-Command python -ErrorAction SilentlyContinue)
    if ($pathPython) {
        Write-Step "Criando .venv local com python do PATH"
        & $pathPython.Source -m venv (Join-Path $RepoRoot ".venv")
        return $venvPython
    }

    throw "Python nao encontrado. Instale Python 3.12 ou rode primeiro o setup feito pelo Codex."
}

function Invoke-HealthCheck {
    param([string]$BaseUrl)

    $deadline = (Get-Date).AddSeconds(40)
    do {
        try {
            $health = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 3
            $ready = Invoke-RestMethod -Uri "$BaseUrl/ready" -TimeoutSec 3
            Write-Host "Health: $($health.status) / $($health.project)"
            Write-Host "Ready: ready=$($ready.ready), busy=$($ready.busy), mvp_profile=$($ready.mvp_profile)"
            return
        } catch {
            Start-Sleep -Seconds 1
        }
    } while ((Get-Date) -lt $deadline)

    throw "Backend nao respondeu em $BaseUrl dentro do tempo esperado."
}

function Enable-TailscaleServeIfRequested {
    param(
        [string]$BackendUrl,
        [int]$HttpsPort,
        [bool]$Enabled
    )

    if (-not $Enabled) {
        Write-Host "Tailscale Serve: ignorado. Use -EnableTailscaleServe para ativar HTTPS privado."
        return
    }

    $tailscale = Get-Command tailscale -ErrorAction SilentlyContinue
    if (-not $tailscale) {
        Write-Warning "tailscale nao esta no PATH. Instale/autentique Tailscale antes de expor o backend para o celular."
        return
    }

    Write-Step "Verificando Tailscale"
    & $tailscale.Source status | Out-Host

    Write-Step "Ativando Tailscale Serve privado"
    & $tailscale.Source serve --bg --https=$HttpsPort $BackendUrl
    & $tailscale.Source serve status | Out-Host
}

$repoRoot = Get-RepoRoot
Set-Location $repoRoot

if ($Port -lt 1 -or $Port -gt 65535) {
    throw "Informe -Port entre 1 e 65535 ou defina ARGUS_BACKEND_PORT."
}

$python = Get-Python -RepoRoot $repoRoot
$baseUrl = "http://${HostAddress}:$Port"

Write-Step "Ambiente Python"
Invoke-Native $python @("--version")

if (-not $SkipDependencyInstall) {
    Write-Step "Instalando/checando dependencias Python"
    Invoke-Native $python @("-m", "pip", "install", "-r", (Join-Path $repoRoot "requirements.txt"))
}

if (-not $SkipTests) {
    Write-Step "Rodando testes do backend"
    Invoke-Native $python @("-m", "pytest", "tests", "-q", "-p", "no:cacheprovider")
}

$env:ARGUS_MVP_PROFILE = "true"

if ($Detached) {
    Write-Step "Subindo backend em segundo plano"
    $logDir = Join-Path $repoRoot "logs"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $stdout = Join-Path $logDir "backend_stdout.log"
    $stderr = Join-Path $logDir "backend_stderr.log"
    $process = Start-Process -FilePath $python `
        -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", $HostAddress, "--port", "$Port") `
        -WorkingDirectory $repoRoot `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr

    $pidPath = Join-Path $logDir "backend.pid"
    Set-Content -LiteralPath $pidPath -Value $process.Id
    Invoke-HealthCheck -BaseUrl $baseUrl
    Enable-TailscaleServeIfRequested -BackendUrl $baseUrl -HttpsPort $TailscaleHttpsPort -Enabled:$EnableTailscaleServe.IsPresent
    Write-Host ""
    Write-Host "Backend rodando em segundo plano. PID: $($process.Id)"
    Write-Host "Logs: $stdout / $stderr"
    Write-Host "Para parar: Stop-Process -Id $($process.Id)"
    exit 0
}

Enable-TailscaleServeIfRequested -BackendUrl $baseUrl -HttpsPort $TailscaleHttpsPort -Enabled:$EnableTailscaleServe.IsPresent

Write-Step "Subindo backend em primeiro plano"
Write-Host "URL local: $baseUrl"
Write-Host "Use Ctrl+C para parar."
& $python -m uvicorn app.main:app --host $HostAddress --port $Port
