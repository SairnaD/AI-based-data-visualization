let rawLabels = [];
let rawValues = [];
let chart;
let currentSettings = null;

/* ---------- AUTO SCALE ---------- */
function autoScale(values) {
    if (!values || values.length === 0) return { min: null, max: null };

    const min = Math.min(...values);
    const max = Math.max(...values);

    if (min === max) {
        return { min: min - 1, max: max + 1 };
    }

    const padding = (max - min) * 0.05;
    return {
        min: min - padding,
        max: max + padding
    };
}

/* ---------- GET SETTINGS FROM CONTROLS ---------- */
function getSettings() {
    return {
        topN: +document.getElementById("topN").value || null,
        sort: document.getElementById("sort").value || null,
        ymin: document.getElementById("ymin").value || null,
        ymax: document.getElementById("ymax").value || null,
        legend: document.getElementById("legend").checked,
        smooth: document.getElementById("smooth").checked,
        aggregation: currentSettings?.aggregation || null
    };
}

/* ---------- APPLY AI SETTINGS ---------- */
function applyAISettings(s) {
    if (!s.settings) return;

    document.getElementById("topN").value = s.settings.topN ?? 10;
    document.getElementById("sort").value = s.settings.sort ?? "desc";
    document.getElementById("legend").checked = s.settings.legend ?? true;
    document.getElementById("smooth").checked = s.settings.smooth ?? false;
    document.getElementById("ymin").value = s.settings.ymin ?? "";
    document.getElementById("ymax").value = s.settings.ymax ?? "";

    currentSettings = s.settings;
}

/* ---------- UPDATE CHART ---------- */
function updateChart() {
    if (!chart) return;
    if (chart.config.type === "scatter") return;

    const s = getSettings();

    let data = rawLabels.map((l, i) => ({
        label: l,
        value: rawValues[i]
    }));

    // --- SORT ---
    if (s.sort) {
        data.sort((a, b) =>
            s.sort === "desc"
                ? b.value - a.value
                : a.value - b.value
        );
    }

    // --- TOP N ---
    if (s.topN) {
        data = data.slice(0, s.topN);
    }

    const labels = data.map(d => d.label);
    const values = data.map(d => d.value);

    chart.data.labels = labels;
    chart.data.datasets[0].data = values;

    chart.options.plugins.legend.display = s.legend;

    if (chart.options.scales?.y) {
        if (!s.ymin && !s.ymax) {
            const scale = autoScale(values);
            chart.options.scales.y.min = scale.min;
            chart.options.scales.y.max = scale.max;
        } else {
            chart.options.scales.y.min = s.ymin;
            chart.options.scales.y.max = s.ymax;
        }
    }

    chart.data.datasets[0].tension = s.smooth ? 0.4 : 0;

    chart.update();
}

