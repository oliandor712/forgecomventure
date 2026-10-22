# Create a worktree for a second Claude Code session. Usage: powershell -File tools/agents/worktree_setup.ps1 <name> [parentDir]
param([Parameter(Mandatory=$true)][string]$Name, [string]$Parent = "")
$ErrorActionPreference = "Stop"
$Repo = (git rev-parse --show-toplevel).Trim()
if (-not $Parent) { $Parent = Split-Path $Repo -Parent }
$WT = Join-Path $Parent ((Split-Path $Repo -Leaf) + "-" + $Name)
$BR = "cd/$Name"
git -C $Repo fetch origin campaign-design
git -C $Repo config rerere.enabled true
if (Test-Path $WT) { Write-Host "exists: $WT" } else { git -C $Repo worktree add -b $BR $WT origin/campaign-design }
$Deps = Join-Path $Parent "concordia-deps\i5jb"
$Data = Join-Path $Deps "mtgish\data\mtgish.lines.json"
if (-not (Test-Path $Data)) {
  New-Item -ItemType Directory -Force $Deps | Out-Null
  $env:GIT_LFS_SKIP_SMUDGE = "1"
  git clone --depth 1 https://github.com/i5jb/mtgish (Join-Path $Deps "mtgish")
}
$env:MTGISH_DATA = $Data
Write-Host "worktree: $WT  branch: $BR"
Write-Host "persist with: setx MTGISH_DATA `"$Data`""
Push-Location $WT; python tools/agents/clone_verify.py; Pop-Location
