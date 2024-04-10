const GREEN  = "#6ef86e";
const RED    = "#ff4a4a";
const BLUE   = "#8cf1e9";
const YELLOW = "#ffd54a";
let data = {};
let doneWriting = false;
let username = "";

let ws_9050 = new WebSocket("ws://localhost:9050/websocketserver");
ws_9050.onopen = function() {
    console.log("[Pepper WS Server js]: Connection established");
    
    ws_9050.send(JSON.stringify({state: "ready"}));
};
ws_9050.onmessage = function(event) {
    humanMessage = JSON.parse(event.data);

    if (humanMessage.command != null) {
		if (humanMessage.command === "close") {
			ws_9050.close();
			console.log("[Pepper WS Server js]: Connection closed");
		}
        else if (humanMessage.command === "game") {
            console.log("[Pepper WS Server js]: Game started");
            window.location.href = "http://127.0.0.1:5500/App/15-puzzle/p15.html";
        }
	}
    if (humanMessage.scene != null) {
        if (humanMessage.scene === "waiting") {
            changeScene(waiting);
            data = {
                username: "",
                vote: 0
            };
            ws_9050.send(JSON.stringify({state: "waiting"}));
        }
        else if (humanMessage.scene === "backPersonScanned") {
            changeScene(backPersonScanned);
            ws_9050.send(JSON.stringify({say: backPersonScanned.text()}));
            setTimeout(() => ws_9050.send(JSON.stringify({state: "waiting2"})), 2000);
        }
        else if (humanMessage.scene === "frontPersonScanned") {
            changeScene(frontPersonScanned);
            ws_9050.send(JSON.stringify({say: frontPersonScanned.text()}));
            setTimeout(() => ws_9050.send(JSON.stringify({state: "person scanned"})), 2000);
        }
        else if (humanMessage.scene === "welcome") {
            changeScene(welcome);
            ws_9050.send(JSON.stringify({say: welcome.text()}));

        }
        else if (humanMessage.scene === "presentation") {
            changeScene(presentation);
            ws_9050.send(JSON.stringify({say: presentation.text()}));
        }
        else if (humanMessage.scene === "noGame") {
            changeScene(noGame);
            ws_9050.send(JSON.stringify({say: noGame.text()}));
        }
        else if (humanMessage.scene === "everPlayed") {
            changeScene(everPlayed);
            ws_9050.send(JSON.stringify({say: everPlayed.text()}));
        }
        else if (humanMessage.scene === "recap") {
            changeScene(recap);
            ws_9050.send(JSON.stringify({say: recap.text()}));
        }
        else if (humanMessage.scene === "rules") {
            changeScene(rules);
        }
    }
};

let waiting = {
    sceneName: "waiting",
    text: () => "Waiting for a human to play with me..."
};

let backPersonScanned = {
    sceneName: "backPersonScanned",
    text: () => "Hello! You are behind me. Please, come in front so that I can see you."
};

let frontPersonScanned = {
    sceneName: "frontPersonScanned",
    text: () => "Hi! I'm Pepper the N-Puzzle Buddy."
};

let welcome = {
    sceneName: "welcome",
    text: () => "Do you want to play a N-Puzzle match together with me?",
    buttons: ["Yes", "No"],
    colors: [GREEN, RED],
    listeners: [
        () => ws_9050.send(JSON.stringify({
            state: "person welcomed",
            buttonPressed: "Yes"
        })),
        () => ws_9050.send(JSON.stringify({
            state: "person welcomed",
            buttonPressed: "No"
        }))
    ]
};

let presentation = {
    sceneName: "presentation",
    text: () => "Great! Before starting, what's your name?",
    buttons: ["Submit"],
    colors: [BLUE],
    listeners: [
        () => {
            username = document.querySelector(".input-name").value;
            data.username = username;
            localStorage.setItem("N-PuzzleJS-userName", username);
            ws_9050.send(JSON.stringify({state: "person presented"}));
        }
    ]
};

let noGame = {
    sceneName: "noGame",
    text: () => "Oh, that's OK. Have a nice day then!",
    buttons: ["Thanks!"],
    colors: [BLUE],
    listeners: [
        () => window.location.href = "http://127.0.0.1:5500/App/index.html"
    ]
};

let everPlayed = {
    sceneName: "everPlayed",
    text: () => `${username}, have you ever played N-Puzzle?`,
    buttons: ["Yes", "No"],
    colors: [GREEN, RED],
    listeners: [
        () => ws_9050.send(JSON.stringify({
            state: "person played",
            buttonPressed: "Yes"
        })),
        () => ws_9050.send(JSON.stringify({
            state: "person played",
            buttonPressed: "No"
        }))
    ]
};

let recap = {
    sceneName: "recap",
    text: () => `Wonderful! Anyway ${username}, would you like a brief rule recap?`,
    buttons: ["Yes, let's recap the rules", "No, let's play the game"],
    colors: [GREEN, RED],
    listeners: [
        () => ws_9050.send(JSON.stringify({
            state: "rules recap",
            buttonPressed: "Yes"
        })),
        () => ws_9050.send(JSON.stringify({
            state: "rules recap",
            buttonPressed: "No"
        }))
    ]
};

