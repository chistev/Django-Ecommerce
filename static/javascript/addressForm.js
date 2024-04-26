$(document).ready(function () {
    // Retrieve the URL from the data attribute
    var getCitiesUrl = $('#getCitiesUrl').data('url');
    $('#state').change(function () {
        var stateId = $(this).val();

        // Send AJAX request to get cities for the selected state
        $.ajax({
            url: getCitiesUrl,
            data: {
                'state_id': stateId
            },
            dataType: 'json',
            success: function (data) {
                var options = '<option value="" disabled selected>City</option>';
                $.each(data.cities, function (key, value) {
                    options += '<option value="' + value.id + '">' + value.name + '</option>';
                });
                $('#city').html(options).removeAttr('disabled').removeClass('bg-secondary');
            },
            error: function (xhr, status, error) {
                console.error("AJAX error:", error);
            }
        });
    });

    // Add form submission event listener
    $('form').submit(function (event) {
        // Check if state is selected
        var stateSelected = $('#state').val();
        // Check if city is selected
        var citySelected = $('#city').val();

        // If state is selected but city is not selected
        if (stateSelected && !citySelected) {
            // Show the message for city selection
            $('#city-selection-message').show();
            // Prevent form submission
            event.preventDefault();
        }
    });
});
