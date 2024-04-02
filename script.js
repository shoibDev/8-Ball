import { getFormData } from './setup.js';

var FormData = (function() {
    return getFormData();
})();

var currentPlayer = 'player1'; 
var switchPlayer = true; 
let firstSink = 0;

let playerOneBalls = []
let playerTwoBalls = []

let sideHigh = "x"
let sideLow = "y"

let high = 15;
let blackBall = 8;
let low = 7;

var active = true; // Game is active when true

function displaySVGsInSequence(svgContents) {
    const svgContainer = $('#svgContainer');
    let index = 0;

    function displayNextSVG() {
        if (index < svgContents.length) {
            svgContainer.html(svgContents[index]);
            index++;
            setTimeout(displayNextSVG, 10);
        }
    }
    displayNextSVG();
    active = true;
}

function updatePlayerUI(currentPlayer) {
    if (currentPlayer === 'player1') {
        $('#playerOneContainer').addClass('activePlayer').removeClass('inactivePlayer');
        $('#playerTwoContainer').addClass('inactivePlayer').removeClass('activePlayer');
    } else if (currentPlayer === 'player2') {
        $('#playerTwoContainer').addClass('activePlayer').removeClass('inactivePlayer');
        $('#playerOneContainer').addClass('inactivePlayer').removeClass('activePlayer');
    }
}

function updatePlayerBalls(balls_sunk) {
    const ballNumbers = balls_sunk.map(ballInfo => ballInfo[0]);

    if (firstSink === 0 && ballNumbers.length > 0) {
        assignSides(ballNumbers[0]);
        firstSink = 1; // Update firstSink to indicate sides have been assigned
    }

    ballNumbers.forEach(ballNumber => {
        if (ballNumber >= 1 && ballNumber <= 7) {
            if (sideLow === 'player1') {
                playerOneBalls.push(ballNumber);
            } else {
                playerTwoBalls.push(ballNumber);
            }
        } else if (ballNumber >= 9 && ballNumber <= 15) {
            if (sideHigh === 'player1') {
                playerOneBalls.push(ballNumber);
            } else {
                playerTwoBalls.push(ballNumber);
            }
        }
    });
}

function assignSides(firstBallNumber) {
    let playerOneLabel = $('#labelOne');
    let playerTwoLabel = $('#labelTwo');

    if (firstBallNumber >= 1 && firstBallNumber <= 7) {
        if (currentPlayer === 'player1') {
            sideLow = 'player1';
            sideHigh = 'player2';
            playerOneLabel.text('Low (1-7)');
            playerTwoLabel.text('High (9-15)');
        } else {
            sideLow = 'player2';
            sideHigh = 'player1';
            playerOneLabel.text('High (9-15)');
            playerTwoLabel.text('Low (1-7)');
        }
    } else if (firstBallNumber >= 9 && firstBallNumber <= 15) {
        if (currentPlayer === 'player1') {
            sideHigh = 'player1';
            sideLow = 'player2';
            playerOneLabel.text('High (9-15)');
            playerTwoLabel.text('Low (1-7)');
        } else {
            sideHigh = 'player2';
            sideLow = 'player1';
            playerOneLabel.text('Low (1-7)');
            playerTwoLabel.text('High (9-15)');
        }
    }
}

function checkForWin() {
    if (sideLow === 'player1' && !playerOneBalls.includes(blackBall) && playerOneBalls.length === low) {
        return playerOneBalls.includes(blackBall) ? false : FormData.player1Name;
    } else if (sideLow === 'player2' && !playerTwoBalls.includes(blackBall) && playerTwoBalls.length === low) {
        return playerTwoBalls.includes(blackBall) ? false : FormData.player2Name;
    } else if (sideHigh === 'player1' && !playerOneBalls.includes(blackBall) && playerOneBalls.length === high) {
        return playerOneBalls.includes(blackBall) ? false : FormData.player1Name;
    } else if (sideHigh === 'player2' && !playerTwoBalls.includes(blackBall) && playerTwoBalls.length === high) {
        return playerTwoBalls.includes(blackBall) ? false : FormData.player2Name;
    }
    return false;
}