/* ---------- LOAD CHART ---------- */
function loadChart(s) {

    document.getElementById("status").innerText = "📊 Ielādē grafiku...";
    const controls = document.querySelector('.controls');
    controls.style.display = 'flex';
    document.getElementById("exportPNG").disabled = false;
    document.getElementById("exportPDF").disabled = false;

    applyAISettings(s);

    fetch(`/data?x=${s.x}&y=${s.y}&agg=${currentSettings?.aggregation || ""}`)
        .then(r => r.json())
        .then(d => {

            if (chart) chart.destroy();

            const typeMap = {
                "Line Chart": "line",
                "Area Chart": "line",
                "Bar Chart": "bar",
                "Pie Chart": "pie",
                "Doughnut Chart": "doughnut",
                "Polar Area Chart": "polarArea",
                "Radar Chart": "radar",
                "Scatter Chart": "scatter"
            };

            const chartType = typeMap[s.chart] || "bar";

            /* ---------- SCATTER ---------- */
            if (chartType === "scatter") {

                chart = new Chart(document.getElementById("chart"), {
                    type: "scatter",
                    data: {
                        datasets: [{
                            label: `${s.x} vs ${s.y}`,
                            data: d.points || [],
                            backgroundColor: "rgba(54, 162, 235, 0.5)",
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: currentSettings?.legend ?? false }
                        },
                        scales: {
                            x: {
                                title: { display: true, text: s.x }
                            },
                            y: {
                                title: { display: true, text: s.y }
                            }
                        }
                    }
                });

                document.getElementById("reason").innerText =
                    "🧠 AI skaidrojums:\n" + (s.reason || "");

                document.getElementById("status").innerText = "";
                return;
            }

            /* ---------- OTHER CHARTS ---------- */

            rawLabels = d.labels || [];
            rawValues = d.values || [];

            const scale = autoScale(rawValues);

            chart = new Chart(document.getElementById("chart"), {
                type: chartType,
                data: {
                    labels: rawLabels,
                    datasets: [{
                        label: s.y === "__count__" ? "Count" : s.y,
                        data: rawValues,
                        fill: s.chart === "Area Chart",
                        tension: currentSettings?.smooth ? 0.4 : 0,
                        borderWidth: 2,
                        pointRadius: chartType === "line" ? 3 : 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: currentSettings?.legend ?? true
                        },
                        zoom: {
                            pan: { enabled: true, mode: "x" },
                            zoom: { wheel: { enabled: true }, mode: "x" }
                        }
                    },
                    scales:
                        chartType === "pie" ||
                        chartType === "doughnut" ||
                        chartType === "polarArea"
                            ? {}
                            : {
                                  y: {
                                      min: currentSettings?.ymin || scale.min,
                                      max: currentSettings?.ymax || scale.max
                                  }
                              }
                }
            });

            updateChart();

            document.getElementById("reason").innerText =
                "🧠 AI skaidrojums:\n" +
                (s.reason || "• Automātiski ģenerēts skaidrojums");

            document.getElementById("status").innerText = "";
        });
}

/* ---------- UPLOAD ---------- */
function uploadFile(file) {

    if (!file) return;


    document.getElementById("status").innerText =
        "🧠 AI analizē datus...";
        


    const fd = new FormData();
    fd.append("file", file);


    fetch("/upload", {
        method: "POST",
        body: fd
    })
        .then(r => r.json())
        .then(data => {

            const c = document.getElementById("choices");
            c.innerHTML = "";

            data.forEach(s => {
                const b = document.createElement("button");
                b.innerText = s.chart + ": " + s.x + " vs " + s.y;
                b.onclick = () => loadChart(s);
                c.appendChild(b);
            });

            document.getElementById("status").innerText =
                "✅ Izvēlies vienu no AI ieteiktajiem grafikiem";
        });
}

/* ---------- DROPZONE ---------- */
const dz = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");

dz.onclick = () => fileInput.click();

fileInput.onchange = () => {
    if (fileInput.files.length)
        uploadFile(fileInput.files[0]);
};

dz.ondragover = e => {
    e.preventDefault();
    dz.classList.add("hover");
};

dz.ondragleave = () => dz.classList.remove("hover");

dz.ondrop = e => {
    e.preventDefault();
    dz.classList.remove("hover");
    if (e.dataTransfer.files.length)
        uploadFile(e.dataTransfer.files[0]);
};

/* ---------- AUTO UPDATE ON CONTROL CHANGE ---------- */
document
    .querySelectorAll("#topN, #sort, #ymin, #ymax, #legend, #smooth")
    .forEach(el => {
        el.addEventListener("change", updateChart);
    });


/* ---------- EXPORT PNG ---------- */

function exportPNG() {
    const canvas = document.getElementById("chart");
    const link = document.createElement("a");

    link.download = "chart.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
}

function exportPDF() {
    const { jsPDF } = window.jspdf;

    const canvas = document.getElementById("chart");
    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF({
        orientation: "landscape",
        unit: "px",
        format: [canvas.width, canvas.height]
    });

    pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height);
    pdf.save("chart.pdf");
}