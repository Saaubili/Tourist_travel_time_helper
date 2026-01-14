const cityNameInput = document.querySelector("#city-input");
const cityResults = document.querySelector("#city-results");
const mapFrame = document.querySelector("#map-frame");
const infoBlock = document.querySelector("#selected-city-info")
const selectedCityName = document.querySelector("#selected-city-name")
const selectedRadio = null
const radioButtons = document.querySelector('input[name="analytics-option"]');
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
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: `city_id=${city.id}`
    })
}

function shouldShowHint() {
    if (!selectedRadio && localStorage.getItem("isCitySelected")) {
        hintDiv.style.display = "block"
        hintDiv.textContent = "Теперь выберете нужный режим"
    }
    else if (selectedRadio && !localStorage.getItem("isCitySelected")) {
        hintDiv.style.display = "block"
        hintDiv.textContent = "Теперь выберете город"
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
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: `analytics_type=${btn.value}`
            })
        })
    });
}


function main() {
    addCitySearchInputEventListener()
    shouldShowHint()
};


main()