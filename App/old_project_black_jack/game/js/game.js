var stage;
var game;
var player;
var bank;

let ws_9020 = new WebSocket("ws://localhost:9020/websocketserver");
ws_9020.onopen = function() {
    console.log("[Pepper BlackJack WS Server js]: Connection established");
};
ws_9020.onmessage = function(event) {
    humanMessage = JSON.parse(event.data);

	if (humanMessage.command != null) {
		if (humanMessage.command === "close") {
			ws_9020.close();
			console.log("[Pepper BlackJack WS Server js]: Connection closed");
		}
	}
	else if (humanMessage.action != null) {
		let button_idx = humanMessage.action === 0 ? 4 : 3;
		let button = game.buttonContainer.children[button_idx];

		button.color = "#ff0000";
		setTimeout(() => button.color = "#fff", 1000);
	}
};

function init() {
	stage = new createjs.Stage("canvas");

	game = {
		inProgress: false,
		chipsValue: {
			blue: 500,
			black: 100,
			green: 25,
			red: 5,
			white: 1
		},
		dealt: {
			blue: 0,
			black: 0,
			green: 0,
			red: 0,
			white: 0
		},
		message: {
			text: null,

			init: function() {
				this.text = new createjs.Text(messages.bet, "40px Arial", "#fff");
				this.text.x = 850;
				this.text.y = 0;
				stage.addChild(this.text);
			}
		},
		deck: [],
		buttons: [
			new Button("New Game", "#fff", 100, -490, () => game.reset()),
			new Button("Quit Game", "#fff", 100, -430, () => game.exit()),
			new Button("Ask Pepper", "#fff", 100, 40, () => player.askPepper()),
			new Button("Hit", "#fff", 100, 100, () => player.hit()),
			new Button("Stand", "#fff", 200, 100, () => player.stand()),
			new Button("Go", "#fff", 935, -430, () => game.go())
		],
		buttonContainer: null,
		dealtChipsContainer: null,

		_alert: function(msg) {
			let alertText = new createjs.Text(msg.msg, "30px Arial", "orange");
			alertText.x = msg.x || 745;
			alertText.y = 120;
			stage.addChild(alertText);
			createjs.Tween.get(alertText)
				.wait(1000)
				.to({alpha: 0}, 1000, createjs.Ease.getPowInOut(1));
		},

		balanceChips: function(funds) {
			let chips = {
				blue: 0,
				black: 0,
				green: 0,
				red: 0,
				white: 0
			};

			while (funds !== 0) {
				Object.keys(chips).reverse().forEach(function (chip) {
					let chipValue = game.chipsValue[chip];
					if (funds >= chipValue) {
						funds -= chipValue;
						++(chips[chip]);
					}
				});
			}

			return chips;
		},

		resetChips: function() {
			Object.keys(this.dealt).forEach(color => this.dealt[color] = 0);
		},

		buildDeck: function() {
			for (let suit of suits) {
				for (let rank = 2; rank < 11; ++rank)
					this.deck.push(new Card(suit, rank));
				for (let rank of ["J", "Q", "K", "A"])
					this.deck.push(new Card(suit, rank));
			}
		},

		addButtons: function() {
			this.buttonContainer = new createjs.Container();
			this.buttonContainer.x = -70;
			this.buttonContainer.y = 500;
			stage.addChild(this.buttonContainer);

			this.buttons.forEach(function(btn) {
				let button = new createjs.Text(btn.text, "30px Arial", btn.color);
				button.x = btn.x;
				button.y = btn.y;

				let hit = new createjs.Shape();
				hit.graphics.beginFill("#000").drawRect(
					0, 0, button.getMeasuredWidth(), button.getMeasuredHeight()
				);
				button.hitArea = hit;

				button.alpha = 0.7;
				button.addEventListener("mouseover", function(event) {
					button.alpha = 1.;
					button.cursor = "Pointer";
				});
				button.addEventListener("mouseout", function (event) {
					button.alpha = 0.7;
				});
				button.addEventListener("click", btn.onclick);
				game.buttonContainer.addChild(button);
			});
		},

		addChips: function() {
			if (!player.chipsContainer) {
				player.chipsContainer = new createjs.Container();
				player.chipsContainer.x = 600;
				player.chipsContainer.y = 500;
				
				this.dealtChipsContainer = new createjs.Container();
				stage.addChild(player.chipsContainer, this.dealtChipsContainer);
			} else {
				player.chipsContainer.removeAllChildren();
			}
			
			let base = {x: 100, y: 45};
			for (let chipColor in player.chips) {
				for (let i = 0; i < player.chips[chipColor]; ++i) {
					let chipImg = new createjs.Bitmap(imgs.chips.get(chipColor, "side"));
					chipImg.x = base.x;
					chipImg.y = base.y;
					chipImg.color = chipColor;
					chipImg.dealt = false;
					player.chipsContainer.addChild(chipImg);

					base.y -= 10;
					if (i === player.chips[chipColor] - 1) {
						chipImg.cursor = "Pointer";
						chipImg.addEventListener("mouseover", function(event) {
							event.currentTarget.scaleX = 1.1;
							event.currentTarget.scaleY = 1.1;
							event.currentTarget.y -= 8;
						});
						chipImg.addEventListener("mouseout", function(event) {
							event.currentTarget.scaleX = 1.;
							event.currentTarget.scaleY = 1.;
							event.currentTarget.y += 8;
						});
						chipImg.addEventListener(
							"click", event => game.throwChip(event.currentTarget)
						);
					}
				}
				base.y = 45;
				base.x += 75;
			}
		},

		throwChip: function(chip) {
			if (chip.dealt || game.isProgress) return;
			chip.dealt = true;
			player.chipsContainer.removeChildAt(player.chipsContainer.getChildIndex(chip));
			chip.x = chip.x + player.chipsContainer.x;
			chip.y = chip.y + player.chipsContainer.y;
			game.dealtChipsContainer.addChild(chip);
			createjs.Tween
				.get(chip)
				.to(
					{x: rand(350, 675) , y: rand(190, 350)}, 750,
					createjs.Ease.getPowInOut(1)
				);
			
			let color = chip.color;

			player.dealt += this.chipsValue[color];
			player.chips[color] -= 1;
			player.funds -= this.chipsValue[color];
			player.fundsText.update();
			this.dealt[color] += 1;
			this.addChips();
		},

		displayCard: function(card, owner) {
			let cardImg = new createjs.Bitmap(
				card.hidden ?
				imgs.cards.path + imgs.cards.back.red + '.' + imgs.cards.ext :
				imgs.cards.get(card.suit, card.value)
			);

			if (owner === "bank") {
				cardImg.x = 0;
				cardImg.y = -100;
				bank.cardsContainer.addChild(cardImg);
				createjs.Tween
					.get(cardImg)
					.to(
						{x: 50 * bank.deck.length, y: 100}, 750,
						createjs.Ease.getPowInOut(1)
					);
				bank.cardsContainer.x -= 20;
			} else if (owner === "player") {
				cardImg.x = 100;
				cardImg.y = -400;
				player.cardsContainer.addChild(cardImg);
				createjs.Tween
					.get(cardImg)
					.to(
						{x: 50 * player.deck.length, y: 100}, 750,
						createjs.Ease.getPowInOut(1)
					);
				player.cardsContainer.x -= 20;
				if(this.deckValue(player.deck) > 21)
					player.lose();
			}
		},

		distributeCard: function(to, hidden = false) {
			let idx = rand(0, this.deck.length - 1);
			let card = this.deck[idx];
			card.hidden = hidden;

			if (to === "player")
				player.deck.push(card);
			else if (to === "bank")
				bank.deck.push(card);
			this.deck.splice(idx, 1);
			this.displayCard(card, to);
		},

		deckValue: function(deck) {
			const accumulate = (partial, card) => {
				if (card.value >= 2 && card.value < 11)
					return partial + card.value;
				else if (['J', 'Q', 'K'].includes(card.value))
					return partial + 10;
				else if (card.value === 'A')
					return partial + 1;
			};

			const usableAce = (deck) => {
				return deck.map(card => card.value)
				.includes('A') && deck.reduce(accumulate, 0) + 10 <= 21;
			};

			let total = deck.reduce(accumulate, 0);

			return usableAce(deck) ? total + 10 : total;
		},

		start: function() {
			player.name.text = new createjs.Text(player.name.value, "30px Arial", "#fff");
			player.name.text.center();
			player.name.text.y = 600;
			stage.addChild(player.name.text);

			this.message.init();
			player.fundsText.init();
			//this.buildDeck();
			this.addButtons();
			this.addChips();
		},

		over: function() {
			//['userName', 'chips', 'funds'].forEach(v => localStorage.removeItem('BlackJackJs-' + v));
			stage.removeAllChildren();

			let gameOverText = new createjs.Text("Game Over", "50px Arial", "#fff");
			gameOverText.center(1, 1);

			let replayText = new createjs.Text("Replay", "30px Arial", "#fff");
			replayText.center(1);
			replayText.y = 400;

			let hit = new createjs.Shape();
			hit.graphics.beginFill("#000").drawRect(
				0, 0, replayText.getMeasuredWidth(), replayText.getMeasuredHeight()
			);

			replayText.hitArea = hit;
			replayText.alpha = 0.7;
			replayText.cursor = "Pointer";
			replayText.addEventListener("mouseover", function(event) {
				replayText.alpha = 1;
			});
			replayText.addEventListener("mouseout", event => replayText.alpha = 0.7);
			replayText.addEventListener("click", () => window.location.reload());
			stage.addChild(gameOverText, replayText);
		},

		end: function() {
			this.dealtChipsContainer.removeAllChildren();
			this.inProgress = false;
			player.betted = false;
			player.deck = [];
			player.blackjack = false;
			player.dealt = 0;
			player.cardsContainer.removeAllChildren();
			player.chips = this.balanceChips(player.funds);
			this.resetChips();
			this.addChips();
			//player.store();
			bank.deck = [];
			bank.blackjack = false;
			bank.cardsContainer.removeAllChildren();
			this.message.text.text = messages.bet;
		},

		new: function() {
			bank.cardsContainer = new createjs.Container();
			bank.cardsContainer.x = 450;
			bank.cardsContainer.y = -100;
			stage.addChild(bank.cardsContainer);
			player.cardsContainer = new createjs.Container();
			player.cardsContainer.x = 450;
			player.cardsContainer.y = 300;
			stage.addChild(player.cardsContainer);

			game.distributeCard("player");
			setTimeout(() => {
				game.distributeCard("player");
				setTimeout(() => {
					game.distributeCard("bank");
					setTimeout(() => {
						game.distributeCard("bank", true);
					}, 750);
				}, 750);
			}, 750);
		},

		startScreen: function() {
			stage.enableMouseOver(10);
			createjs.Ticker.addEventListener("tick", tick);
			createjs.Ticker.setFPS(30);

			player.name.value = localStorage.getItem("BlackJackJs-userName") || "Player";
			player.name.value = localStorage.getItem("BlackJackJs-userName");
			player.funds = localStorage.getItem("BlackJackJs-funds");
			player.chips = JSON.parse(localStorage.getItem("BlackJackJs-chips"));
			this.start();
		},

		reset: function() {
			window.location.reload();
		},

		exit: function() {
			//this.end();
			window.location.href = "http://127.0.0.1:5500/App/survey.html";
		},

		go: function() {
			if (player.dealt && !this.inProgress) {
				this.inProgress = true;
				player.betted = true;
				this.message.text.text = "";
				this.deck = [];
				this.buildDeck();
				this.new();
			}
			else if (!player.dealt)
				this._alert(messages.warning.bet);
		},

		check: function() {
			let playerScore = this.deckValue(player.deck);
			let bankScore = this.deckValue(bank.deck);

			player.blackjack = playerScore === 21 && player.deck.length === 2;
			bank.blackjack = bankScore === 21 && bank.deck.length === 2;
			if (bank.blackjack && player.blackjack)
				return player.draw();
			else if (bank.blackjack)
				return player.lose();
			else if (player.blackjack)
				return player.win();

			if (bankScore > 21)
				player.win();
			else if (bankScore >= 17 && bankScore <= 21) {
				if (playerScore > bankScore)
					player.win();
				else if (playerScore < bankScore)
					player.lose();
				else
					player.draw();
			}
		}
	};

	player = {
		name: {
			value: "Player",
			text: false
		},
		chips: game.balanceChips(1000),
		chipsContainer: null,
		funds: 1000,
		fundsText: {
			text: null,

			init: function() {
				this.text = new createjs.Text(player.funds, "30px Arial", "#fff");
				this.text.x = 880;
				this.text.y = 590;
				stage.addChild(this.text);
			},

			update: function() {
				this.text.text = player.funds;
			}
		},
		dealt: 0,
		betted: false,
		deck: [],
		cardsContainer: null,
		blackjack: false,

		hit: function() {
			if (!this.betted)
				return game._alert(messages.warning.bet);
			game.distributeCard("player");
		},

		stand: function() {
			if (!this.betted)
				return game._alert(messages.warning.bet);
			game.inProgress = true;
			bank.play();
		},

		win: function() {
			game.message.text.text = messages.win;
			setTimeout(function() {
				player.funds += player.blackjack ? player.dealt * 3 : player.dealt * 2;
				game.end();
				player.fundsText.update();
			}, 2000);
			ws_9020.send(JSON.stringify({pose: "win"}));
		},

		lose: function() {
			game.message.text.text = messages.lose;
			setTimeout(function() {
				if (player.funds <= 0)
					return game.over();
				game.end();
			}, 2000);
			ws_9020.send(JSON.stringify({pose: "lose"}));
		},

		draw: function() {
			game.message.text.text = messages.draw;
			setTimeout(function() {
				player.funds += player.dealt;
				game.end();
				player.fundsText.update();
			}, 2000);
		},

		askPepper: function() {
			if (player.deck.length === 0 || bank.deck.length === 0)
				return;
			playerCardValues = player.deck.map(card => card.value);
			bankCardValues = bank.deck.filter(card => !card.hidden).map(card => card.value);
			ws_9020.send(JSON.stringify({gameState: {
				playerCardValues: playerCardValues,
				bankCardValues: bankCardValues
			}}));
		}
	};

	bank = {
		deck: [],
		cardsContainer: null,
		blackjack: false,

		play: function() {
			this.cardsContainer.children[1].image.src = imgs.cards.get(
				this.deck[1].suit, this.deck[1].value
			);

			let total = game.deckValue(this.deck);
			if (total < 17) {
				game.distributeCard('bank');
				if (game.deckValue(this.deck) < 17)
					setTimeout(() => bank.play(), 1000);
				else
					game.check();
			}
			else
				game.check();
		}
	};

	function tick() {
		stage.update();
	}

	localStorage.setItem(
		"BlackJackJs-userName",
		localStorage.getItem("BlackJackJs-userName") || player.name.value
	);
	localStorage.setItem("BlackJackJs-funds", "1000");
	localStorage.setItem("BlackJackJs-chips", JSON.stringify(player.chips));
	game.startScreen();
}
