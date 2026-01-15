const cityNameInput = document.querySelector("#city-input");
const cityResults = document.querySelector("#city-results");
const mapFrame = document.querySelector("#map-frame");
const infoBlock = document.querySelector("#selected-city-info")
const selectedCityName = document.querySelector("#selected-city-name")
let selectedRadio = null
const radioButtons = document.querySelectorAll('input[name="analytics-option"]');
const hintDiv = document.querySelector('#form-hint-div')
let isCitySelected = false


function updateCityInfo(cityData) {
    selectedCityName.textContent = `Вы выбрали город: ${cityData.name}`;
    infoBlock.classList.remove('d-none');
    mapFrame.src = `https://www.google.com/maps?q=${cityData.lat},${cityData.lon}&z=10&output=embed`;
}


function selectCity(city) {
    localStorage.setItem("isCitySelected", true);
    isCitySelected = true
    cityNameInput.value = city.name;
    cityResults.innerHTML = "";
    updateCityInfo(city)
    shouldShowHint()
    fetch("/save_city_selection/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `city_id=${city.id}`
    })
        .then(() => checkIfReadyToAnalyze())
}

function shouldShowHint() {
    hintDiv.innerHTML = ""
    const arrow = document.createElement("div");
    arrow.classList.add("hint-arrow");
    if (!selectedRadio && localStorage.getItem("isCitySelected")) {
        hintDiv.style.display = "block"
        hintDiv.textContent = "Теперь выберете нужный режим"
        arrow.classList.add("right");
        hintDiv.appendChild(arrow);
    }
    else if (selectedRadio && !localStorage.getItem("isCitySelected")) {
        hintDiv.style.display = "block"
        hintDiv.textContent = "Теперь выберете город"
        arrow.classList.add("left");
        hintDiv.appendChild(arrow);
    }
    else {
        hintDiv.style.display = "none"
    }
}

function createCityListElement(city) {
    const li = document.createElement("li");
    li.textContent = city.name;
    li.classList.add("autocomplete-item");
    li.onclick = () => {
        selectCity(city)
    };
    cityResults.appendChild(li);
}

function addCitySearchInputEventListener() {
    cityNameInput.addEventListener("input", () => {
        const cityName = cityNameInput.value.charAt(0).toUpperCase() + cityNameInput.value.slice(1);
        if (cityName.length < 2) {
            cityResults.innerHTML = "";
            return;
        }

        fetch(`/city_searching/?city_name=${cityName}`)
            .then(cityInfoResponse => cityInfoResponse.json())
            .then(cityData => {
                cityResults.innerHTML = "";
                cityData.forEach(city => {
                    createCityListElement(city)
                });
            });
    })
}

function addRadioButtonsEventListener() {
    radioButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            selectedRadio = btn
            shouldShowHint()
            fetch("/save_analytics_type/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `analytics_type=${btn.value}`
            })
                .then(() => checkIfReadyToAnalyze())
        })
    });
}


function checkIfReadyToAnalyze() {
    fetch("/check_if_ready_to_analyze/")
        .then(response => response.json())
        .then(analyticsData => {
            if (!analyticsData || !analyticsData.best_weeks.length) {
                console.warn("Нет данных для анализа");
                return;
            }
            if (analyticsData.status === "error") {
                console.error(analyticsData.message)
                return
            }
            const topWeeksList = document.querySelector("#top-weeks-list");
            topWeeksList.innerHTML = "";

            analyticsData.best_weeks.forEach(week => {
                const li = document.createElement("li");
                get_dates = getWeekDaysFromPeriod(week.period)
                li.textContent = `Период: ${get_dates} — оценка ${week.score}`;
                topWeeksList.appendChild(li);
            });
            createBarPlot(analyticsData)
        })
}


function createBarPlot(analyticsData) {
    let periods = []
    let scores = []
    let colors = []

    analyticsData.graph_data.forEach(week =>{
        score = week.score
        periods.push(week.period)
        scores.push(score)
        if (score >= 4.5)
            colors.push("rgba(16, 233, 9, 1)")
        else if (score >= 3.8)
            colors.push("rgba(167, 233, 14, 1)")
        else if (score >= 2.8)
            colors.push("rgba(221, 236, 12, 1)")
        else if (score > 1.8)
            colors.push("rgba(233, 138, 14, 1)")
        else
            colors.push("rgba(236, 25, 10, 1)")
    })

    const barData = [{
        x: periods,
        y: scores,
        type: 'bar',
        marker:{color: colors},
        name: 'Оценки недель'
    }];

    const layout = {
        title: "Оценка всех недель",
        xaxis: { title: "Неделя" },
        yaxis: { title: "Оценка (0–5)", range: [0, 5] }
    };

    Plotly.newPlot(
        'weekly-scores-plot', barData, layout, { responsive: true }
    );
}

function getWeekDaysFromPeriod(period, locale = "ru-RU") {
    const start = new Date(2024, 0, 1);
    const weekStart = new Date(start);
    weekStart.setDate(start.getDate() + (period - 1) * 7);

    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);

    const options = { day: "numeric", month: "long" };

    return `${weekStart.toLocaleDateString(locale, options)} – ${weekEnd.toLocaleDateString(locale, options)}`;
}



function main() {
    addCitySearchInputEventListener()
    shouldShowHint()
    addRadioButtonsEventListener()
};


main()