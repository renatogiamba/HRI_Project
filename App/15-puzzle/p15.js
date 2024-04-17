var moves = 0;
var size = 3;
var board = null;
var emptyTile = null;

var ws_9020 = new WebSocket("ws://localhost:9020/websocketserver");
ws_9020.onopen = function() {
    console.log("[Pepper N-Puzzle WS Server js]: Connection established");
};
ws_9020.onmessage = function(event) {
    humanMessage = JSON.parse(event.data);

	if (humanMessage.command != null) {
		if (humanMessage.command === "close") {
			ws_9020.close();
			console.log("[Pepper N-Puzzle WS Server js]: Connection closed");
		}
	}
	else if (humanMessage.move != null) {
		const tileIdx = humanMessage.move;

        if (tileIdx == 0) return;
        
		let movingTile = document.getElementById(`tile-${tileIdx}`);
        movingTile.style.backgroundColor = "green";

		setTimeout(() => movingTile.style.backgroundColor = "#fff", 1000);
	}
};

function difficulty2size(difficulty) {
    if (difficulty === "Easy")
        return 3;
    else if (difficulty === "Medium")
        return 4;
    else if (difficulty === "Hard")
        return 5;
    else
        return 3;
}

function checkFinished() {
    return board.every(
        (elem, idx) => idx == board.length - 1 || board[idx] <= board[idx + 1]
    );
}

function onClickTile(event) {
    let tile = event.target;
    let iDiff = Math.abs(tile.i - emptyTile.i);
    let jDiff = Math.abs(tile.j - emptyTile.j);

    if (iDiff > 1 || jDiff > 1)
        return;
    else if (iDiff == 1 && jDiff > 0)
        return;
    else if (jDiff == 1 && iDiff > 0)
        return;
    else {
        [board[tile.pos], board[emptyTile.pos]] = [board[emptyTile.pos], board[tile.pos]];
        updateTiles();
        ++moves;

        let moveString = document.getElementById("moves");
        moveString.innerText = `Moves: ${moves}`;
    }
    if (checkFinished()) {
        ws_9020.send(JSON.stringify({"pose": "win"}));
        let game_over_dialog = document.getElementById("game-over");
        game_over_dialog.showModal();
    }
}

function createBoard() {
    board = null;
    board = new Int8Array(size * size);

    for (let i = 0; i < size * size; ++i) {
        board[i] = i + 1;
    }
}

function updateTiles() {
    let divBoard = document.querySelector(".board");
    divBoard.replaceChildren();

    for (let i = 0; i < size; ++i) {
        let row = document.createElement("div");
        row.className = "row";
        divBoard.appendChild(row);

        for (let j = 0; j < size; ++j) {
            let tile = document.createElement("button");
            let tileValue = board[j+i*size];
            let isEmptyTile = tileValue == board.length;

            tile.id = `tile-${tileValue}`;
            tile.pos = j + i * size;
            tile.i = i;
            tile.j = j;
            tile.innerText = isEmptyTile ?  "" : `${tileValue}`;
            tile.className = isEmptyTile ? "empty-tile" : "tile";
            tile.addEventListener("click", onClickTile);
            row.appendChild(tile);
            if (isEmptyTile){
                emptyTile = tile;
            }
        }
    }
}

function shuffle() {
    function countInversions(arr) {
        let numInvs = 0;

        for (let i = 0; i < arr.length - 1; ++i) {
            for (let j = i + 1; j < arr.length; ++j) {
                if (arr[i] != arr.length && arr[j] != arr.length && arr[i] > arr[j])
                    ++numInvs;
            }
        }

        return numInvs;
    }

    function isSolvable(puzzle) {
        const numInvs = countInversions(puzzle);

        if (puzzle.length & 1)
            return numInvs % 2 == 0;
        else {     
            const pos = puzzle.findLastIndex(elem => elem == puzzle.length) + 1;
            if (pos & 1)
                return numInvs % 2 == 0;
            else
                return numInvs % 2 == 1;
        }
    }

    let solvable = false;

    while (!solvable) {
        for(let i = 0; i < board.length; ++i) {
            const j = Math.floor(Math.random() * board.length);

            [board[i], board[j]] = [board[j], board[i]];
        }
        solvable = isSolvable(board);
    }
}

function startGame() {
    createBoard();
    shuffle();
    updateTiles();
    moves = 0;

    let moveString = document.getElementById("moves");
    moveString.innerText = `Moves: ${moves}`;
    document.getElementById("pepper-timeout").value = "";
}

let size_selector = document.getElementById("level");
size_selector.addEventListener("change", function() {
    size = parseInt(size_selector.value);

    if (document.querySelector(".board").childElementCount > 0) {
        document.querySelector(".board").replaceChildren();
        startGame();
    }
});

size = difficulty2size(localStorage.getItem("N-Puzzle-JS-difficulty") || "Easy");

let level_option = document.querySelector(`#level option[value="${size}"]`);
level_option.selected = true;

let username = document.getElementById("user");
username.innerHTML += " ";
username.innerHTML += (localStorage.getItem("N-Puzzle-JS-userName") || "GUEST");

let pepper_help_btn = document.getElementById("pepper-help");
pepper_help_btn.addEventListener("click", function(event) {
    let gameTileMatrix = [];

    for (let i = 0; i < size; ++i) {
        gameTileMatrix.push([]);

        for (let j = 0; j < size; ++j)
            gameTileMatrix[i].push(board[j + i * size]);
    }

    let timeout = parseInt(document.getElementById("pepper-timeout").value) || 0;

    ws_9020.send(JSON.stringify({"gameTileMatrix": gameTileMatrix, "timeout": timeout}));
})

let game_over_dialog = document.getElementById("game-over");
let game_over_dialog_play_btn = document.getElementById("game-over-play");
game_over_dialog_play_btn.addEventListener("click", function() {
    game_over_dialog.close();
    window.location.reload();
});
let game_over_dialog_survey_btn = document.getElementById("game-over-survey");
game_over_dialog_survey_btn.addEventListener("click", function() {
    game_over_dialog.close();
    window.location.href = "http://127.0.0.1:5500/App/survey.html";
});

let quit_btn = document.getElementById("quit");
quit_btn.addEventListener("click", function() {
    window.location.href = "http://127.0.0.1:5500/App/survey.html";
});

startGame();
