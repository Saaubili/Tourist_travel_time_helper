const input = document.querySelector("#city-input");
const cityResults = document.querySelector("#city-results");
const hidden = document.querySelector("#city-id");
const mapFrame = document.querySelector("#map-frame");
const infoBlock = document.querySelector("#selected-city-info")
const selectedCityName = document.querySelector("#selected-city-name")

function updateCityInfo(cityData) {
    selectedCityName.textContent = `Вы выбрали город: ${cityData.name}`;
    infoBlock.classList.remove('d-none');
    mapFrame.src = `https://www.google.com/maps?q=${cityData.lat},${cityData.lon}&z=10&output=embed`;
}

input.addEventListener("input", () => {
    const cityName = input.value.charAt(0).toUpperCase() + input.value.slice(1);
    if (cityName.length < 2) {
        cityResults.innerHTML = "";
        infoBlock.classList.add('d-none')
        return;
    }

    fetch(`/city_searching/?city_name=${cityName}`)
        .then(cityInfoResponse => cityInfoResponse.json())
        .then(cityData => {
            cityResults.innerHTML = "";
            cityData.forEach(city => {
                const li = document.createElement("li");
                li.textContent = city.name;
                li.classList.add("autocomplete-item");
                li.onclick = () => {
                    input.value = city.name;
                    hidden.value = city.id;
                    cityResults.innerHTML = "";
                    fetch("/save_city_selection/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                        },
                        body: `city_id=${city.id}`
                    })
                        .then(res => res.json())
                        .then(data => {
                            updateCityInfo(data.city);
                        });
                };
                cityResults.appendChild(li);
            });
        });
});