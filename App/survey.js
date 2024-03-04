let ws_9030 = new WebSocket("ws://localhost:9030/websocketserver");
ws_9030.onopen = function() {
    console.log("[Pepper Survey WS Server js]: Connection established");
};
ws_9030.onmessage = function(event) {
    humanMessage = JSON.parse(event.data);

    if (humanMessage.command != null) {
		if (humanMessage.command === "close") {
			ws_9030.close();
			console.log("[Pepper Survey WS Server js]: Connection closed");
		}
	}
};

document.getElementById("btn-submit").addEventListener("click", function(event) {
    let radioButtons = document.querySelectorAll(".star:checked");
    let textArea = document.getElementById("mini-review");
    ws_9030.send(JSON.stringify({
        state: "survey collected",
        interactionRate: parseInt(radioButtons[0].value),
        recommendationRate: parseInt(radioButtons[1].value),
        review: textArea.value
    }));

    let scene = document.querySelector(".scene");
    scene.innerHTML = "";
    let header = document.createElement("h2");
    header.innerHTML = "Thank you for your time!";
    scene.appendChild(header);

    let button = document.createElement("button");
    button.innerHTML = "Go to interaction!";
    button.addEventListener("click", () => {
        window.location.href = "http://127.0.0.1:5500/App/index.html";
    });
    button.style.margin = "80px 0 20px 0";
    scene.appendChild(button);

    document.querySelector("body").classList.add("thank-you");
    ws_9030.send(JSON.stringify({say: "Thank you for your time. Have a nice day!"}));
});
