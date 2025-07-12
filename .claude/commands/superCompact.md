---
description: 超级压缩：压缩会话内容 + 自动提交 + 更新项目文件
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git branch:*), Bash(git log:*), Bash(git diff:*), Edit, Write, Read
---

# SuperCompact - 超级压缩命令

## 当前状态

- Git状态: !`git status --porcelain`
- 当前分支: !`git branch --show-current`
- 最近3个提交: !`git log --oneline -3`
- 未提交的变更: !`git diff --stat`

## 执行任务

执行以下任务序列：

### 1. 压缩会话内容
首先执行标准的 `/compact` 操作来压缩当前会话历史，保留关键信息。

### 2. 更新项目管理文件

#### 更新/创建 CLAUDE.md
- 如果文件存在，在文件末尾添加SuperCompact执行记录
- 如果文件不存在，创建新文件并包含基本说明

内容格式：
```markdown
## SuperCompact 记录

最后执行时间: [时间戳]
执行内容: 会话压缩 + 自动提交 + 项目文件更新
Git提交: [提交哈希] (如果适用)
```

#### 更新 .supercompact_log
创建或追加日志文件，记录每次SuperCompact的执行时间和状态。

### 3. 创建Git提交
如果当前目录是Git仓库且有变更（包括刚才更新的项目文件）：
- 添加所有变更到暂存区 (`git add .`)
- 创建提交，提交信息格式：
  ```
  auto: compact session at [时间戳]
  
  🤖 Generated with [Claude Code](https://claude.ai/code)
  
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

## 执行要求

1. **有序执行**：严格按照上述1-2-3的顺序执行（先compact，再更新文件，最后git提交）
2. **错误处理**：如果某一步失败，继续执行后续步骤
3. **状态反馈**：每完成一个步骤都要明确告知用户
4. **最终总结**：执行完成后提供完整的执行摘要

## 预期输出

执行完成后应输出：
```
🎉 SuperCompact 执行完成！

📊 执行摘要:
   ✅ 会话内容已压缩
   ✅ Git提交已创建: [commit-hash] (如果适用)
   ✅ 项目文件已更新
   ⏰ 执行时间: [时间戳]
```

开始执行SuperCompact...