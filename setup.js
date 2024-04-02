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
            $('#gameSetupForm').hide();
            $('h1').hide();
            $('#mainContent').load('8-ball.html', function() {
                $('#gameModal').hide();
                $('#svgContainer').html(data.svg);
                $()
            });
        }, "json")
          .fail(function() {
            alert("Error initializing the game.");
        });
    });
});