<#
.SYNOPSIS
Copies the Concordia adventure plane from this repository into a Forge install.

.DESCRIPTION
Copies forge-gui\res\adventure\Concordia into <ForgeDir>\res\adventure\Concordia.
An existing Concordia folder in the install is moved to <ForgeDir>\adventure-backups
first, so nothing you changed by hand is lost. The Realm of Legends plane and the
rest of the install are not touched, except the few shared files Concordia adds outside its
folder (listed in $sharedFiles, such as the debug menu's token script), which are copied
into their own place under <ForgeDir>\res.

.PARAMETER ForgeDir
The Forge install folder, the one that contains res\adventure.
Default: C:\Users\olian\Forge

.PARAMETER RepoDir
The repository root. Default: the folder two levels above this script.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File tools\concordia\copy-to-install.ps1

.EXAMPLE
powershell -ExecutionPolicy Bypass -File tools\concordia\copy-to-install.ps1 -ForgeDir "D:\Games\Forge"
#>
param(
    [string]$ForgeDir = "C:\Users\olian\Forge",
    [string]$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

$source = Join-Path $RepoDir "forge-gui\res\adventure\Concordia"
$adventureDir = Join-Path $ForgeDir "res\adventure"
$target = Join-Path $adventureDir "Concordia"
$backupRoot = Join-Path $ForgeDir "adventure-backups"

if (-not (Test-Path $source)) {
    throw "Concordia source folder not found: $source. Run this script from a full copy of the repository."
}
if (-not (Test-Path $adventureDir)) {
    throw "No res\adventure folder under '$ForgeDir'. Pass the Forge install folder with -ForgeDir."
}

if (Test-Path $target) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $backup = Join-Path $backupRoot ("Concordia-" + $stamp)
    Move-Item -Path $target -Destination $backup
    Write-Host "Existing Concordia moved to: $backup"
}

Copy-Item -Path $source -Destination $target -Recurse -Force

$count = (Get-ChildItem -Path $target -Recurse -File).Count
Write-Host "Copied $count files to: $target"

# Files Concordia needs outside its own folder, relative to forge-gui\res.
$sharedFiles = @(
    "tokenscripts\c_0_1_a_debug_wand_haste.txt"   # Debug Wand, the debug menu's instant win token
)
foreach ($file in $sharedFiles) {
    $from = Join-Path $RepoDir (Join-Path "forge-gui\res" $file)
    $to = Join-Path $ForgeDir (Join-Path "res" $file)
    New-Item -ItemType Directory -Force -Path (Split-Path $to) | Out-Null
    Copy-Item -Path $from -Destination $to -Force
    Write-Host "Copied: res\$file"
}
Write-Host ""
Write-Host "Next: start Forge, open Adventure > Settings > Plane, choose Concordia, then start a new game."
Write-Host "Note: the opening's color choice and tutorial raiders need the rebuilt Forge jar (J-Start, J-Ante, J-Raid)."
