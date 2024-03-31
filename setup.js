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

        // Use getFormData to retrieve form data
        var formData = getFormData();
        
        $.post("/initialize", formData, function(data) {
            $('#gameSetupForm').hide();

            // Optionally, if you want to also hide the header
            $('h2').hide();
            $('#mainContent').load('8-ball.html', function() {
                // After loading 8-ball.html, you can initialize or display the game setup data
                // This is also a good place to run any JavaScript needed to initialize the new content
                console.log("8-ball game setup:", formData);
                // You might want to do something with formData here or initialize the game based on the response
            });
        }).fail(function() {
            alert("Error initializing the game.");
        });
    });
});
