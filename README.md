# 生物经济投融资周报爬虫

**项目目标**：自动采集生物医药、合成生物、生物制造等领域的投融资情报，支撑周报生成。

## 主要功能
- 动脉网情报采集（已实现）
- 数据保存为 Markdown + JSON
- 自动同步到 NAS

## 项目结构
bio-weekly/
├── src/
│   └── dongmai/          # 动脉网爬虫主代码
├── scripts/
│   └── run_and_upload.sh # 执行入口
├── docs/                 # 文档
└── data/                 # 输出结果（可选）

## 使用方法

```bash
# 运行动脉网爬虫
./scripts/run_and_upload.sh


后续开发计划

 增加 36氪、投资界等多个源
 LLM 结构化提取（公司、轮次、金额等）
 自动生成完整周报
 Docker 容器化部署

技术栈

Python + Playwright
Git + SCP 同步到 NAS