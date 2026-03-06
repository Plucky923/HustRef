# HustRef

HustRef 是一个将异构参考文献输入（BibTeX、EndNote/RIS、ACM Ref 纯文本）转换为华中科技大学硕士论文参考文献格式的工具。

项目目标是把格式转换流程拆成清晰的三段流水线：

`parse -> normalize -> format`

并提供：

- 命令行工具（CLI）
- 本地 Web 界面
- 可执行回归测试（含 `test.md` 场景）

## 1. 当前能力

### 支持的输入来源

- `bibtex`
- `endnote`（含 RIS）
- `acm_ref`（或 `plain` / `text`）
- `auto`（自动识别）

### 支持的输出文献类型

- 图书 `book`
- 期刊 `journal`
- 会议 `conference`
- 专利 `patent`
- 学位论文 `thesis`

### 已实现的核心规范

- 中英文作者格式化
- 作者人数规则：`<=6` 全列，`>6` 截断为前 6 人并追加 `等` / `et al`
- 页码范围规范化（`--` / `—` -> `-`）
- 输出行尾不带终止标点（如 `.`、`。`、`;`、`:`）
- 可选诊断信息：缺失必填字段、潜在格式风险

## 2. 快速开始

### 环境要求

- Python `3.10+`

### 安装（开发模式）

```bash
python3 -m pip install -e .
```

如果不安装，也可以直接通过 `PYTHONPATH=src` 运行模块。

### 30 秒体验

```bash
make cli
```

当前示例输出：

```text
E. S. Lein, M. J. Hawrylycz, N. Ao, M. Ayres, A. Bensinger, A. Bernard, et al. Genome-wide atlas of gene expression in the adult mouse brain. Nature, 2007, 445(7124): 168-176
```

## 3. CLI 使用

### 基本命令

```bash
hustref --source auto --input path/to/refs.txt
```

等价（未安装脚本时）：

```bash
PYTHONPATH=src python3 -m hustref.cli --source auto --input path/to/refs.txt
```

### 参数说明

| 参数 | 可选值 / 说明 |
| --- | --- |
| `--source` | `auto`(默认)、`bibtex`、`endnote`、`ris`、`acm_ref`、`plain`、`text` |
| `--input` | 输入文件路径；不传则从 `stdin` 读取 |
| `--json` | 输出规范化后的 JSON（非格式化参考文献文本） |
| `--diagnostics` | 输出诊断信息（缺失字段、warning 等） |
| `--strict` | 严格模式；含 `error` 的记录会被跳过，命令返回非 0 退出码 |

### 常见示例

1) 输出格式化参考文献（文本）

```bash
PYTHONPATH=src python3 -m hustref.cli \
  --source bibtex \
  --input tests/fixtures/sample.bib
```

2) 输出规范化 JSON

```bash
PYTHONPATH=src python3 -m hustref.cli \
  --source bibtex \
  --input tests/fixtures/sample.bib \
  --json
```

3) 开启严格模式（演示缺失 `year` 会返回退出码 `1`）

```bash
cat <<'EOF' | PYTHONPATH=src python3 -m hustref.cli --source bibtex --strict
@article{no_year,
  author = {John Smith},
  title = {A title without year},
  journal = {Journal of Missing Metadata}
}
EOF
echo $?
```

当输入缺失必填字段时，CLI 会在 stderr 输出错误并返回非 0 退出码。

## 4. 本地 Web 界面

### 启动

```bash
make web
```

默认地址：`http://127.0.0.1:8765`

### API（供前端调用）

- 路径：`POST /api/convert`
- 请求体：

```json
{
  "text": "@article{...}",
  "source": "auto",
  "strict": false
}
```

- 返回体关键字段：

```json
{
  "ok": true,
  "text": "...",
  "lines": ["..."],
  "entries": [],
  "summary": {
    "record_count": 1,
    "error_count": 0,
    "warning_count": 0
  }
}
```

## 5. Python API

```python
from hustref import convert_text, convert_to_json, convert_with_diagnostics

bib = """
@article{demo,
  author = {John Smith and Bob Jones},
  title = {Example},
  journal = {Journal of Tests},
  year = {2024},
  volume = {8},
  number = {3},
  pages = {10--20}
}
"""

lines = convert_text(bib, source_format="bibtex")
print(lines[0])

payload = convert_to_json(bib, source_format="bibtex")
print(payload)

report = convert_with_diagnostics(bib, source_format="bibtex", strict=True)
print(report.has_errors, report.formatted_lines())
```

## 6. 项目结构

```text
src/hustref/
  parsers/      # 输入适配：bibtex / endnote(ris) / acm_ref
  normalize/    # 作者、字段、标点后处理
  formatters/   # 按类型输出：book/journal/conference/patent/thesis
  pipeline.py   # parse -> normalize -> format + diagnostics
  validate.py   # 必填字段和 warning 校验
tests/
  unit/         # 单元测试
  fixtures/     # 测试输入样例
```

## 7. 开发与测试

```bash
# 全量单元测试
make test

# markdown 用例回归（test.md）
make test-md

# 基础静态检查（compile）
make lint

# CLI 冒烟测试
make cli
```

## 8. `test.md` 回归用例

`test.md` 支持以 Markdown 方式维护多源输入和期望输出，`make test` 会自动加载并执行校验。

用例结构与示例见：

- `docs/test-cases.md`

## 9. 设计说明文档

- 架构说明：`docs/architecture.md`
- Web 界面说明：`docs/web-ui.md`

## 10. 已知边界

- 解析器目前采用“无第三方依赖”的最小实现，复杂或非标准输入可能需要补充规则
- BibTeX / RIS 字段映射仍有可扩展空间（尤其会议时间、专利细分字段）
- 复杂自由文本（高噪声 ACM Ref 变体）可能需要人工复核