let rules = {
    sceneName: "rules",
    text: () => `The game is made of a N by N grid filled with tiles numbered from 1 to N^2-1,
    and with a single empty cell. At the start, the tiles are randomly scrambled and
    the goal of the game is to slide them back in consecutive order with the empty tile on
    the bottom right.`,
    buttons: ["Got it! Let's play the game"],
    colors: [BLUE],
    listeners: [
        () => ws_9050.send(JSON.stringify({state: "got rules"})),
    ]
};

function textAnimation(sentence) {
    let target = document.querySelector('.welcome-text')
    let letterCount = 1

    let interval = window.setInterval(function() {
        if (letterCount === sentence.length+1) {
            window.clearInterval(interval)
            doneWriting = true
            return
        }
        target.innerHTML = sentence.substring(0, letterCount)
        letterCount += 1
    }, 100)
}

function changeScene(props, flag='') {
    currentScene = props.sceneName;

    let buttonContainer = document.querySelector('.button-container');
    if (buttonContainer.children.length != 0) {
        buttonContainer.classList.remove('buttons-in');
        buttonContainer.classList.add('buttons-out');
    }
    buttonContainer.innerHTML = "";

    if (currentScene === "waiting") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                clearInterval(interval);
            }
        }, 200);
    }
    else if (currentScene === "backPersonScanned") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                clearInterval(interval);
            }
        }, 200);
    }
    else if (currentScene === "frontPersonScanned") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                clearInterval(interval);
            }
        }, 200);
    }
    else if (currentScene === "welcome") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                for (let i = 0; i < props.buttons.length; ++i) {
                    let button = document.createElement("button");
    
                    button.classList.add("button");
                    button.innerHTML = props.buttons[i];
                    button.style.backgroundColor = props.colors[i];
                    button.addEventListener("click", props.listeners[i]);
    
                    buttonContainer.appendChild(button);
                    buttonContainer.classList.remove("buttons-out");
                    buttonContainer.classList.add("buttons-in");
                }

                clearInterval(interval);
            }
        }, 200);
    }
    else if (currentScene === "presentation") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                let textArea = document.createElement("input");

                textArea.classList.add("input-name");
                buttonContainer.appendChild(textArea);
                buttonContainer.classList.remove("buttons-out");
                buttonContainer.classList.add("buttons-in");

                let button = document.createElement("button");

                button.classList.add("button");
                button.innerHTML = props.buttons[0];
                button.style.backgroundColor = props.colors[0];
                button.addEventListener("click", props.listeners[0]);

                buttonContainer.appendChild(button);
                buttonContainer.classList.remove("buttons-out");
                buttonContainer.classList.add("buttons-in");

                clearInterval(interval);
            }
        }, 200);
    }
    else if (currentScene === "noGame") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                let button = document.createElement("button");

                button.classList.add("button");
                button.innerHTML = props.buttons[0];
                button.style.backgroundColor = props.colors[0];
                button.addEventListener("click", props.listeners[0]);

                buttonContainer.appendChild(button);
                buttonContainer.classList.remove("buttons-out");
                buttonContainer.classList.add("buttons-in");

                clearInterval(interval);
            }
        }, 200);
    }
    else if (currentScene === "everPlayed") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                for (let i = 0; i < props.buttons.length; ++i) {
                    let button = document.createElement("button");
    
                    button.classList.add("button");
                    button.innerHTML = props.buttons[i];
                    button.style.backgroundColor = props.colors[i];
                    button.addEventListener("click", props.listeners[i]);
    
                    buttonContainer.appendChild(button);
                    buttonContainer.classList.remove("buttons-out");
                    buttonContainer.classList.add("buttons-in");
                }

                clearInterval(interval);
            }
        }, 200);
    }
    else if (currentScene === "recap") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                for (let i = 0; i < props.buttons.length; ++i) {
                    let button = document.createElement("button");
    
                    button.classList.add("button");
                    button.innerHTML = props.buttons[i];
                    button.style.backgroundColor = props.colors[i];
                    button.addEventListener("click", props.listeners[i]);
    
                    buttonContainer.appendChild(button);
                    buttonContainer.classList.remove("buttons-out");
                    buttonContainer.classList.add("buttons-in");
                }

                clearInterval(interval);
            }
        }, 200);
    }
    else if (currentScene === "rules") {
        textAnimation(props.text());
        let interval = setInterval(() => {
            if (doneWriting) {
                doneWriting = false;
                let button = document.createElement("button");

                button.classList.add("button");
                button.innerHTML = props.buttons[0];
                button.style.backgroundColor = props.colors[0];
                button.addEventListener("click", props.listeners[0]);

                buttonContainer.appendChild(button);
                buttonContainer.classList.remove("buttons-out");
                buttonContainer.classList.add("buttons-in");

                clearInterval(interval);
            }
        }, 200);
    }
}
