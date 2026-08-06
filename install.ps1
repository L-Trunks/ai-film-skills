# 把六个 skill 装进 Claude Code 的个人 skills 目录（Windows）。
#
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Project
#
# 重复执行是安全的：同名目录会先备份成 <name>.bak-<时间戳> 再覆盖。
param([switch]$Project)

$src = Join-Path $PSScriptRoot "skills"
if (-not (Test-Path $src)) { Write-Host "找不到 skills\ 目录，请在仓库根目录执行"; exit 1 }

if ($Project) {
  $dst = Join-Path (Get-Location) ".claude\skills"; $scope = "项目级"
} else {
  $dst = Join-Path $env:USERPROFILE ".claude\skills"; $scope = "个人级"
}
if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Force -Path $dst | Out-Null }

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$n = 0
foreach ($d in Get-ChildItem -Path $src -Directory) {
  if (-not (Test-Path (Join-Path $d.FullName "SKILL.md"))) { continue }
  $target = Join-Path $dst $d.Name
  if (Test-Path $target) {
    Move-Item -Path $target -Destination "$target.bak-$stamp"
    Write-Host "  已有同名，备份为 $($d.Name).bak-$stamp"
  }
  Copy-Item -Path $d.FullName -Destination $target -Recurse
  Write-Host "  装好 $($d.Name)"
  $n++
}

Write-Host ""
Write-Host "共 $n 个 skill -> $dst（$scope）"
Write-Host ""
Write-Host "现在跟 Claude Code 说一句「做一部短片」就会触发。"
Write-Host "想跑仓库里的参考脚本，再改 skills\local-ai-film\examples\scripts\config.py 里的三个路径，"
Write-Host "然后 python doctor.py 体检。"
