import { shouldShowHint } from "./utils.js"
import { checkIfReadyToAnalyze } from "./run_analytics.js"

const cityNameInput = document.querySelector("#city-input")
const cityResults = document.querySelector("#city-results")
const mapFrame = document.querySelector("#map-frame")
const infoBlock = document.querySelector("#selected-city-info")
const selectedCityName = document.querySelector("#selected-city-name")
const radioButtons = document.querySelectorAll('input[name="analytics-option"]')
let selectedRadio = null

function setSelectedRadio(value) {
    localStorage.setItem("selectedRadio", value)
    selectedRadio = value
}

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

function addRadioButtonsEventListener() {
    radioButtons.forEach(btn => {
        btn.addEventListener("click", () => {
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
        })
    })
}

function main() {
    check_if_all_already_selected()
    addCitySearchInputEventListener()
    addRadioButtonsEventListener()
    shouldShowHint()
}

function check_if_all_already_selected() {
    document.addEventListener("DOMContentLoaded", function () {
        const isCitySelected = localStorage.getItem("isCitySelected")
        const selectedRadio_storage = localStorage.getItem("selectedRadio")
        document.querySelector(`input[name="analytics-option"][value="${selectedRadio_storage}"]`).checked = true

        if (isCitySelected && selectedRadio_storage) {
            checkIfReadyToAnalyze()
        }
    });
}

main()