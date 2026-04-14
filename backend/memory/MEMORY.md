# MEMORY.md - Agent Memory

## 概述
本文件存储 Agent 的持久化记忆，包括：
- 项目约定和事实
- 工具使用经验
- 跨会话上下文

## 使用方式
通过 memory 工具读取/写入，内容会通过 fence 标签隔离防止误当作用户输入。
