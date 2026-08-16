#!/usr/bin/env bash

# Local skill registry for app-slop-audit.
# Source this script to resolve a skill name to its SKILL.md path.
#
# Usage:
#   source ./skill.sh app-slop-audit

declare -A SKILLS=(
  [app-slop-audit]="skills/app-slop-audit/SKILL.md"
)

if [[ $# -eq 0 ]]; then
  echo "Usage: source ./skill.sh <skill-name>"
  echo "Available skills: ${!SKILLS[@]}"
else
  echo "${SKILLS[$1]}"
fi