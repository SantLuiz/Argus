param(
    [string]$ModelsDir = "models",
    [switch]$SkipYolo,
    [switch]$SkipMidas
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

    $pathPython = Get-Command python -ErrorAction SilentlyContinue
    if ($pathPython) {
        Write-Step "Criando .venv local com python do PATH"
        & $pathPython.Source -m venv (Join-Path $RepoRoot ".venv")
        return $venvPython
    }

    throw "Python nao encontrado. Instale Python 3.12 ou rode primeiro o setup do ambiente."
}

$repoRoot = Get-RepoRoot
Set-Location $repoRoot
$python = Get-Python -RepoRoot $repoRoot

Write-Step "Preparando diretorios de modelos"
New-Item -ItemType Directory -Force -Path (Join-Path $repoRoot $ModelsDir) | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $repoRoot "$ModelsDir\yolo") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $repoRoot "$ModelsDir\torch") | Out-Null

$arguments = @("scripts/prepare_models.py", "--models-dir", $ModelsDir)
if ($SkipYolo) {
    $arguments += "--skip-yolo"
}
if ($SkipMidas) {
    $arguments += "--skip-midas"
}

Write-Step "Baixando/aquecendo modelos"
& $python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao preparar modelos. Verifique conexao com a internet e dependencias Python."
}
