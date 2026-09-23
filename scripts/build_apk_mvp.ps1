param(
    [ValidateSet("debug", "release")]
    [string]$Mode = "debug",
    [string]$JavaHome = $env:JAVA_HOME,
    [string]$FlutterPath,
    [string]$AndroidSdkPath,
    [switch]$SkipAnalyze,
    [switch]$SkipTests,
    [switch]$Offline
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

function Resolve-JavaHome {
    param([string]$RequestedJavaHome)

    if ($RequestedJavaHome -and (Test-Path -LiteralPath $RequestedJavaHome)) {
        return (Resolve-Path $RequestedJavaHome).Path
    }

    $commonPaths = @(
        "C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot",
        "C:\Program Files\Microsoft\jdk-17",
        "C:\Program Files\Eclipse Adoptium\jdk-17*",
        "C:\Program Files\Java\jdk-17*"
    )

    foreach ($path in $commonPaths) {
        $match = Get-Item -LiteralPath $path -ErrorAction SilentlyContinue
        if ($match) {
            return $match.FullName
        }
        $wildcardMatch = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($wildcardMatch) {
            return $wildcardMatch.FullName
        }
    }

    throw "JDK 17 nao encontrado. Informe -JavaHome ou defina JAVA_HOME apontando para um JDK 17."
}

$repoRoot = Get-RepoRoot
$flutter = $FlutterPath
if (-not $flutter) {
    $localFlutter = Join-Path $repoRoot ".tools\flutter\bin\flutter.bat"
    if (Test-Path -LiteralPath $localFlutter) {
        $flutter = $localFlutter
    } else {
        $flutterCommand = Get-Command flutter -ErrorAction SilentlyContinue
        if ($flutterCommand) { $flutter = $flutterCommand.Source }
    }
}
$androidSdk = $AndroidSdkPath
if (-not $androidSdk) {
    $localSdk = Join-Path $repoRoot ".tools\android-sdk"
    if (Test-Path -LiteralPath $localSdk) { $androidSdk = $localSdk }
    elseif ($env:ANDROID_HOME) { $androidSdk = $env:ANDROID_HOME }
    else { $androidSdk = $env:ANDROID_SDK_ROOT }
}
$appDir = Join-Path $repoRoot "app_flutter"
$resolvedJavaHome = Resolve-JavaHome -RequestedJavaHome $JavaHome

if (-not $flutter -or -not (Test-Path -LiteralPath $flutter)) {
    throw "Flutter nao encontrado. Informe -FlutterPath, instale no PATH ou em .tools/flutter."
}

if (-not $androidSdk -or -not (Test-Path -LiteralPath $androidSdk)) {
    throw "Android SDK nao encontrado. Informe -AndroidSdkPath ou defina ANDROID_HOME."
}

$env:JAVA_HOME = $resolvedJavaHome
$env:ANDROID_HOME = (Resolve-Path $androidSdk).Path
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:FLUTTER_SUPPRESS_ANALYTICS = "true"

$localAppData = Join-Path $repoRoot ".tools\appdata\Local"
$roamingAppData = Join-Path $repoRoot ".tools\appdata\Roaming"
$gradleUserHome = Join-Path $repoRoot ".tools\gradle"
$androidUserHome = if ($env:ARGUS_ANDROID_USER_HOME) {
    $env:ARGUS_ANDROID_USER_HOME
} else {
    Join-Path $repoRoot ".tools\android-user-home"
}
New-Item -ItemType Directory -Force -Path $localAppData, $roamingAppData, $gradleUserHome, $androidUserHome | Out-Null
$env:LOCALAPPDATA = $localAppData
$env:APPDATA = $roamingAppData
$env:GRADLE_USER_HOME = $gradleUserHome
$env:ANDROID_USER_HOME = $androidUserHome
$env:JAVA_TOOL_OPTIONS = "-Duser.home=$androidUserHome"

Set-Location $appDir

Write-Step "Flutter"
Invoke-Native $flutter @("--version")

Write-Step "Resolvendo dependencias Flutter"
if ($Offline) {
    Invoke-Native $flutter @("pub", "get", "--offline")
} else {
    Invoke-Native $flutter @("pub", "get")
}

if (-not $SkipAnalyze) {
    Write-Step "Rodando flutter analyze"
    $analyzeArgs = @("analyze")
    if ($Offline) {
        $analyzeArgs += "--no-pub"
    }
    Invoke-Native $flutter $analyzeArgs
}

if (-not $SkipTests) {
    Write-Step "Rodando flutter test"
    $testArgs = @("test")
    if ($Offline) {
        $testArgs += "--no-pub"
    }
    Invoke-Native $flutter $testArgs
}

Write-Step "Build APK $Mode"
Write-Host "O backend sera configurado no app, pela tela Configuracoes."
$buildArgs = @("build", "apk", "--$Mode")
if ($Offline) {
    $buildArgs += "--no-pub"
}
Invoke-Native $flutter $buildArgs

$apkPath = if ($Mode -eq "release") {
    Join-Path $appDir "build\app\outputs\flutter-apk\app-release.apk"
} else {
    Join-Path $appDir "build\app\outputs\flutter-apk\app-debug.apk"
}

if (-not (Test-Path -LiteralPath $apkPath)) {
    throw "Build terminou, mas o APK esperado nao foi encontrado em $apkPath."
}

Write-Host ""
Write-Host "APK gerado:"
Write-Host $apkPath
$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $apkPath
Write-Host "SHA256:"
Write-Host $hash.Hash
