<#
.SYNOPSIS
Builds Forge's Adventure code on this PC and installs it, with the Concordia plane, into a Forge install.

.DESCRIPTION
1. Runs a Maven build of forge-gui-mobile-dev from this repository. This produces
   forge-gui-mobile-dev-<version>-jar-with-dependencies.jar, the bundled Adventure game that
   the install runs. Needs JDK 17 or newer and Maven on PATH. Maven downloads dependencies,
   including the jitpack.io repository, so this must run on a machine with normal internet access.
2. Replaces the installed jar-with-dependencies file with the built one. The installed file is
   backed up to <ForgeDir>\adventure-backups first, and keeps its name.
3. Copies the Concordia plane into <ForgeDir>\res\adventure\Concordia (via copy-to-install.ps1).

Nothing in the install is deleted. Backups are kept in <ForgeDir>\adventure-backups.

.PARAMETER ForgeDir
The Forge install folder. Default: C:\Users\olian\Forge

.PARAMETER RepoDir
The repository root. Default: the folder two levels above this script.

.PARAMETER SkipBuild
Do not run Maven. Use the jar already in forge-gui-mobile\target.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File tools\concordia\build-and-install.ps1
#>
param(
    [string]$ForgeDir = "C:\Users\olian\Forge",
    [string]$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$builtPattern = 'forge-gui-mobile-dev-.*jar-with-dependencies\.jar$'
$installedPattern = 'forge-gui-mobile-dev-.*jar-with-dependencies'


if (-not $SkipBuild) {
    if (-not (Get-Command mvn -ErrorAction SilentlyContinue)) {
        throw "Maven (mvn) is not on PATH. Install Maven 3.8+ and JDK 17+, then run this again."
    }
    Push-Location $RepoDir
    try {
        Write-Host "Building forge-gui-mobile-dev and its dependencies. This can take 10-20 minutes."
        & mvn -B -pl forge-gui-mobile-dev -am package -DskipTests
        if ($LASTEXITCODE -ne 0) {
            throw "Maven build failed. Read the errors above. Send them back if you need help."
        }
    }
    finally {
        Pop-Location
    }
}

$built = Get-ChildItem -Path (Join-Path $RepoDir "forge-gui-mobile-dev\target") -Filter "*.jar" -File |
    Where-Object { $_.Name -match $builtPattern } | Select-Object -First 1
if (-not $built) {
    throw "No jar-with-dependencies in forge-gui-mobile-dev\target. Run without -SkipBuild first."
}
Write-Host "Built jar: $($built.FullName)"

if (-not (Test-Path $ForgeDir)) {
    throw "Forge folder not found: $ForgeDir. Pass the right folder with -ForgeDir."
}
$installed = Get-ChildItem -Path $ForgeDir -Recurse -File |
    Where-Object { $_.Name -match $installedPattern -and $_.FullName -notlike "*adventure-backups*" }
if (-not $installed) {
    throw "No forge-gui-mobile-dev jar-with-dependencies found under $ForgeDir. Check the -ForgeDir path."
}

$backupRoot = Join-Path $ForgeDir "adventure-backups"
New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($jar in $installed) {
    $backup = Join-Path $backupRoot ($jar.Name + "-" + $stamp)
    Copy-Item -Path $jar.FullName -Destination $backup
    Copy-Item -Path $built.FullName -Destination $jar.FullName -Force
    Write-Host "Replaced: $($jar.FullName)  (backup: $backup)"
}
if ($installed.Count -gt 1) {
    Write-Host "Note: more than one Adventure jar was found. Each was replaced; check the install folder."
}
if ($installed[0].Name -ne $built.Name) {
    Write-Host "Note: the installed file is $($installed[0].Name). The built file is $($built.Name). The built file was copied under the installed name."
}

& (Join-Path $PSScriptRoot "copy-to-install.ps1") -ForgeDir $ForgeDir -RepoDir $RepoDir

Write-Host ""
Write-Host "Done. Start Forge, open Adventure > Settings > Plane, choose Concordia, and start a new game."
