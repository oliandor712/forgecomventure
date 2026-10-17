<#
.SYNOPSIS
Builds Forge's Adventure code on this PC and installs it, with the Concordia plane, into a Forge install.

.DESCRIPTION
1. Runs a Maven build of forge-gui-mobile-dev and its dependencies from this repository.
   Needs JDK 17 or newer and Maven on PATH. Maven downloads dependencies, including the
   jitpack.io repository, so this must run on a machine with normal internet access.
2. Replaces the installed forge-gui-mobile jar with the built one. Each installed jar is
   backed up to <ForgeDir>\adventure-backups first.
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
$jarPattern = '^forge-gui-mobile-\d'

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

$built = Get-ChildItem -Path (Join-Path $RepoDir "forge-gui-mobile\target") -Filter "*.jar" -File |
    Where-Object { $_.Name -match $jarPattern } | Select-Object -First 1
if (-not $built) {
    throw "No forge-gui-mobile jar in forge-gui-mobile\target. Run without -SkipBuild first."
}
Write-Host "Built jar: $($built.FullName)"

if (-not (Test-Path $ForgeDir)) {
    throw "Forge folder not found: $ForgeDir. Pass the right folder with -ForgeDir."
}
$installed = Get-ChildItem -Path $ForgeDir -Filter "*.jar" -Recurse -File |
    Where-Object { $_.Name -match $jarPattern -and $_.FullName -notlike "*adventure-backups*" }
if (-not $installed) {
    throw "No forge-gui-mobile jar found under $ForgeDir. Send the jar list from that folder and this can be matched by hand."
}

$backupRoot = Join-Path $ForgeDir "adventure-backups"
New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($jar in $installed) {
    $backup = Join-Path $backupRoot ($jar.BaseName + "-" + $stamp + ".jar")
    Copy-Item -Path $jar.FullName -Destination $backup
    Copy-Item -Path $built.FullName -Destination $jar.FullName -Force
    Write-Host "Replaced: $($jar.FullName)  (backup: $backup)"
}
if ($installed.Count -gt 1) {
    Write-Host "Note: more than one forge-gui-mobile jar was found. Check the install's lib folder."
}
if ($installed[0].Name -ne $built.Name) {
    Write-Host "Note: the installed jar is named $($installed[0].Name) and the built one is $($built.Name)."
    Write-Host "The new jar was copied under the installed name. The other Forge jars must be the same version."
}

& (Join-Path $PSScriptRoot "copy-to-install.ps1") -ForgeDir $ForgeDir -RepoDir $RepoDir

Write-Host ""
Write-Host "Done. Start Forge, open Adventure > Settings > Plane, choose Concordia, and start a new game."
