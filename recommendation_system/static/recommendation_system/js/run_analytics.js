import { createBarPlot } from "./create_plot.js"
import { getWeekDaysFromPeriod } from "./utils.js"
import { determineColorByScore } from "./utils.js"

const weeksInfoDiv = document.querySelector("#weeks-info-div")
const chosenPeriodsDiv = document.querySelector('#chosen-periods-div');

export function checkIfReadyToAnalyze() {
    fetch("/check_if_ready_to_analyze/")
        .then(response => response.json())
        .then(data => {
            if (!data || data.status === "error")
                return
            if (data.best_weeks) {
                if (data.best_weeks.length !== 0) {
                    weeksInfoDiv.classList.remove("d-none")
                    chosenPeriodsDiv.classList.add("d-none")

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
                }
            }
            else if (data.period_score) {
                let score = data.period_score

                weeksInfoDiv.classList.add("d-none")
                chosenPeriodsDiv.classList.remove("d-none")

                const scoreEl = document.querySelector('#chosen-periods-score');
                scoreEl.style.backgroundColor = determineColorByScore(0.2, score)

                scoreEl.textContent = score

                createBarPlot(data)
            }
        })
}