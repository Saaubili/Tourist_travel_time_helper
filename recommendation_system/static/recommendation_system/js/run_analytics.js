import { createBarPlot } from "./create_plot.js"
import { getWeekDaysFromPeriod } from "./utils.js"
import { determineColorByScore } from "./utils.js"

const weeksInfoDiv = document.querySelector("#weeks-info-div")

export function checkIfReadyToAnalyze() {
    fetch("/check_if_ready_to_analyze/")
        .then(r => r.json())
        .then(data => {
            if (!data || !data.best_weeks.length) return
            if (data.status === "error") return

            weeksInfoDiv.classList.remove("d-none")

            const topWeeksList = document.querySelector("#top-weeks-list")
            topWeeksList.innerHTML = ""

            data.best_weeks.forEach(week => {
                const li = document.createElement("li")
                li.style.backgroundColor = determineColorByScore(0.2, week.score)
                li.classList.add("top-weeks-list-item")
                li.textContent = `Период: ${getWeekDaysFromPeriod(week.period)} — оценка ${week.score}`
                topWeeksList.appendChild(li)
            })

            createBarPlot(data)
        })
}