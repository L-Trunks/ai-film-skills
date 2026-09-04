# 把六个 skill 装进 Claude Code 的个人 skills 目录（Windows）。
#
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Project
#
# 重复执行是安全的：同名目录会先备份到 <skills 的上一级>\skills-backup\<时间戳>\ 再覆盖。
#
# ⛔ 本文件必须存成 **带 BOM 的 UTF-8**。Windows PowerShell 5.1 读无 BOM 的 .ps1
#    时按系统 ANSI 码页解码，中文字符串会碎成乱码并导致 ParserError，装都装不上。
param([switch]$Project)

$src = Join-Path $PSScriptRoot "skills"
if (-not (Test-Path $src)) { Write-Host "找不到 skills\ 目录，请在仓库根目录执行"; exit 1 }

if ($Project) {
  $dst = Join-Path (Get-Location) ".claude\skills"; $scope = "项目级"
} else {
  $dst = Join-Path $env:USERPROFILE ".claude\skills"; $scope = "个人级"
}
if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Force -Path $dst | Out-Null }

# ⛔ 备份目录不能留在 skills\ 里面 —— 它自带 SKILL.md，Claude Code 会把它当成
#    另一个同名 skill 一起加载，skill 列表里每一项都会出现两遍。
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$bak = Join-Path (Split-Path $dst -Parent) "skills-backup\$stamp"

$n = 0
foreach ($d in Get-ChildItem -Path $src -Directory) {
  if (-not (Test-Path (Join-Path $d.FullName "SKILL.md"))) { continue }
  $target = Join-Path $dst $d.Name
  if (Test-Path $target) {
    if (-not (Test-Path $bak)) { New-Item -ItemType Directory -Force -Path $bak | Out-Null }
    Move-Item -Path $target -Destination (Join-Path $bak $d.Name)
    Write-Host "  已有同名，备份到 skills-backup\$stamp\$($d.Name)"
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
