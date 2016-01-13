// This script was made to prevent redundant code in plate pages

// Namespace for layout functions
window.LAYOUT = {};

$(document).ready(function () {
    var time_conversions = [
        1,
        60,
        1440,
        10080
    ];

    var time_units = [
        'min',
        'hour',
        'days',
        'weeks'
    ];

    function get_best_time_index(value) {
        var index = 0;
        while (time_conversions[index + 1]
            && time_conversions[index + 1] <= value
            && (value % time_conversions[index + 1] == 0
                || value % time_conversions[index] != 0
                || (value > 1440 && index != 2))) {
            index += 1;
        }
        return index;
    }

    window.LAYOUT.fill_layout = function(layout_data) {
        $.each(layout_data, function(well, data) {
            var list = $('#' + well + '_list');

            var stamp =  '';
            var text = '';
            var li = '';

            // Set type

            stamp = well + '_type';

            $('#' + stamp)
                .text(data.type);

            if (data.color) {
                $('#' + well).css('background-color', data.color);
            }

            // Set time
            stamp = well + '_time';
            // Only display text if timepoint or compounds (timepoint of zero acceptable)
            if (data.timepoint !== undefined) {
                // Get best units and convert
                var best_index = get_best_time_index(data.timepoint);
                var best_unit = time_units[best_index];
                var converted_time = data.timepoint / time_conversions[best_index];

                // Display time with best value
                text = 'Time: ' + converted_time + ' ' + best_unit;

                // Be sure to add event when necessary
                li = $('<li>')
                    .attr('id', stamp)
                    .text(text);

                list.prepend(li);
            }

//          // Set compounds
            if (data.compounds) {
                $.each(data.compounds, function (index, compound) {

                    // BE CERTAIN THAT STAMPS DO NOT COLLIDE
                    stamp = well + '_' + index;

                    text = compound.name + ' (' + compound.concentration +
                        ' ' + compound.concentration_unit + ')';

                    li = $('<li>')
                        .text(text)
                        .attr('compound', compound.id);

                    list.append(li);
                });
            }

            // Set label
            stamp = well + '_label';
            if (data.label) {
                // Be sure to add event when necessary
                li = $('<li>')
                    .attr('id', stamp)
                    .text(data.label);

                list.append(li);
            }
        });
    };
});
