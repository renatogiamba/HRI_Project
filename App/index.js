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

    if (currentScene != 'waitingToStart') {
        ws.send(JSON.stringify({'vocabulary': props.buttons, 'sentence': props.text(), 'scene': props.sceneName}))
    }
    else {
        ws.send(JSON.stringify({'message': 'interface started'}))
    }

    textAnimation(props.text())

    if (currentScene == 'noGame') {
        ws.send(JSON.stringify({'pepperSad': true, sentence: props.text()}))
        window.setTimeout(function() {
            console.log('resetting')
            changeScene(waitingToStart)
        }, 15000)
        return
    }

    // Keeps cheking every 0.2 seconds wether the whole sentence has been written to let the buttons appear
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
                    // If the player won the previous game, the button for the next level is suggested
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

function main() {
    ws = new WebSocket('ws://localhost:9050/websocketserver')
    ws.onopen = function() {
        console.log('Connection established')
        ws.send('First Interaction')
    }
    ws.onmessage = function(event){
        console.log(event.data)
        humanMessage = JSON.parse(event.data)

        if(humanMessage.answer == 'First Start'){
            changeScene(waitingToStart)
        }
        else if (humanMessage.answer == 'start'){
            changeScene(welcome)
        }
    }

    let green = '#6ef86e'
    let red = '#ff4a4a'

    let welcome = {
        sceneName: 'welcome',
        text: () => 'Hello Human! Do you want to play a BlackJack match?',
        buttons: ['Yes', 'No'],
        colors: [green, red],
        listeners: [() => {
                        ws.send(JSON.stringify({'buttonPressed': 'Yes'}))
                        changeScene(presentation)
                    },
                    () => {
                        ws.send(JSON.stringify({'buttonPressed': 'No'}))
                        changeScene(noGame)
                    }
                ]
    }

    waitingToStart = {
       sceneName: 'waitingToStart',
       text: () => 'Waiting for a human to play with me...',
       buttons: [],
       colors: [],
       listeners: []
    }
}

main()