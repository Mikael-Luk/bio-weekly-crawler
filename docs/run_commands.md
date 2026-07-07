# 生物经济投融资周报 - 爬虫执行指令

## 快速运行

```bash
cd ~/bio-weekly
./run_all.sh
cd ~/bio-weekly/src/dongmai
source ~/news_scraper/venv/bin/activate
python3 crawler.py
cat ~/bio-weekly/cron.log
scp dongmai_*.md jichangtao@192.168.0.69:/volume1/docker/bio-weekly/data/reports/
scp dongmai_*.json jichangtao@192.168.0.69:/volume1/docker/bio-weekly/data/reports/
ssh jichangtao@192.168.0.69 "ls -la /volume1/docker/bio-weekly/data/reports/"
```
