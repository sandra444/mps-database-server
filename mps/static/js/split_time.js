window.SPLIT_TIME = {
    // For converting between times
    time_conversions: {
        'day': 1440.0,
        'hour': 60.0,
        'minute': 1.0
    },
    get_split_time: null,
    get_minutes: null
}

// SHOULD PROBABLY JUST HANDLE THIS IN PYTHON WHEN POSSIBLE
window.SPLIT_TIME.get_split_time = function(time_in_minutes) {
    var times = {
        'day': 0,
        'hour': 0,
        'minute': 0
    };

    var time_in_minutes_remaining = time_in_minutes;
    $.each(window.SPLIT_TIME.time_conversions, function(time_unit, conversion) {
        var initial_time_for_current_field = Math.floor(time_in_minutes_remaining / conversion);
        if (initial_time_for_current_field) {
            times[time_unit] = initial_time_for_current_field;
            time_in_minutes_remaining -= initial_time_for_current_field * conversion;
        }
    });

    // Add fractions of minutes if necessary
    if (time_in_minutes_remaining) {
        times['minute'] += time_in_minutes_remaining
    }

    return times
};

window.SPLIT_TIME.get_minutes = function(days, hours, minutes) {
    return minutes + (hours * 60) + (days * 1440)
};
