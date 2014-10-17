$(document).ready(function () {
    var get_points = function (id, name) {
        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                call: 'fetch_chip_readout',
                id: id,
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                data = [name];
                time = [];
                csv = json.csv.split('\n');
                for (var i in csv) {
                    var line = csv[i].split(',');
                    if (line[2]) {
                        time.push(line[0]);
                        data.push(line[2]);
                    }
                }
                plot(data, time);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    };

    var plot = function (data, time) {
        console.log(data);

        if (data.length == 1) {
            alert('There is not any data for this readout!');
            return;
        }

        displayed += 1;

        time.unshift('x' + displayed);

        var xs = {};
        xs[data[0]] = 'x' + displayed;

        console.log(xs);

        if (!chart) {
            chart = c3.generate({
                bindto: '#chart',

                data: {
                    xs: xs,

                    columns: [
                        data,
                        time,
                    ]
                }
            });
        }
        else {
            chart.load({
                xs: xs,

                columns: [
                    data,
                    time,
                ]
            });
        }
    };

    //Get token
    var middleware_token = getCookie('csrftoken');

    //Create chart variable
    var chart = null;
    var displayed = 0;

    $('.readout').click(function () {
        alert($(this).attr('id'));
        get_points($(this).attr('id'), $(this).attr('name'));
    });

});
