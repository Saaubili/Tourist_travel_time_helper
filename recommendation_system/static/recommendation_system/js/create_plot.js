import { generate_shapes_for_plot } from "./utils.js"
import { generate_annotations_for_plot } from "./utils.js"
import { getWeekDaysFromPeriod } from "./utils.js"
import { determineColorByScore } from "./utils.js"

export function createBarPlot(analyticsData) {
    const plotDiv = document.querySelector("#plot-div")
    plotDiv.classList.remove("d-none")
    let periods = []
    let scores = []
    let colors = []

    analyticsData.graph_data.forEach(week => {
        let score = week.score
        periods.push(getWeekDaysFromPeriod(week.period))
        scores.push(score)
        colors.push(determineColorByScore(1, score))
    })

    const barData = [{
        x: periods,
        y: scores,
        type: 'bar',
        marker: { color: colors },
    }]

    const layout = {
        title: "Оценка всех недель",
        xaxis: { showticklabels: false },
        yaxis: { title: "Оценка (0–5)", range: [0, 5] },
        annotations: [
            generate_annotations_for_plot(5, -0.25, "Зима"),
            generate_annotations_for_plot(15, -0.25, "Весна"),
            generate_annotations_for_plot(28, -0.25, "Лето"),
            generate_annotations_for_plot(41, -0.25, "Осень"),
            generate_annotations_for_plot(51, -0.25, "Зима"),
        ],
        shapes: [
            generate_shapes_for_plot(-1, 9, `rgba(49, 101, 170, 0.05)`),
            generate_shapes_for_plot(9, 22, `rgba(189, 192, 12, 0.05)`),
            generate_shapes_for_plot(22, 35, `rgba(31, 196, 25, 0.05)`),
            generate_shapes_for_plot(35, 48, `rgba(184, 77, 16, 0.05)`),
            generate_shapes_for_plot(48, 53, `rgba(49, 101, 170, 0.05)`)
        ]
    }

    const config = {
        responsive: true,
        displayModeBar: false,
    }

    Plotly.react(
        'weekly-scores-plot', barData, layout, config
    )
}