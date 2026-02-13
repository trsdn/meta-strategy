#!/bin/bash
# Send push notification via ntfy.sh
# Usage: ./scripts/copilot-notify.sh "Title" "Message" [priority]
#
# Examples:
#   ./scripts/copilot-notify.sh "✅ Task Complete" "All tests passing"
#   ./scripts/copilot-notify.sh "🔔 Decision needed" "Should we add Redis?" "high"

NTFY_TOPIC="${NTFY_TOPIC:-$(sed -n 's/^export NTFY_TOPIC="\(.*\)"/\1/p' ~/.zshrc 2>/dev/null)}"

if [ -z "$NTFY_TOPIC" ]; then
  echo "Set NTFY_TOPIC env var"
  exit 1
fi

TITLE="${1:-Copilot notification}"
MESSAGE="${2:-Task completed}"
PRIORITY="${3:-default}"

curl -s -H "Title: $TITLE" -H "Priority: $PRIORITY" -d "$MESSAGE" "ntfy.sh/$NTFY_TOPIC"
