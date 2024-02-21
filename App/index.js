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

    buttonContainer.innerHTML = ''

    if (currentScene == 'waitingToStart'){
        ws.send(JSON.stringify({'message': 'interface started'}))
    }
    textAnimation(props.text())
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