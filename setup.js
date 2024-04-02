// Exporting getFormData for use in other modules
export function getFormData() {
    return {
        player1Name: $("#player1Name").val(),
        player2Name: $("#player2Name").val(),
        gameName: $("#gameName").val()
    };
}

$(document).ready(function() {
    $("#gameSetupForm").submit(function(event) {
        event.preventDefault();

        var formData = getFormData();
        
        $.post("/initialize", formData, function(data) {
            // Hide the form and optional header
            $('#gameSetupForm').hide();
            $('h1').hide();

            // Load the 8-ball.html content
            $('#mainContent').load('8-ball.html', function() {
                // Use the SVG content from the response
                // Assuming you have a container to display the SVG
                $('#svgContainer').html(data.svg);
                console.log("8-ball game setup:", formData);
                // Additional initialization based on the game setup can be done here
            });
        }, "json") // Expect a JSON response
          .fail(function() {
            alert("Error initializing the game.");
        });
    });
});