function updateGameAfterShot(balls_sunk) {
    let sunkOwnBall = false;
    let sunkOpponentBall = false;
    let sunkBlackBall = false;

    balls_sunk.forEach(([ballNumber, _]) => {
        if (ballNumber === blackBall) {
            sunkBlackBall = true;
        } else if ((sideLow === currentPlayer && ballNumber <= 7) || (sideHigh === currentPlayer && ballNumber >= 9 && ballNumber <= 15)) {
            sunkOwnBall = true;
        } else {
            sunkOpponentBall = true;
        }
    });

    if (sunkBlackBall) {
        const winner = checkForWin();
        if (winner) {
          
            $("#modalText").text(winner + " wins the game!");
            $("#gameModal").css("display", "block");
            active = false;
        } else {
          
            $("#modalText").text(currentPlayer + " loses by sinking the 8-ball prematurely.");
            $("#gameModal").css("display", "block");
            active = false;
        }
    } else {
        if (sunkOpponentBall) {
            switchPlayer = false;
        }
        if (!sunkOwnBall) {
            switchPlayer = true;
        }
        if(sunkOwnBall){
            switchPlayer = false;
        }
    }
}


$(document).ready(function() {

    var currentPlayer = Math.random() < 0.5 ? 'player1' : 'player2';
    updatePlayerUI(currentPlayer);

    // Set player names from FormData
    $('#playerOneName').text(FormData.player1Name || "Player 1");
    $('#playerTwoName').text(FormData.player2Name || "Player 2");

    let isDragging = false;
    let line = null;
    let startX, startY;

    $('#svgContainer').on('mousedown', 'circle[fill="WHITE"]', function(event) {
        event.preventDefault();
        
        const svg = document.querySelector('#svgContainer svg');
        startX = parseFloat($(this).attr('cx'));
        startY = parseFloat($(this).attr('cy'));
    
        isDragging = true;
        line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', startX); // Start from the ball's center
        line.setAttribute('y1', startY); // Start from the ball's center
        line.setAttribute('x2', startX); // Initially, line is a point
        line.setAttribute('y2', startY); // Initially, line is a point
        line.setAttribute('stroke', 'black');
        line.setAttribute('stroke-width', 5); // Thick line for visibility
        svg.appendChild(line);
    });

    $(document).on('mousemove', function(event) {
        if (!isDragging || !line) return;
    
        const svg = document.querySelector('#svgContainer svg');
        const pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());
    
        // Instead of inverting the direction, directly use the mouse position
        line.setAttribute('x2', svgP.x);
        line.setAttribute('y2', svgP.y);
    });

    $(document).on('mouseup', function(event) {
        if (!isDragging) return;
        isDragging = false;
    
        const svg = document.querySelector('#svgContainer svg');
        const pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());

        // Calculate deltas for the shot based on the inverted line
        const deltaX = startX - (svgP.x - startX) - startX;
        const deltaY = startY - (svgP.y - startY) - startY;
    
        if (line) {
            line.remove();
            line = null;
        }
    
        var currentPlayerKey = currentPlayer + "Name";
        var data = {
            playerName: FormData[currentPlayerKey], 
            gameName: FormData.gameName, 
            x: deltaX,
            y: deltaY
        };

        if(active){
            $.post("/shot", data)
                .done(function(response) {
                    switchPlayer = true
                    active = false
                
                    if (response.svgContents) {
                        displaySVGsInSequence(response.svgContents);
                    }

                    if (response.balls_sunk && response.balls_sunk.length > 0) {
                        
                        updatePlayerBalls(response.balls_sunk);
                        updateGameAfterShot(response.balls_sunk);
                    }
                    if (switchPlayer) {
                        currentPlayer = currentPlayer === 'player1' ? 'player2' : 'player1';
            
                        updatePlayerUI(currentPlayer); // Update the UI to reflect the current player
                    }
                })
                .fail(function(jqXHR, textStatus, errorThrown) {
                    console.error("Error submitting shot:", textStatus, errorThrown);
                });
        }
    });

    $('#modalClose').click(function() {
        $('#gameModal').hide();
    });
    
    $('#reloadPage').click(function() {
        window.location.reload(); // Reloads the current page
    });
});
