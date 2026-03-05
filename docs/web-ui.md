# 本地 Web 界面使用说明

## 启动方式
- 命令：`make web`
- 默认地址：`http://127.0.0.1:8765`

等价命令：
`PYTHONPATH=src python3 -m hustref.webapp --host 127.0.0.1 --port 8765`

## 已实现功能
- 左侧输入区：
  - 输入格式下拉（自动检测 / BibTeX / EndNote / ACM Ref）
  - 严格模式开关
  - 输入文本框
  - 转换按钮、填充示例按钮
- 右侧输出区：
  - 格式化结果显示
  - 一键复制到剪贴板
- 底部诊断区：
  - 每条记录的 `error/warning` 展示
  - 严格模式被跳过的记录提示
  - 缺失字段（例如 `year`）可直接定位

## API 约定
- 路径：`POST /api/convert`
- 请求体：
```json
{
  "text": "...",
  "source": "auto",
  "strict": false
}
```
- 返回体（核心字段）：
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

