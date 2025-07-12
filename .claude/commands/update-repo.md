---
description: "基于 README.md 自动更新 GitHub 仓库信息"
---

# 更新仓库信息

基于项目 README.md 文件自动更新 GitHub 仓库的描述和话题标签。

## 执行步骤

1. 读取 @README.md 文件
2. 提取项目描述（通常是第3行）
3. 根据内容分析相关话题标签
4. 使用 gh repo edit 命令更新仓库信息

## 使用方法

在项目根目录执行：`/update-repo`

## 注意事项

- 需要安装 GitHub CLI (gh)
- 需要有仓库的写入权限
- 建议在 git 仓库中使用