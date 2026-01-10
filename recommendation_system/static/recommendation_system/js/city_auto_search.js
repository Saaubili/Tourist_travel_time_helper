const input = document.querySelector("#city-input");
const results = document.querySelector("#city-results");
const hidden = document.querySelector("#city-id");

input.addEventListener("input", () => {
    const cityName = input.value.charAt(0).toUpperCase() + input.value.slice(1);
    if (cityName.length < 2) {
        results.innerHTML = "";
        return;
    }


    fetch(`/city_searching/?city_name=${cityName}`)
        .then(res => res.json())
        .then(data => {
            results.innerHTML = "";

            data.forEach(city => {
                const li = document.createElement("li");
                li.textContent = `${city.name}`;
                li.classList.add("autocomplete-item");

                li.onclick = () => {
                    input.value = city.name;
                    hidden.value = city.id;
                    results.innerHTML = "";
                };

                results.appendChild(li);
            });
        });
})