var moves = 0;
var size = 2;
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
	else if (humanMessage.action != null) {
		let button_idx = humanMessage.action === 0 ? 1 : 0;
		let button = game.buttonContainer.children[button_idx];

		button.color = "#ff0000";
		setTimeout(() => button.color = "#fff", 1000);
	}
};


function checkFinished() {
    return board.every((elem,idx)=>idx==board.length-1||board[idx]<=board[idx+1]);
}
function onClickTile(event){
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
        [board[tile.pos],board[emptyTile.pos]] = [board[emptyTile.pos],board[tile.pos]];
        updateTiles();
        ++moves;
        let moveString = document.getElementById('moves');
        moveString.innerText = `Moves: ${moves}`;
    }
    if (checkFinished())
        alert('DONEEE');
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
            tile.addEventListener("click",onClickTile);
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
            return numInvs%2 == 0;
        else {     
            let pos = puzzle.findLastIndex(elem => elem == puzzle.length);
            if ((pos+1) & 1)
                return numInvs%2 == 0;
            else
                return numInvs%2 == 1;
        }
    }
    let solvable = false;
    while (!solvable) {
        for( let i = 0; i < board.length; ++i) {
            const j = Math.floor(Math.random() * board.length);
            [board[i],board[j]]= [board[j],board[i]];
        }
        solvable = isSolvable(board);
    }
}

function startGame() {
    createBoard();
    shuffle();
    updateTiles();
    moves = 0;
}

let size_selector = document.getElementById("size");
size_selector.addEventListener("change", function() {
    size = parseInt(size_selector.value);

    if (document.querySelector(".board").childElementCount > 0) {
        document.querySelector(".board").replaceChildren();
        startGame();
    }
});
size = parseInt(size_selector.value);

startGame();