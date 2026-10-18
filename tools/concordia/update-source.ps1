<#
.SYNOPSIS
Brings an unzipped copy of this repository up to date from GitHub, downloading only changed files.

.DESCRIPTION
Updates the folders that Concordia work changes (by default forge-gui-mobile\src,
forge-gui\res\adventure\Concordia and tools\concordia) so they match the branch on
GitHub. Only files whose content differs are downloaded, and files that were deleted
from the repository are deleted locally. Run build-and-install.ps1 afterwards to
rebuild the Forge jar and copy Concordia into the Forge install.

The commit it synced to is written to .concordia-source-commit in the repository
folder. On the next run the script asks GitHub what changed since then, and stops if
anything changed outside these folders: in that case download the full ZIP instead.

.PARAMETER RepoDir
The repository folder (the one that contains forge-gui-mobile). Default: the folder two
levels above this script, or the current folder when the script is run from the
one-line command.

.PARAMETER Repo
The GitHub repository to download from. Default: oliandor712/forgecomventure

.PARAMETER Branch
The branch to download from. Default: campaign-design

.PARAMETER Paths
The repository folders to update, written with forward slashes.

.EXAMPLE
cd C:\Users\olian\concordia-build\forgecomventure-campaign-design
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor 3072; & ([scriptblock]::Create((irm https://raw.githubusercontent.com/oliandor712/forgecomventure/campaign-design/tools/concordia/update-source.ps1)))"

.EXAMPLE
powershell -ExecutionPolicy Bypass -File tools\concordia\update-source.ps1
#>
param(
    [string]$RepoDir = "",
    [string]$Repo = "oliandor712/forgecomventure",
    [string]$Branch = "campaign-design",
    [string[]]$Paths = @("forge-gui-mobile/src", "forge-gui/res/adventure/Concordia", "tools/concordia")
)

$ErrorActionPreference = "Stop"
# The download progress bar makes Invoke-WebRequest very slow in Windows PowerShell.
$ProgressPreference = "SilentlyContinue"
# Windows PowerShell 5.1 may default to TLS 1.0, which GitHub refuses. The one-line command in the
# first example sets this itself, because it downloads this script before this line can run.
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

if (-not $RepoDir) {
    if ($PSScriptRoot) {
        $RepoDir = Join-Path $PSScriptRoot "..\.."
    } else {
        $RepoDir = (Get-Location).Path
    }
}
if (-not (Test-Path -LiteralPath (Join-Path $RepoDir "forge-gui-mobile\pom.xml") -PathType Leaf)) {
    throw "'$RepoDir' is not the repository folder. Open the unzipped folder that contains forge-gui-mobile (cd into it), or pass -RepoDir."
}
# .NET file calls below resolve relative paths against a different folder than PowerShell does.
$RepoDir = (Resolve-Path -LiteralPath $RepoDir).Path

$api = "https://api.github.com/repos/$Repo"
$separator = [IO.Path]::DirectorySeparatorChar
$marker = Join-Path $RepoDir ".concordia-source-commit"

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

# Downloads one file, trying again twice after a dropped connection or a damaged download.
function Save-GitHubFile([string]$Uri, [string]$OutFile, [string]$Sha) {
    $problem = ""
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $Uri -OutFile $OutFile
            if ((Get-GitBlobSha $OutFile) -eq $Sha) {
                return
            }
            $problem = "the download came through damaged"
        } catch {
            $problem = $_.Exception.Message
        }
        if ($attempt -lt 3) {
            Start-Sleep -Seconds (2 * $attempt)
        }
    }
    throw "Could not download $Uri ($problem). Check your internet connection and run the update again."
}

Write-Host "Checking $Repo ($Branch) for changes..."
$commit = Invoke-GitHubApi "$api/commits/$Branch"
Write-Host "Latest commit: $($commit.sha.Substring(0, 8))"

# Changes outside the synced folders (for example a pom.xml or another module) need the full ZIP.
if (Test-Path -LiteralPath $marker -PathType Leaf) {
    $base = (Get-Content -LiteralPath $marker -Raw).Trim()
    if ($base -and $base -ne $commit.sha) {
        $compare = Invoke-GitHubApi "$api/compare/$base...$($commit.sha)"
        $outside = @()
        foreach ($changedFile in @($compare.files)) {
            $inside = $false
            foreach ($path in $Paths) {
                if ($changedFile.filename.StartsWith($path.TrimEnd("/") + "/")) {
                    $inside = $true
                }
            }
            if (-not $inside -and -not $changedFile.filename.StartsWith("docs/")) {
                $outside += $changedFile.filename
            }
        }
        if ($outside.Count -gt 0) {
            Write-Host "These files changed outside the folders this script updates:"
            $outside | ForEach-Object { Write-Host "  $_" }
            throw "Download the full ZIP into a new folder instead of using this update."
        }
    }
} else {
    Write-Host "First update of this folder: it can't check for changes outside $($Paths -join ', ')."
}

$downloaded = 0
$unchanged = 0
$removed = 0
foreach ($path in $Paths) {
    $path = $path.Trim("/")
    $cut = $path.LastIndexOf("/")
    if ($cut -ge 0) {
        $parent = Invoke-GitHubApi "$api/contents/$($path.Substring(0, $cut))?ref=$($commit.sha)"
    } else {
        $parent = Invoke-GitHubApi "$api/contents?ref=$($commit.sha)"
    }
    $name = $path.Substring($cut + 1)
    $folder = $parent | Where-Object { $_.name -eq $name -and $_.type -eq "dir" }
    if (-not $folder) {
        throw "There is no folder '$path' on branch '$Branch' of $Repo."
    }
    $tree = Invoke-GitHubApi "$api/git/trees/$($folder.sha)?recursive=1"
    if ($tree.truncated) {
        throw "GitHub sent only part of the file list for '$path'. Download the full ZIP instead."
    }

    $localRoot = Join-Path $RepoDir $path.Replace("/", $separator)
    $wanted = @{}
    foreach ($file in @($tree.tree | Where-Object { $_.type -eq "blob" })) {
        $relative = $file.path.Replace("/", $separator)
        $wanted[$relative.ToLowerInvariant()] = $true
        $local = Join-Path $localRoot $relative
        if ((Test-Path -LiteralPath $local -PathType Leaf) -and (Get-GitBlobSha $local) -eq $file.sha) {
            $unchanged++
            continue
        }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $local) | Out-Null
        $encoded = ($file.path -split "/" | ForEach-Object { [Uri]::EscapeDataString($_) }) -join "/"
        $temp = $local + ".download"
        Save-GitHubFile "https://raw.githubusercontent.com/$Repo/$($commit.sha)/$path/$encoded" $temp $file.sha
        [IO.File]::Copy($temp, $local, $true)
        Remove-Item -LiteralPath $temp -Force
        Write-Host "  updated $path/$($file.path)"
        $downloaded++
    }

    if (Test-Path -LiteralPath $localRoot) {
        $prefixLength = (Get-Item -LiteralPath $localRoot).FullName.TrimEnd($separator).Length + 1
        foreach ($item in @(Get-ChildItem -LiteralPath $localRoot -Recurse -File)) {
            $relative = $item.FullName.Substring($prefixLength)
            if (-not $wanted.ContainsKey($relative.ToLowerInvariant())) {
                Remove-Item -LiteralPath $item.FullName -Force
                Write-Host "  removed $path/$($relative.Replace($separator, '/'))"
                $removed++
            }
        }
    }
}

Set-Content -LiteralPath $marker -Value $commit.sha
Write-Host ""
Write-Host "Done: $downloaded updated, $unchanged unchanged, $removed removed."
Write-Host "Next: powershell -ExecutionPolicy Bypass -File tools\concordia\build-and-install.ps1"
