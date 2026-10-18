<#
.SYNOPSIS
Updates the Concordia adventure plane in a Forge install straight from GitHub.

.DESCRIPTION
Downloads only the files in forge-gui\res\adventure\Concordia that differ from the
installed copy, so you don't need the full repository ZIP (the whole Concordia folder
is under 2 MB). Files that were removed from the repository are removed from the
install too. The installed Concordia folder is moved to <ForgeDir>\adventure-backups
before the new one replaces it.

This updates the plane's data only (maps, quests, decks, enemies). When the Forge
code changes, you still need the full repository and build-and-install.ps1.

.PARAMETER ForgeDir
The Forge install folder, the one that contains res\adventure.
Default: C:\Users\olian\Forge

.PARAMETER Repo
The GitHub repository to download from. Default: oliandor712/forgecomventure

.PARAMETER Branch
The branch to download from. Default: campaign-design

.EXAMPLE
powershell -ExecutionPolicy Bypass -Command "& ([scriptblock]::Create((irm https://raw.githubusercontent.com/oliandor712/forgecomventure/campaign-design/tools/concordia/update-concordia.ps1)))"

.EXAMPLE
powershell -ExecutionPolicy Bypass -File tools\concordia\update-concordia.ps1 -ForgeDir "D:\Games\Forge"
#>
param(
    [string]$ForgeDir = "C:\Users\olian\Forge",
    [string]$Repo = "oliandor712/forgecomventure",
    [string]$Branch = "campaign-design"
)

$ErrorActionPreference = "Stop"
# The download progress bar makes Invoke-WebRequest very slow in Windows PowerShell.
$ProgressPreference = "SilentlyContinue"
# Windows PowerShell 5.1 may default to TLS 1.0, which GitHub refuses.
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

if (-not (Test-Path -LiteralPath $ForgeDir -PathType Container)) {
    throw "Forge folder not found: '$ForgeDir'. Pass the Forge install folder with -ForgeDir."
}

$sourcePath = "forge-gui/res/adventure/Concordia"
$api = "https://api.github.com/repos/$Repo"
$adventureDir = Join-Path $ForgeDir "res\adventure"
$target = Join-Path $adventureDir "Concordia"
$backupRoot = Join-Path $ForgeDir "adventure-backups"
$separator = [IO.Path]::DirectorySeparatorChar

if (-not (Test-Path -LiteralPath $adventureDir)) {
    throw "No res\adventure folder under '$ForgeDir'. Pass the Forge install folder with -ForgeDir."
}

function Invoke-GitHubApi([string]$Uri) {
    try {
        return Invoke-RestMethod -UseBasicParsing -Uri $Uri
    } catch {
        throw "GitHub did not answer '$Uri': $($_.Exception.Message) GitHub allows 60 checks an hour without signing in; if you ran this many times, wait a while and try again."
    }
}

# The SHA-1 git stores for a file, so unchanged files can be skipped without downloading them.
function Get-GitBlobSha([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    $header = [Text.Encoding]::ASCII.GetBytes("blob $($bytes.Length)`0")
    $sha1 = [Security.Cryptography.SHA1]::Create()
    try {
        [void]$sha1.TransformBlock($header, 0, $header.Length, $null, 0)
        [void]$sha1.TransformFinalBlock($bytes, 0, $bytes.Length)
        return ([BitConverter]::ToString($sha1.Hash) -replace "-", "").ToLowerInvariant()
    } finally {
        $sha1.Dispose()
    }
}

Write-Host "Checking $Repo ($Branch) for Concordia changes..."
$commit = Invoke-GitHubApi "$api/commits/$Branch"
$parent = Invoke-GitHubApi "$api/contents/forge-gui/res/adventure?ref=$($commit.sha)"
$folder = $parent | Where-Object { $_.name -eq "Concordia" -and $_.type -eq "dir" }
if (-not $folder) {
    throw "There is no Concordia folder on branch '$Branch' of $Repo."
}
$tree = Invoke-GitHubApi "$api/git/trees/$($folder.sha)?recursive=1"
if ($tree.truncated) {
    throw "GitHub sent only part of the file list. Use the full repository ZIP and copy-to-install.ps1 instead."
}
$files = @($tree.tree | Where-Object { $_.type -eq "blob" })
Write-Host "Latest commit: $($commit.sha.Substring(0, 8)), $($files.Count) files in Concordia."

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
$staging = Join-Path $backupRoot ("Concordia-download-" + $stamp)
New-Item -ItemType Directory -Force -Path $staging | Out-Null

# Build the new folder next to the backups: unchanged files are copied from the install,
# changed and new ones are downloaded. The install is only touched once this succeeds.
$downloaded = 0
$unchanged = 0
$wanted = @{}
try {
    foreach ($file in $files) {
        $relative = $file.path.Replace("/", $separator)
        $wanted[$relative.ToLowerInvariant()] = $true
        $installed = Join-Path $target $relative
        $staged = Join-Path $staging $relative
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $staged) | Out-Null
        if ((Test-Path -LiteralPath $installed -PathType Leaf) -and (Get-GitBlobSha $installed) -eq $file.sha) {
            Copy-Item -LiteralPath $installed -Destination $staged
            $unchanged++
            continue
        }
        $encoded = ($file.path -split "/" | ForEach-Object { [Uri]::EscapeDataString($_) }) -join "/"
        Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/$Repo/$($commit.sha)/$sourcePath/$encoded" -OutFile $staged
        if ((Get-GitBlobSha $staged) -ne $file.sha) {
            throw "The download of $($file.path) came through damaged. Run the update again."
        }
        Write-Host "  downloaded $($file.path)"
        $downloaded++
    }
} catch {
    Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction SilentlyContinue
    throw
}

$removed = @()
if (Test-Path -LiteralPath $target) {
    $prefixLength = (Resolve-Path -LiteralPath $target).Path.TrimEnd($separator).Length + 1
    foreach ($item in Get-ChildItem -LiteralPath $target -Recurse -File) {
        $relative = $item.FullName.Substring($prefixLength)
        if (-not $wanted.ContainsKey($relative.ToLowerInvariant())) {
            $removed += $relative
            Write-Host "  removing $relative"
        }
    }
}

if ($downloaded -eq 0 -and $removed.Count -eq 0) {
    Remove-Item -LiteralPath $staging -Recurse -Force
    Write-Host "Concordia is already up to date: $target"
    return
}

$backup = $null
if (Test-Path -LiteralPath $target) {
    $backup = Join-Path $backupRoot ("Concordia-" + $stamp)
    try {
        Move-Item -LiteralPath $target -Destination $backup
    } catch {
        Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction SilentlyContinue
        throw "Could not move the installed Concordia folder. Close Forge and run the update again. ($($_.Exception.Message))"
    }
}
try {
    Move-Item -LiteralPath $staging -Destination $target
} catch {
    if ($backup) {
        Move-Item -LiteralPath $backup -Destination $target
    }
    throw
}

Write-Host ""
Write-Host "Done: $downloaded downloaded, $unchanged unchanged, $($removed.Count) removed."
if ($backup) {
    Write-Host "Previous Concordia moved to: $backup"
}
Write-Host "Start Forge and play Concordia. If Forge was open, restart it first."
