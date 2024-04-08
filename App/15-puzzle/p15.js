var clicks = 0;
var size = 2;
var board = null;
var emptyTile = null;

/*var board, zx, zy, clicks, possibles, clickCounter, oldzx = -1, oldzy = -1;
function getPossibles() {
    var ii, jj, cx = [-1, 0, 1, 0], cy = [0, -1, 0, 1];
    possibles = [];
    for( var i = 0; i < 4; i++ ) {
        ii = zx + cx[i]; jj = zy + cy[i];
        if( ii < 0 || ii > 3 || jj < 0 || jj > 3 ) continue;
        possibles.push( { x: ii, y: jj } );
    }
}
function updateBtns() {
    var b, v, id;
    for( var j = 0; j < 4; j++ ) {
        for( var i = 0; i < 4; i++ ) {
            id = "btn" + ( i + j * 4 );
            b = document.getElementById( id );
            v = board[i][j];
            if( v < 16 ) {
                b.innerHTML = ( "" + v );
                b.className = "button"
            }
            else {
                b.innerHTML = ( "" );
                b.className = "empty";
            }
        }
    }
    clickCounter.innerHTML = "Clicks: " + clicks;
}
function shuffle() {
    var v = 0, t; 
    do {
        getPossibles();
        while( true ) {
            t = possibles[Math.floor( Math.random() * possibles.length )];
            console.log( t.x, oldzx, t.y, oldzy )
            if( t.x != oldzx || t.y != oldzy ) break;
        }
        oldzx = zx; oldzy = zy;
        board[zx][zy] = board[t.x][t.y];
        zx = t.x; zy = t.y;
        board[zx][zy] = 16; 
    } while( ++v < 200 );
}
function restart() {
    shuffle();
    clicks = 0;
    updateBtns();
}
function checkFinished() {
    var a = 0;
    for( var j = 0; j < 4; j++ ) {
        for( var i = 0; i < 4; i++ ) {
            if( board[i][j] < a ) return false;
            a = board[i][j];
        }
    }
    return true;
}
function btnHandle( e ) {
    getPossibles();
    var c = e.target.i, r = e.target.j, p = -1;
    for( var i = 0; i < possibles.length; i++ ) {
        if( possibles[i].x == c && possibles[i].y == r ) {
            p = i;
            break;
        }
    }
    if( p > -1 ) {
        clicks++;
        var t = possibles[p];
        board[zx][zy] = board[t.x][t.y];
        zx = t.x; zy = t.y;
        board[zx][zy] = 16;
        updateBtns();
        if( checkFinished() ) {
            setTimeout(function(){ 
                alert( "WELL DONE!" );
                restart();
            }, 1);
        }
    }
}
function createBoard() {
    board = new Array( 4 );
    for( var i = 0; i < 4; i++ ) {
        board[i] = new Array( 4 );
    }
    for( var j = 0; j < 4; j++ ) {
        for( var i = 0; i < 4; i++ ) {
            board[i][j] = ( i + j * 4 ) + 1;
        }
    }
    zx = zy = 3; board[zx][zy] = 16;
}
function createBtns() {
    var b, d = document.createElement( "div" );
    d.className += "board";
    document.body.appendChild( d );
    for( var j = 0; j < 4; j++ ) {
        for( var i = 0; i < 4; i++ ) {
            b = document.createElement( "button" );
            b.id = "btn" + ( i + j * 4 );
            b.i = i; b.j = j;
            b.addEventListener( "click", btnHandle, false );
            b.appendChild( document.createTextNode( "" ) );
            d.appendChild( b );
        }
    }
    clickCounter = document.createElement( "p" );
    clickCounter.className += "txt";
    document.body.appendChild( clickCounter );
}
function start() {
    createBtns();
    createBoard();
    restart();
}*/

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
        //[tile.pos,posEmpty] = [posEmpty,tile.pos];
        //[tile.i,iEmpty]= [iEmpty,tile.i];
        //[tile.j,jEmpty]= [jEmpty,tile.j];
        updateTiles();
    }

}

function createTiles() {
    let board = document.querySelector(".board");

    for (let i = 0; i < size; ++i) {
        let row = document.createElement("div");
        row.className = "row";
        board.appendChild(row);

        for (let j = 0; j < size; ++j) {
            let tile = document.createElement("button");
            tile.id = `tile-${j + i * size + 1}`;
            tile.pos = j + i * size;
            tile.i = i;
            tile.j = j;
            tile.innerText = "";
            tile.className = "tile";
            tile.addEventListener("click",onClickTile);
            row.appendChild(tile);
        }
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
    for (let i = 0; i < size; ++i) {
        for (let j = 0; j < size; ++j) {
            let tile = document.getElementById(`tile-${j + i *size + 1}`);
            let tileValue = board[j + i * size];
            let isEmptyTile = tileValue == size * size;

            //tile.id = `tile-${tileValue}`;
            tile.pos = j + i *size;
            tile.i = i;
            tile.j = j;
            tile.className = isEmptyTile ? "empty-tile" : "tile";
            tile.innerText = isEmptyTile ? "": `${tileValue}`;
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
            if (pos & 1)
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
    createTiles();
    createBoard();
    shuffle();
    updateTiles();
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