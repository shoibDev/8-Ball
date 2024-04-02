import { getFormData } from './setup.js';

var FormData = (function() {
    return getFormData();
})();


var currentPlayer = 'player1'; // Default to 'player1' or 'player2'
var switchPlayer = true; // Keeps track of whether to switch player after a shot
let firstSink = 0;

let playerOneBalls = []
let playerTwoBalls = []

let sideHigh = "x"
let sideLow = "y"

let high = 15;
let blackBall = 8;
let low = 7;

function displaySVGsInSequence(svgContents) {
    const svgContainer = $('#svgContainer');
    let index = 0;

    function displayNextSVG() {
        if (index < svgContents.length) {
            svgContainer.html(svgContents[index]);
            index++;
            setTimeout(displayNextSVG, 10); // Wait for 1 second before displaying the next SVG
        }
    }

    displayNextSVG();
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
    // Extract only the ball numbers from the tuples
    const ballNumbers = balls_sunk.map(ballInfo => ballInfo[0]);
    console.log(ballNumbers)

    if (firstSink === 0 && ballNumbers.length > 0) {
        // Assign sides based on the first ball sunk
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
        return playerOneBalls.includes(blackBall) ? false : 'player1';
    } else if (sideLow === 'player2' && !playerTwoBalls.includes(blackBall) && playerTwoBalls.length === low) {
        return playerTwoBalls.includes(blackBall) ? false : 'player2';
    } else if (sideHigh === 'player1' && !playerOneBalls.includes(blackBall) && playerOneBalls.length === high) {
        return playerOneBalls.includes(blackBall) ? false : 'player1';
    } else if (sideHigh === 'player2' && !playerTwoBalls.includes(blackBall) && playerTwoBalls.length === high) {
        return playerTwoBalls.includes(blackBall) ? false : 'player2';
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
            console.log(winner + " wins the game!");
        } else {
            console.log(currentPlayer + " loses by sinking the 8-ball prematurely.");
        }
    } else {
        if (sunkOpponentBall) {
            switchPlayer = false;
        }
        if (!sunkOwnBall) {
            switchPlayer = true; // Switch player if no own balls were sunk
        }
        if(sunkOwnBall){
            switchPlayer = false;
        }
    }
}


$(document).ready(function() {

    currentPlayer = Math.random() < 0.5 ? 'player1' : 'player2';
    console.log(currentPlayer + " starts first");
    updatePlayerUI(currentPlayer);

    let isDragging = false;
    let line = null;
    let startX, startY;

    $('#svgContainer').on('mousedown', 'circle[fill="WHITE"]', function(event) {
        const svg = document.querySelector('#svgContainer svg');
        const pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());

        startX = svgP.x;
        startY = svgP.y;

        isDragging = true;
        line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', startX);
        line.setAttribute('y1', startY);
        line.setAttribute('x2', startX);
        line.setAttribute('y2', startY);
        line.setAttribute('stroke', 'black');
        line.setAttribute('stroke-width', 5); // Thick line
        svg.appendChild(line);
    });

    $(document).on('mousemove', function(event) {
        if (!isDragging || !line) return;

        const svg = document.querySelector('#svgContainer svg');
        const pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());

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
    
        const deltaX = svgP.x - startX;
        const deltaY = svgP.y - startY;
    
        if (line) {
            line.remove();
            line = null;
        }
    
        var currentPlayerKey = currentPlayer + "Name";
        var data = {
            playerName: FormData[currentPlayerKey], // Dynamically access the name based on currentPlayer
            gameName: FormData.gameName, // Directly accessing properties without jQuery syntax
            x: deltaX,
            y: deltaY
        };
    
        // Use $.post to send the data, including handling success and error responses
        $.post("/shot", data)
            .done(function(response) {
                console.log("Shot submitted successfully:", response);
                switchPlayer = true
                console.log(currentPlayer)
            
                if (response.svgContents) {
                    displaySVGsInSequence(response.svgContents);
                }

                if (response.balls_sunk && response.balls_sunk.length > 0) {
                    
                    updatePlayerBalls(response.balls_sunk);
                    updateGameAfterShot(response.balls_sunk);
                }

                if (switchPlayer) {
                    currentPlayer = currentPlayer === 'player1' ? 'player2' : 'player1';
                    console.log("Switching players. It's now " + currentPlayer + "'s turn.");
                    updatePlayerUI(currentPlayer); // Update the UI to reflect the current player
                }

                
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                console.error("Error submitting shot:", textStatus, errorThrown);
            });
    });
});
