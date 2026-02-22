$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Join-Path $ScriptDir "SpellforceDataEditor"
$OutputDir = Join-Path $ProjectDir "bin\Release\net8.0-windows10.0.17763.0"
$TargetDir = $ProjectDir

Write-Host "=== SpellForce Data Editor Build Script ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectDir"

try {
    $dotnetVersion = dotnet --version 2>$null
    Write-Host "Found dotnet SDK: $dotnetVersion" -ForegroundColor Green
} catch {
    Write-Host ".NET SDK not found. Please install .NET 8.0 SDK." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Restoring NuGet packages..." -ForegroundColor Yellow
dotnet restore "SpellforceDataEditor.sln" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Package restore failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Packages restored" -ForegroundColor Green

Write-Host ""
Write-Host "Building Release configuration..." -ForegroundColor Yellow
dotnet build "SpellforceDataEditor.sln" -c Release -p:Platform=x86 --no-restore 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Build completed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "Copying all required files to target directory..." -ForegroundColor Yellow

# Files and patterns to copy
$FilesToCopy = @(
    "SpellforceDataEditor.exe",
    "SpellforceDataEditor.dll",
    "SpellforceDataEditor.deps.json",
    "SpellforceDataEditor.runtimeconfig.json",
    "SpellforceDataEditor.dll.config",
    "SFEngine.dll",
    "NAudio.dll",
    "NAudio.*.dll",
    "OpenTK.*.dll",
    "SDL2.dll",
    "Microsoft.Windows.SDK.NET.dll",
    "WinRT.Runtime.dll",
    "config.txt",
    "pakdata.dat"
)

# Copy files
foreach ($Pattern in $FilesToCopy) {
    $SourceFiles = Get-ChildItem -Path $OutputDir -Filter $Pattern -ErrorAction SilentlyContinue
    foreach ($SourceFile in $SourceFiles) {
        $TargetFile = Join-Path $TargetDir $SourceFile.Name

        # Remove old file if exists
        if (Test-Path $TargetFile) {
            Remove-Item $TargetFile -Force
        }

        # Copy file
        Copy-Item $SourceFile.FullName $TargetFile -Force
        Write-Host "  Copied $($SourceFile.Name)" -ForegroundColor Gray
    }
}

# Copy runtimes directory if it exists
$RuntimesSource = Join-Path $OutputDir "runtimes"
if (Test-Path $RuntimesSource) {
    $RuntimesTarget = Join-Path $TargetDir "runtimes"

    # Remove old runtimes if exists
    if (Test-Path $RuntimesTarget) {
        Remove-Item $RuntimesTarget -Recurse -Force
    }

    # Copy runtimes directory
    Copy-Item $RuntimesSource $TargetDir -Recurse -Force
    Write-Host "  Copied runimes/" -ForegroundColor Gray
}

# Copy sound directory if it exists
$SoundSource = Join-Path $OutputDir "sound"
if (Test-Path $SoundSource) {
    $SoundTarget = Join-Path $TargetDir "sound"

    # Remove old sound if exists
    if (Test-Path $SoundTarget) {
        Remove-Item $SoundTarget -Recurse -Force
    }

    # Copy sound directory
    Copy-Item $SoundSource $TargetDir -Recurse -Force
    Write-Host "  Copied sound/" -ForegroundColor Gray
}

$ExeTarget = Join-Path $TargetDir "SpellforceDataEditor.exe"
$FileInfo = Get-Item $ExeTarget
Write-Host ""
Write-Host "=== Build Complete ===" -ForegroundColor Green
Write-Host "Exe location: $ExeTarget" -ForegroundColor Cyan
Write-Host "Total size: $([math]::Round((Get-ChildItem $TargetDir -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)) MB" -ForegroundColor Cyan
