function prepareData(labels, values, settings) {
    let data = labels.map((l, i) => ({ label: l, value: values[i] }));

    if (settings.sort) {
        data.sort((a, b) =>
            settings.sort === "asc"
                ? a.value - b.value
                : b.value - a.value
        );
    }

    if (settings.topN) {
        data = data.slice(0, settings.topN);
    }

    return {
        labels: data.map(d => d.label),
        values: data.map(d => d.value)
    };
}

const chart = new Chart(ctx, {
    type: chartType,
    data: {
        labels,
        datasets: [{
            data: values,
            tension: settings.smooth ? 0.4 : 0,
            fill: chartType === "line" && settings.smooth
        }]
    },
    options: {
        plugins: {
            legend: { 
                display: settings.legend,
                labels: {
                    color: "#FFFFFF",
                    font: {
                        size: 14,
                        weight: "600"
                    }
                }
            },

            zoom: {
                zoom: {
                    wheel: {
                        enabled: true
                    },
                    pinch: {
                        enabled: true
                    },
                    mode: "x"
                },
                pan: {
                    enabled: true,
                    mode: "x"
                }
            }
        },

        scales: {
            x: {
                ticks: {
                    color: "#E6E8EF"
                },
                grid: {
                    color: "rgba(255,255,255,0.08)"
                }
            },

            y: {
                min: settings.ymin,
                max: settings.ymax,
                ticks: {
                    color: "#E6E8EF"
                },
                grid: {
                    color: "rgba(255,255,255,0.08)"
                }
            }
        }
    }
});

option = {
    legend: { show: settings.legend },
    yAxis: {
        min: settings.ymin,
        max: settings.ymax
    },
    series: [{
        smooth: settings.smooth,
        data: values
    }]
};

document.getElementById("chart").ondblclick = () => chart.resetZoom();
