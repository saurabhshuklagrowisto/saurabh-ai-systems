---
name: group-scan
trigger: "analyse groups" OR "check groups" OR "scan groups"
---
When the owner says "analyse groups", "check groups", or "scan groups":
1. Make HTTP POST to http://127.0.0.1:5678/webhook/group-scan
2. Reply: "Scanning groups now."
