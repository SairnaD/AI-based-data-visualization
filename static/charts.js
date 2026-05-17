function prepareData(labels, values, settings) {

    let data = labels.map((l, i) => ({
        label: l,
        value: values[i]
    }));

    /* ---------- SORT ---------- */

    if (settings.sort) {

        data.sort((a, b) =>
            settings.sort === "asc"
                ? a.value - b.value
                : b.value - a.value
        );
    }

    /* ---------- TOP N ---------- */

    if (settings.topN) {
        data = data.slice(0, settings.topN);
    }

    return {
        labels: data.map(d => d.label),
        values: data.map(d => d.value)
    };
}

/* ---------- REGISTER PLUGIN ---------- */

Chart.register(ChartDataLabels);

/* ---------- CHART ---------- */

const chart = new Chart(ctx, {

    type: chartType,

    data: {

        labels,

        datasets: [{

            data: values,

            tension: settings.smooth ? 0.4 : 0,

            fill:
                chartType === "line" &&
                settings.smooth,

            borderWidth: 2,

            pointRadius:
                chartType === "line"
                    ? 4
                    : 2
        }]
    },

    options: {

        responsive: true,

        plugins: {

            /* ---------- LEGEND ---------- */

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

            /* ---------- VALUE LABELS ---------- */

            datalabels: {

                display: function(context) {
                    if (context.chart.config.type === "scatter") {
                        return false;
                    }

                    if (!settings.showValues) {
                        return false;
                    }

                    return true;
                },


                color: "#FFFFFF",

                font: {
                    weight: "bold",
                    size: 11
                },

                formatter: function(value, context) {

                    const type =
                        context.chart.config.type;

                    /* PIE / DOUGHNUT / POLAR */

                    if (
                        type === "pie" ||
                        type === "doughnut" ||
                        type === "polarArea"
                    ) {

                        const data =
                            context.chart
                                .data
                                .datasets[0]
                                .data;

                        const total =
                            data.reduce(
                                (a, b) => a + b,
                                0
                            );

                        const percentage =
                            (
                                (value / total) * 100
                            ).toFixed(1);

                        return percentage + "%";
                    }

                    /* SCATTER */

                    if (type === "scatter") {

                        if (!settings.showValues) {
                            return null;
                        }

                        return `(${value.x}, ${value.y})`;
                    }

                    /* OTHER CHARTS */

                    return value;
                },

                anchor:
                    chartType === "pie" ||
                    chartType === "doughnut"
                        ? "center"
                        : "end",

                align:
                    chartType === "pie" ||
                    chartType === "doughnut"
                        ? "center"
                        : "top",

                clamp: true
            },

            /* ---------- ZOOM ---------- */

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

        /* ---------- SCALES ---------- */

        scales:

            chartType === "pie" ||
            chartType === "doughnut" ||
            chartType === "polarArea"

                ? {}

                : {

                    x: {

                        ticks: {
                            color: "#E6E8EF"
                        },

                        grid: {
                            color:
                                "rgba(255,255,255,0.08)"
                        }
                    },

                    y: {

                        min: settings.ymin,

                        max: settings.ymax,

                        ticks: {
                            color: "#E6E8EF"
                        },

                        grid: {
                            color:
                                "rgba(255,255,255,0.08)"
                        }
                    }
                }
    }
});

/* ---------- EXTRA OPTIONS ---------- */

option = {

    legend: {
        show: settings.legend
    },

    yAxis: {

        min: settings.ymin,

        max: settings.ymax
    },

    series: [{

        smooth: settings.smooth,

        data: values
    }]
};

/* ---------- DOUBLE CLICK RESET ---------- */

document
    .getElementById("chart")
    .ondblclick = () => chart.resetZoom();