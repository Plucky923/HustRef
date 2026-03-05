const sourceSelect = document.getElementById("sourceSelect");
const strictCheckbox = document.getElementById("strictCheckbox");
const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");
const convertBtn = document.getElementById("convertBtn");
const sampleBtn = document.getElementById("sampleBtn");
const copyBtn = document.getElementById("copyBtn");
const diagnosticsList = document.getElementById("diagnosticsList");
const summaryBar = document.getElementById("summaryBar");

const SAMPLE_TEXT = `@article{yao2017,
  author = {Tao Yao and Jie Wan and Peilin Huang and Xin He and Feifei Wu and Chao Xie},
  title = {Building efficient key-value stores via a lightweight compaction tree},
  journal = {ACM Transactions on Storage},
  year = {2017},
  volume = {13},
  number = {4},
  pages = {1--28}
}`;

sampleBtn.addEventListener("click", () => {
    inputText.value = SAMPLE_TEXT;
    sourceSelect.value = "bibtex";
});

copyBtn.addEventListener("click", async () => {
    const text = outputText.value;
    if (!text.trim()) {
        summaryBar.textContent = "输出为空，暂无可复制内容。";
        return;
    }
    try {
        await navigator.clipboard.writeText(text);
        summaryBar.textContent = "已复制到剪贴板。";
    } catch (err) {
        summaryBar.textContent = "复制失败，请手动复制。";
    }
});

convertBtn.addEventListener("click", async () => {
    const payload = {
        text: inputText.value,
        source: sourceSelect.value,
        strict: strictCheckbox.checked
    };

    if (!payload.text.trim()) {
        outputText.value = "";
        renderDiagnostics([]);
        summaryBar.textContent = "请输入参考文献原始文本。";
        return;
    }

    setLoading(true);
    summaryBar.textContent = "正在转换...";

    try {
        const response = await fetch("/api/convert", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const result = await response.json();

        if (!response.ok || result.ok === false) {
            outputText.value = "";
            renderDiagnostics([]);
            summaryBar.textContent = result.error || "转换失败";
            return;
        }

        outputText.value = result.text || "";
        renderDiagnostics(result.entries || []);

        const summary = result.summary || {};
        summaryBar.textContent = `共 ${summary.record_count || 0} 条；错误 ${summary.error_count || 0}；警告 ${summary.warning_count || 0}`;
    } catch (err) {
        outputText.value = "";
        renderDiagnostics([]);
        summaryBar.textContent = "请求失败，请确认本地服务已启动。";
    } finally {
        setLoading(false);
    }
});

function setLoading(loading) {
    convertBtn.disabled = loading;
    convertBtn.textContent = loading ? "转换中..." : "转换";
}

function renderDiagnostics(entries) {
    diagnosticsList.innerHTML = "";

    if (!entries.length) {
        diagnosticsList.innerHTML = '<p class="hint">暂无诊断信息。</p>';
        return;
    }

    entries.forEach((entry, idx) => {
        const card = document.createElement("article");
        card.className = "diag-card";

        const title = document.createElement("h3");
        title.textContent = `记录 #${idx + 1} ${entry.skipped ? "(严格模式已跳过)" : ""}`;
        card.appendChild(title);

        const issues = entry.issues || [];
        if (!issues.length) {
            const ok = document.createElement("p");
            ok.className = "diag-item ok";
            ok.textContent = "无异常，已通过校验。";
            card.appendChild(ok);
        } else {
            issues.forEach((issue) => {
                const item = document.createElement("p");
                item.className = `diag-item ${issue.level || "warning"}`;
                item.textContent = `[${issue.level}] 字段 ${issue.field}: ${issue.message}`;
                card.appendChild(item);
            });
        }

        diagnosticsList.appendChild(card);
    });
}

