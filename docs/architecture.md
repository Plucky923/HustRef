# HustRef 架构设计（第 1 阶段落地）

## 1. 技术选型
- 核心逻辑：Python 3.10+
  - 原因：字符串处理、正则表达式能力强，适合 BibTeX/RIS/纯文本解析
  - 当前实现保持“无第三方依赖”，后续可按需引入 `bibtexparser`、`rispy`
- 前端展示：建议 React 或 Vue（本仓库当前先完成后端/核心库）
  - 前端通过 API 或 WebAssembly/CLI 调用 `parse -> normalize -> format` 流程

## 2. 三层流水线
- Parse：`src/hustref/parsers/`
  - `bibtex.py`、`endnote.py`(RIS)、`acm_ref.py`（纯文本）
- Normalize：`src/hustref/normalize/`
  - `authors.py`（中英文作者、缩写、人数截断）
  - `fields.py`（年份/页码/空白清洗）
  - `punctuation.py`（去末尾标点）
- Format：`src/hustref/formatters/`
  - 按类型分文件：`book`、`journal`、`conference`、`patent`、`thesis`
  - `router.py` 根据 `type` 路由

流程严格为：`parse -> normalize -> format`，不混入文件 I/O。

附加校验层：`src/hustref/validate.py`
- 用于检查必填字段缺失，输出 `error/warning` 诊断信息
- 可在 CLI 中通过 `--diagnostics` 和 `--strict` 启用

## 3. 标准中间格式（ReferenceRecord）
统一数据结构定义在 `src/hustref/models.py`，核心字段包括：
- `type`: `book|journal|conference|patent|thesis`
- `language`: `zh|en`
- `authors`: `[{first_name,last_name,raw}]`
- 其余标准字段：`title, journal_name, conference_name, year, volume, issue, pages, publisher, location ...`

该结构可由 `convert_to_json()` 输出为 JSON，便于前端调试和规则对照。

## 4. 当前能力边界
- 已支持：BibTeX、RIS、ACM 风格纯文本的最小可用解析
- 已支持：中英文检测、英文名缩写、`<=6` 全列出、`>6` 使用 `等`/`et al`
- 已支持：五类文献格式化与“末尾无标点”规则
- 已支持：本地 Web 双栏界面（输入/输出、复制、诊断提示）
- 待增强：
  - BibTeX/RIS 字段映射更完整（会议时间、专利文献类型等）
  - ACM 纯文本复杂变体解析（可引入 LLM 兜底）
  - 前端错误提示可细化为字段级高亮定位

## 5. 周计划映射（与你的方案对齐）
- 第 1 周：架构、模型、模块边界（已落地）
- 第 2-3 周：增强解析器覆盖率与异常处理
- 第 4-5 周：补齐 HUST 细则和类型细分模板
- 第 6 周：前端交互（输入源切换、一键复制、错误提示）（已落地本地版）
- 第 7 周：50+ Ground Truth 回归测试与开源发布
