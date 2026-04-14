#!/bin/bash
cd /Users/brain/.openclaw/workspace/swimming_pauls
python3 local_agent.py --port 8765 2>&1 | tee /tmp/pauls_agent.log
