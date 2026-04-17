#!/bin/bash
cd /Users/brain/.openclaw/workspace/swimming_pauls

USER_ID="973dfe463ec85785"

echo "=== DEPOSIT ==="
python3 treasury_system.py deposit $USER_ID 10000

echo ""
echo "=== ALLOCATE TO PAULS ==="
python3 treasury_system.py allocate $USER_ID "Economy Paul" 2000 aggressive
python3 treasury_system.py allocate $USER_ID "AI Paul" 1500 moderate
python3 treasury_system.py allocate $USER_ID "Visionary Paul" 1000 conservative

echo ""
echo "=== SUMMARY ==="
python3 treasury_system.py summary $USER_ID