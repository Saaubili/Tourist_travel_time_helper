const hintDiv = document.querySelector('#form-hint-div')

export function generate_shapes_for_plot(x0, x1, fillcolor) {
    return {
        type: 'rect',
        x0,
        y0: 0,
        x1,
        y1: 5,
        line: {
            color: 'rgba(0, 0, 0, 0.5)',
            width: 0.5
        },
        fillcolor
    }
}

export function generate_annotations_for_plot(xSpot, ySpot, text) {
    return {
        xref: 'x',
        yref: 'paper',
        x: xSpot,
        xanchor: 'bottom',
        y: ySpot,
        yanchor: 'bottom',
        text,
        showarrow: false
    }
}

export function getWeekDaysFromPeriod(period, locale = "ru-RU") {
    const start = new Date(2024, 0, 1)
    const weekStart = new Date(start)
    weekStart.setDate(start.getDate() + (period - 1) * 7)

    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 6)

    const options = { day: "numeric", month: "long" }

    return `${weekStart.toLocaleDateString(locale, options)} – ${weekEnd.toLocaleDateString(locale, options)}`
}

export function shouldShowHint() {
    hintDiv.innerHTML = ""

    const isCitySelected = localStorage.getItem("isCitySelected")
    const selectedRadio = localStorage.getItem("selectedRadio")

    if (!selectedRadio && isCitySelected) {
        hintDiv.style.display = "block"
        hintDiv.textContent = "Теперь выберете нужный режим"
    } else if (selectedRadio && !isCitySelected) {
        hintDiv.style.display = "block"
        hintDiv.textContent = "Теперь выберете город"
    } else {
        hintDiv.style.display = "none"
    }
}

export function determineColorByScore(alpha, score){
    if (score >= 4.3)
            return `rgba(16, 233, 9, ${alpha})`
        else if (score >= 3.7)
            return `rgba(167, 233, 14, ${alpha})`
        else if (score >= 2.8)
            return `rgba(221, 236, 12, ${alpha})`
        else if (score > 1.8)
            return `rgba(233, 138, 14, ${alpha})`
        else
            return `rgba(236, 25, 10, ${alpha})`
}