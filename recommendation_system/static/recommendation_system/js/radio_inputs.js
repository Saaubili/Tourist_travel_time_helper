import { shouldShowHint, getWeeksFromRange } from "./utils.js"
import { checkIfReadyToAnalyze } from "./run_analytics.js"

let selectedRadio = null

function setSelectedRadio(value) {
    localStorage.setItem("selectedRadio", value)
    selectedRadio = value
}

function addRadioButtonsEventListener(btn) {
    setSelectedRadio(btn.value)
    shouldShowHint()
    fetch("/save_analytics_type/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `analytics_type=${btn.value}`
    }).then(() => checkIfReadyToAnalyze())
}

export function createErrorMessage(text, periodErrorDiv) {
    const periodError = document.createElement("p")
    periodError.textContent = `${text}`
    periodError.className = "period-error"
    periodErrorDiv.appendChild(periodError)
}

export function setRadioInputsEvents() {
    const periodErrorDiv = document.querySelector('#period-error-div');
    const bestWeekBtn = document.querySelector('#analytics-best-periods')
    const checkPeriodBtn = document.querySelector('#analytics-check-period')
    const analyzePeriodBtn = document.querySelector('#analyze-period-btn')
    const dateInput = document.querySelector('#period-input-div');

    bestWeekBtn.addEventListener("click", () => {
        addRadioButtonsEventListener(bestWeekBtn)
    })

    checkPeriodBtn.addEventListener("click", () => {
        periodErrorDiv.innerHTML = ""
        addRadioButtonsEventListener(checkPeriodBtn)
        dateInput.classList.remove("d-none")
    })

    analyzePeriodBtn.addEventListener("click", () => {
        periodErrorDiv.innerHTML = ""

        const startDate = document.querySelector('#period-input-start')
        const endDate = document.querySelector('#period-input-end')
        localStorage.setItem("startDate", startDate.value)
        localStorage.setItem("endDate", endDate.value)

        if (!startDate.value || !endDate.value) {
            createErrorMessage("Периоды не выбраны!", periodErrorDiv)
            return
        }
        if (startDate.value > endDate.value) {
            createErrorMessage("Конечная дата должна быть не раньше начальной!", periodErrorDiv)
            return
        }

        let periodsSet = getWeeksFromRange(new Date(startDate.value), new Date(endDate.value))
        if (periodsSet === "Too far ahead") {
            createErrorMessage("Слишком большой период, максимальное значение - 1 месяц!", periodErrorDiv)
            return
        }

        fetch("/save_chosen_periods/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `chosen_periods=${periodsSet}`
        })
            .then(() => {
                checkPeriodBtn.click()
            })
    })
}