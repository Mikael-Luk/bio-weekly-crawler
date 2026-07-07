#!/bin/bash
cd ~/bio-weekly/src/dongmai
source ~/news_scraper/venv/bin/activate
python3 crawler.py
scp dongmai_*.md jichangtao@192.168.0.69:/docker/bio-weekly/data/reports/
scp dongmai_*.json jichangtao@192.168.0.69:/docker/bio-weekly/data/reports/