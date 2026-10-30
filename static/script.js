// script.js
var button = document.getElementById("button_submit");
var error = document.getElementById("error");

button.addEventListener("click", function (event) {
    event.preventDefault(); 

    var name = document.getElementById("name").value;
    var description = document.getElementById("description").value;

    if (name === "" || description === "") {
        error.textContent = "Заполни все поля!";
        error.classList.remove("hidden");
        return;
    }

    error.classList.add("hidden");

    fetch("/create", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ name: name, description: description })
    })
    .then(function (response) {
        // response.url содержит конечный URL после редиректа (например, /todo/1)
        window.location.href = response.url; 
    })
    .catch(function (err) {
        error.textContent = "Ошибка: " + err;
        error.classList.remove("hidden");
    });
});