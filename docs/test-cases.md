# test.md 用例格式

`test.md` 支持用 Markdown 维护可执行测试用例，运行 `make test` 时会自动加载并验证。

## 结构约定
- 用 `# Test ...` 开始一个测试用例
- 用以下标题声明输入来源（大小写不敏感）：
  - `## BibTex`
  - `## EndNote`
  - `## ACMRef`
- 可选：`## Expected`（期望输出，支持多行）
- 每个来源标题下方紧跟原始输入文本，直到下一个标题

## 示例
```markdown
# Test 1
## BibTex
@article{key,
  author = {Alice Smith and Bob Jones},
  title = {Example},
  journal = {Journal Name},
  year = {2024}
}

## EndNote
%0 Journal Article
%A Alice Smith
%T Example
%J Journal Name
%D 2024

## ACMRef
Alice Smith and Bob Jones. 2024. Example. Journal Name. 1, 1, Article 1.

## Expected
A. Smith, B. Jones. Example. Journal Name, 2024, 1(1): Article 1
```

## 校验规则
- 每个输入片段必须能成功解析至少 1 条记录
- 严格模式下不得有 `error` 级别问题（例如缺失 `year`）
- 输出行末不能有标点符号（符合 HUST 规则）
- 若存在 `Expected` 区块，则输出必须与其逐字一致
