import { shouldShowHint } from "./utils.js"
import { checkIfReadyToAnalyze } from "./run_analytics.js"
import { setRadioInputsEvents } from "./radio_inputs.js"

const cityNameInput = document.querySelector("#city-input")
const cityResults = document.querySelector("#city-results")
const mapFrame = document.querySelector("#map-frame")
const infoBlock = document.querySelector("#selected-city-info")
const selectedCityName = document.querySelector("#selected-city-name")

function updateCityInfo(cityData) {
    selectedCityName.textContent = `Вы выбрали город: ${cityData.name}`
    infoBlock.classList.remove('d-none')
    mapFrame.src = `https://www.google.com/maps?q=${cityData.lat},${cityData.lon}&z=10&output=embed`
}

function selectCity(city) {
    localStorage.setItem("isCitySelected", true)
    cityNameInput.value = city.name
    cityResults.innerHTML = ""
    updateCityInfo(city)
    shouldShowHint()

    fetch("/save_city_selection/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `city_id=${city.id}`
    }).then(() => checkIfReadyToAnalyze())
}

function createCityListElement(city) {
    const li = document.createElement("li")
    li.textContent = city.name
    li.classList.add("autocomplete-item")
    li.onclick = () => selectCity(city)
    cityResults.appendChild(li)
}

function addCitySearchInputEventListener() {
    cityNameInput.addEventListener("input", () => {
        const cityName = cityNameInput.value.charAt(0).toUpperCase() + cityNameInput.value.slice(1)

        if (cityName.length < 2) {
            cityResults.innerHTML = ""
            return
        }

        fetch(`/city_searching/?city_name=${cityName}`)
            .then(response => response.json())
            .then(data => {
                cityResults.innerHTML = ""
                data.forEach(city => createCityListElement(city))
            })
    })
}

function check_if_all_already_selected() {
    document.addEventListener("DOMContentLoaded", function () {
        const isCitySelected = localStorage.getItem("isCitySelected")

        const selectedRadio_storage = localStorage.getItem("selectedRadio")

        const startDate = localStorage.getItem("startDate")
        const endDate = localStorage.getItem("endDate")

        const startDateInput = document.querySelector('#period-input-start');
        const endDateInput = document.querySelector('#period-input-end');

        const selected_btn_at_start = document.querySelector(`input[name="analytics-option"][value="${selectedRadio_storage}"]`)

       if (selected_btn_at_start) {
            selected_btn_at_start.click();
        }

        if (startDate && endDate) {
            startDateInput.value = startDate;
            endDateInput.value = endDate;
        }

        if (isCitySelected && selected_btn_at_start) {
            checkIfReadyToAnalyze();
        }
    })
}

function main() {
    check_if_all_already_selected()
    addCitySearchInputEventListener()
    setRadioInputsEvents()
    shouldShowHint()
}

main()