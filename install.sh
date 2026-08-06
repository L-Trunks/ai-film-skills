#!/usr/bin/env bash
# 把六个 skill 装进 Claude Code 的个人 skills 目录。
#
#   bash install.sh              装到 ~/.claude/skills/（个人级，所有项目可用）
#   bash install.sh --project    装到 ./.claude/skills/（只对当前项目可用）
#
# 重复执行是安全的：同名目录会先备份成 <name>.bak-<时间戳> 再覆盖。
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
DST="$HOME/.claude/skills"
SCOPE="个人级"
if [ "${1:-}" = "--project" ]; then
  DST="$(pwd)/.claude/skills"
  SCOPE="项目级"
fi

[ -d "$SRC" ] || { echo "找不到 skills/ 目录，请在仓库根目录执行"; exit 1; }
mkdir -p "$DST"

stamp=$(date +%Y%m%d-%H%M%S)
n=0
for d in "$SRC"/*/; do
  name=$(basename "$d")
  [ -f "$d/SKILL.md" ] || continue
  if [ -e "$DST/$name" ]; then
    mv "$DST/$name" "$DST/$name.bak-$stamp"
    echo "  已有同名，备份为 $name.bak-$stamp"
  fi
  cp -r "$d" "$DST/$name"
  echo "  装好 $name"
  n=$((n+1))
done

echo
echo "共 $n 个 skill -> $DST（$SCOPE）"
echo
echo "现在跟 Claude Code 说一句「做一部短片」就会触发。"
echo "想跑仓库里的参考脚本，再改 skills/local-ai-film/examples/scripts/config.py 里的三个路径，"
echo "然后 python doctor.py 体检。"
