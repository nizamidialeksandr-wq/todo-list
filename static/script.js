
var button = document.getElementById("button_submit");
var error = document.getElementById("error");
var toast = document.getElementById("toast");


button.addEventListener("click", function (event) {
    event.preventDefault(); // страница не перезагружается

    var name = document.getElementById("name").value;
    var description = document.getElementById("description").value;
    
    console.log("Имя:", name, "Описание:", description);

    // валидация: ищем первое незаполненное поле
    var empty = "";
    if (name === "") {
        empty = "Не заполнено поле: имя";
    } else if (description === "") {
        empty = "Не заполнено поле: описание";


    }
    
    if (empty !== "") {
        error.textContent =  empty;
        error.classList.remove("hidden");
        toast.classList.add("hidden");
        return; // дальше не идём, на сервер не отправляем
    }

    error.classList.add("hidden");

    // шлём на сервер те же данные, что отправил бы сам браузер
    fetch("/contact", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
            name: name,
            description: description,
        })
    })
        .then(function (response) {
            return response.text();
        })
        .then(function (text) {
            
            toast.classList.remove("hidden");
            toast.innerHTML = text;
            
            document.getElementById("name").value = "";
            document.getElementById("description").value = "";          

        })
        .catch(function (err) {
            error.textContent = "Не отправилось: " + err;
            error.classList.remove("hidden");
        });
            
});
