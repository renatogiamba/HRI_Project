const GREEN = "#6ef86e";
const RED   = "#ff4a4a";
const BLUE = '#8cf1e9'
let data = {}

let ws_9050 = new WebSocket("ws://localhost:9050/websocketserver")
ws_9050.onopen = function() {
    console.log("Connection established")
    ws_9050.send("First Interaction")
}
ws_9050.onmessage = function(event) {
    console.log(event.data)
    humanMessage = JSON.parse(event.data)

    if (humanMessage.answer == "First Start"){
        changeScene(waitingToStart)
        data = {
            'username': '',
            'isNovice': true,
        }
    }
    else if (humanMessage.answer == "start"){
        changeScene(welcome)
    }
    else if (currentScene == 'welcome')
        if (humanMessage.answer == 'Yes'){
            changeScene(presentation)
        }
        else if (humanMessage == 'No'){
            changeScene(noGame)
        }
    else if (currentScene == 'presentation') {
        userName = humanMessage.answer
        changeScene(isNovice)
    }
    else if (currentScene == 'isNovice') {
        if (humanMessage.answer == 'Yes') {
            data.isNovice = false
            changeScene(playedBefore)
        }
        else if (humanMessage.answer == 'No') {
            data.isNovice = true
            changeScene(rules)
        }
    }
    else if (currentScene == 'playedBefore') {
        if (humanMessage.answer == 'Yes') {
            changeScene(rules)
        }
        else if (humanMessage.answer == 'No') {
            window.location.href = "http://127.0.0.1:5500/App/game/index.html"
        }
    }
    else if (currentScene == 'rules'){
        window.location.href = "http://127.0.0.1:5500/App/game/index.html"
    }
}


let welcome = {
    sceneName: "welcome",
    text: () => 'Hello Human! Do you want to play a BlackJack match?',
    buttons: ["Yes", "No"],
    colors: [GREEN, RED],
    listeners: [
        () => {
            ws_9050.send(JSON.stringify({"buttonPressed": "Yes"}))
            changeScene(presentation)
        },
        () => {
            ws_9050.send(JSON.stringify({"buttonPressed": "No"}))
            changeScene(noGame)
        }
    ]
}

let waitingToStart = {
    sceneName: "waitingToStart",
    text: () => "Waiting for a human to play with me...",
    buttons: [],
    colors: [],
    listeners: []
}

let presentation = {
    sceneName: 'presentation',
    text: () => `Great, I'm Pepper! What's your username?`,
    buttons: [],
    colors: [],
    listeners: [() => {
                    ws_9050.send(JSON.stringify({'buttonPressed': userName}))
                    data.username = userName
                    changeScene(isNovice)
                }
            ]
}

let noGame = {
    sceneName: 'noGame',
    text: () => 'Oh ok, that\'s a pity. I hope you have a nice day!',
    buttons: [],
    colors: [],
    listeners: []
}

let isNovice = {
    sceneName: 'isNovice',
    text: () => `${userName}, such a nice name! Have you ever played BlackJack?`,
    buttons: ['Yes', 'No'],
    colors: [GREEN, RED],
    listeners: [() => {
                    ws_9050.send(JSON.stringify({'buttonPressed': 'Yes'}))
                    data.isNovice = false
                    changeScene(playedBefore)
                },
                () => {
                    ws_9050.send(JSON.stringify({'buttonPressed': 'No'}))
                    data.isNovice = true
                    changeScene(rules)
                }
            ]
}

let playedBefore = {
    sceneName: 'playedBefore',
    text: () => 'Great! Do you want to be reminded the rules of the game?',
    buttons: ['Yes', 'No'],
    colors: [GREEN, RED],
    listeners: [() => {
                    ws_9050.send(JSON.stringify({'buttonPressed': 'Yes'}))
                    changeScene(rules)
                },
                () => {
                    ws_9050.send(JSON.stringify({'buttonPressed': 'No'}))
                    window.location.href = "http://127.0.0.1:5500/App/game/index.html"
                }
            ]
}

let rules = {
    sceneName: 'rules',
    text: () => 'The goal of the game is to...',
    buttons: ['Got it'],
    colors: [BLUE],
    listeners: [() => {
        ws_9050.send(JSON.stringify({'buttonPressed': 'Got it'}))
        window.location.href = "http://127.0.0.1:5500/App/game/index.html"
        
    }]
}

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
    currentScene = props.sceneName

    let buttonContainer = document.querySelector('.button-container')
    if (buttonContainer.children.length != 0) {
        buttonContainer.classList.remove('buttons-in')
        buttonContainer.classList.add('buttons-out')
    }

    buttonContainer.innerHTML = ''

    if (currentScene != "waitingToStart")
        ws_9050.send(JSON.stringify(
            {
                "vocabulary": props.buttons,
                "sentence": props.text(),
                "scene": props.sceneName
            }
        ))
    else {
        ws_9050.send(JSON.stringify({"message": "interface started"}))
    }

    textAnimation(props.text())

    if (currentScene == 'noGame') {
        ws_9050.send(JSON.stringify({'pepperSad': true, sentence: props.text()}))
        window.setTimeout(function() {
            console.log('resetting')
            changeScene(waitingToStart)
        }, 15000)
        return
    }

    let buttonInterval = window.setInterval(function() {
        if (doneWriting) {
            if (props.buttons.length == 0) {
                if (currentScene != 'waitingToStart') {
                    window.setTimeout(function() {
            
                        input = document.createElement('input')
                        input.classList.add('input-name')
                        input.addEventListener('keypress', function(e) {
                            if (e.key == 'Enter') {
                                userName = input.value
                                props.listeners[0]()
                            }
                        })
                        buttonContainer.appendChild(input)
            
                    }, 1000)
                }
            }
            else {
                window.setTimeout(function() {
                    if (flag == 'levelWon') {
                        console.log(data)
                        chosenLevel = data.levelsPlayed.at(-1)
                        console.log(chosenLevel)
                        for (let i=0; i<props.buttons.length; i++) {
                            let button = document.createElement('button')
                            button.classList.add('button')
                            button.innerHTML = props.buttons[i]
                            button.style.backgroundColor = props.colors[i]
                            button.addEventListener('click', props.listeners[i])
                            if (i == chosenLevel) {
                                let buttonDiv = document.createElement('div')
                                buttonDiv.classList.add('button-div')
                                let belowButton = document.createElement('div')
                                belowButton.innerHTML = 'Since you won the previous game, why not try a bigger challenge?'
                                belowButton.classList.add('below-button')

                                buttonDiv.appendChild(button)
                                buttonContainer.appendChild(buttonDiv)
                                button.style.maxWidth = `${button.offsetWidth}px`
                                belowButton.style.top = `${button.offsetHeight}px`
                                belowButton.style.left = `${-button.offsetWidth/2}px`
                                belowButton.style.width = `${button.offsetWidth*2}px`
                                buttonDiv.appendChild(belowButton)
                            }
                            else {
                                buttonContainer.appendChild(button)
                            }
                        }
                    }
                    else {
                        for (let i=0; i<props.buttons.length; i++) {
                            let button = document.createElement('button')
                            button.classList.add('button')
                            button.innerHTML = props.buttons[i]
                            button.style.backgroundColor = props.colors[i]
                            button.addEventListener('click', props.listeners[i])
                            buttonContainer.appendChild(button)
                        }
                    }
        
                    buttonContainer.classList.remove('buttons-out')
                    buttonContainer.classList.add('buttons-in')
            
                }, 200)
            }
            doneWriting = false
            window.clearInterval(buttonInterval)
        }
    })
}