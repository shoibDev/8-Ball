import { getFormData } from './setup.js';

var FormData = getFormData();

function sendShotData(deltaX, deltaY) {
    // Retrieve the initial form data
    var formData = getFormData();

    // Adding deltaX and deltaY to the formData object
    formData.deltaX = deltaX;
    formData.deltaY = deltaY;

    // Use $.ajax to send the extended formData, including deltaX and deltaY
    $.ajax({
        url: '/shot',
        type: 'POST',
        contentType: 'application/json', // Send as JSON
        data: JSON.stringify(formData), // Convert formData object to JSON string
        success: function(response) {
            console.log('Shot made successfully:', response);
        },
        error: function(xhr, status, error) {
            console.error('Error making shot:', status, error);
        }
    });
}

function displaySVGsInSequence(svgContents) {
    const svgContainer = $('#svgContainer');
    let index = 0;
    console.log("init")

    function displayNextSVG() {
        if (index < svgContents.length) {
            svgContainer.html(svgContents[index]);
            console.log(svgContents[index])
            index++;
            setTimeout(displayNextSVG, 10); // Wait for 1 second before displaying the next SVG
        }
    }

    displayNextSVG();
}

$(document).ready(function() {
    $.get("/getSVG", function(data) {
        console.log(data);
        $('#svgContainer').html(data);
    }).fail(function() {
        alert("Failed to load the SVG. Please try again.");
    });

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
    
        // Correctly define the data object
        var data = {
            playerName: FormData.player1Name, // Assuming FormData.player1Name exists
            gameName: FormData.gameName, // Directly accessing properties without jQuery syntax
            x: deltaX,
            y: deltaY
        };
    
        // Use $.post to send the data, including handling success and error responses
        $.post("/shot", data)
            .done(function(response) {
                console.log("Shot submitted successfully:", response);
                
                if (response.svgContents) {
                    displaySVGsInSequence(response.svgContents);
                }
                
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                console.error("Error submitting shot:", textStatus, errorThrown);
            });
    });
});
