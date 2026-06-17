<p align="center">
  <img src="./assets/logo.png" alt="Plan Governance logo" width="128" />
</p>

<h1 align="center">Plan Governance</h1>

<p align="center">
  <strong>让项目计划文档在 brownfield 仓库里保持当前、可见、可治理。</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="#30-秒开始">30 秒开始</a> ·
  <a href="#真实产物">真实产物</a>
</p>

<p align="center">
  <a href="./LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-0F766E.svg" /></a>
  <img alt="Codex Plugin" src="https://img.shields.io/badge/Codex-Plugin-111827.svg" />
  <img alt="Language" src="https://img.shields.io/badge/docs-English%20%2F%20%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-2563EB.svg" />
</p>

<p align="center">
  <img src="./assets/hero-banner.png" alt="Plan Governance overview" width="900" />
</p>

## 为什么会有这个 skill

Claude 写了一份新的生产级计划。Codex 后来进入同一个项目时，没有确认当前执行主线，结果把一份旧计划当成了当前事实来源。

这不是罕见事故，而是多 agent、长周期项目里很常见的问题：不同 agent 会创建不同计划，旧文档还留在仓库里，项目却靠聊天上下文记住“现在到底该按哪份走”。

`plan-governance` 把这种隐含记忆变成仓库内可见状态。它不负责替你写所有计划，它负责治理计划文档的生命周期：接入分析、registry、替代关系、关闭、以及启用后的持续维护。

## 它解决什么

| 问题 | plan-governance 做什么 |
|---|---|
| 多份文档都像“当前计划” | 创建 canonical `docs/plan_registry.md`，记录生命周期和权威性字段 |
| 新计划替代旧计划，但没人记录关系 | 维护 `supersedes` / `superseded_by` 替代关系 |
| 老项目里已经有一堆历史文档 | 先做只读接入分析，再决定是否正式治理 |
| agent 总是依赖聊天上下文 | 启用治理后安装 managed `AGENTS.md` block |
| 用户不想长期记一堆维护命令 | 启用后主动维护 register、refresh、close、supersede、lint |

## 30 秒开始

### 安装

在 Codex 里，用 `$skill-installer` 从这个 GitHub 仓库安装：

```text
用 $skill-installer 从 GitHub 安装 cici-uu8/Plan-governance-Skill。
```

如果新 skill 没有立即出现，重启 Codex。

### 使用

安装后只需要记住两句固定入口：

```text
用 $plan-governance 接入分析这个仓库。
用 $plan-governance 启用计划治理。
```

| 入口 | 含义 |
|---|---|
| `用 $plan-governance 接入分析这个仓库。` | 只读扫描。会写 adoption report，但不创建 registry，也不修改 `AGENTS.md`。 |
| `用 $plan-governance 启用计划治理。` | 创建治理文件，并默认安装 managed `AGENTS.md` block，除非你明确拒绝。 |

## 启用后会发生什么

一旦仓库里存在 `docs/plan_registry.md`，这个仓库就被视为已启用计划治理。

| 事件 | 默认行为 |
|---|---|
| 出现新的计划文档 | 主动 register 或 refresh 治理状态 |
| 新计划替代旧计划 | 建立替代关系，并把旧计划标记为 superseded |
| 计划结束且没有后继 | close 它，而不是继续改历史正文 |
| 治理状态变化 | 刷新 timeline report 并执行 lint |
| 多份文档都可能是当前计划 | 先问用户，不擅自决定 |
| 新文档可能是替代，也可能是并行工作流 | 先问用户，再建立关系 |

这个 skill 的目标不是让用户手动跑八个命令。正确体验应该是：用户完成接入和启用，之后 agent 在正常项目工作中主动维护计划生命周期。

## 真实产物

### 只读接入分析报告

`init` 会在正式治理前生成一份可读报告，帮助人判断哪些历史文件是当前计划、历史计划、弱匹配，或者需要隔离确认。

<p align="center">
  <img src="./assets/screenshot-adoption-report.png" alt="Plan adoption report screenshot" width="900" />
</p>

### Canonical registry

启用后，registry 会成为计划生命周期状态的可见事实来源。

<p align="center">
  <img src="./assets/screenshot-registry.png" alt="Plan registry screenshot" width="900" />
</p>

### 时间线视图

timeline report 从 registry 派生，让人和 agent 都能快速看清 active、blocked、closed、superseded、quarantine 文档。

<p align="center">
  <img src="./assets/screenshot-timeline.png" alt="Plan timeline report screenshot" width="900" />
</p>

示例 Markdown 输出见 [`examples/`](./examples/)。

## 适用边界与退出机制

不要把计划治理强行塞进每个仓库。

适合使用的场景：

- 仓库里有项目级计划文档
- 存在多份当前或历史计划
- 多个 agent 需要稳定的计划生命周期事实来源

不适合强制启用的场景：

- 只有 scratch notes
- 只有聊天记录
- 没有项目级计划文档

如果只想停止 `AGENTS.md` 的治理规则注入，同时保留治理历史：

```bash
python3 ~/.codex/skills/plan-governance/scripts/plan_governance.py remove-agents-block --repo-root "$(pwd)"
```

这只会移除 managed block，不会删除 registry、报告或配置文件，因为这些文件可能已经承载项目历史。

## 宿主兼容性

这个项目首先面向 Codex skills 和 Codex plugin 分发。

| 宿主 | 状态 | 说明 |
|---|---|---|
| Codex | 支持 | 使用 `SKILL.md`、本地脚本、`AGENTS.md` 和 `.codex-plugin/plugin.json` |
| 兼容 Codex skills 的宿主 | 可能支持 | 需要支持 skill 调用和本地脚本执行 |
| Claude Code 或其他 agent 宿主 | 需要适配 | 不能假设 `$plan-governance`、`AGENTS.md` 或 plugin metadata 自动生效 |

## 仓库结构

```text
plan-governance/
├── .codex-plugin/plugin.json
├── README.md
├── README.zh-CN.md
├── SKILL.md
├── agents/openai.yaml
├── assets/
├── examples/
├── references/
├── scripts/
├── skills/plan-governance/SKILL.md
└── templates/
```

`README.md` 是公开项目入口。`SKILL.md` 是 agent 执行指南。`skills/plan-governance/SKILL.md` 是 plugin 分发入口使用的包装层。

## Star History

这个仓库刚公开。下面的图会在项目有真实使用后变得有意义。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=cici-uu8/Plan-governance-Skill&type=Date&theme=dark" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=cici-uu8/Plan-governance-Skill&type=Date" />
  <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=cici-uu8/Plan-governance-Skill&type=Date" />
</picture>

## 许可证与贡献

本项目采用 [MIT License](./LICENSE)。

在公开 API 和分发路径稳定前，issue 和 PR 建议优先聚焦：

- 宿主兼容性问题
- 计划分类误判或漏判
- 生命周期治理边界案例
- README、examples 和安装说明清晰度
