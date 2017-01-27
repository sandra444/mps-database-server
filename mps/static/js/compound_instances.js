// This file tracks compound instances for Chip Setups and Assay Layouts
// TODO to be refactored

// IMPORTANT NOTE //
// Instances are placed in the dictionary using the following key:
// <compound_id>_<supplier_name>_<lot>_<receipt_date (as ISO [assumed])>

// Global variable for sharing data with other files
window.COMPOUND_INSTANCES = {
    'data_map': {},
    'instances': {}
};

$(document).ready(function() {
    // TODO REVISE ACQUISITION OF TOKEN
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');
    // Alias for global variable
    var data_map = window.COMPOUND_INSTANCES.data_map;
    var instances = window.COMPOUND_INSTANCES.instances;

    $.ajax({
        url: "/compounds_ajax/",
        type: "POST",
        dataType: "json",
        data: {
            call: 'fetch_compound_instances',
            csrfmiddlewaretoken: middleware_token
        },
        success: function (json) {
            // *Unless something dynamic is being performed,this should just be in python!*
            $.each(json, function(index, compound_instance) {
                var compound_instance_id = compound_instance.id;
                var compound_id = compound_instance.compound_id;
                var supplier_name = compound_instance.supplier_name;
                var lot = compound_instance.lot;
                var receipt_date = compound_instance.receipt_date;

                // Add to instance
                instances[compound_instance_id] = compound_instance;

                // Add to data map
                if(!data_map[compound_id]) {
                    data_map[compound_id] = {};
                }

                if(!data_map[compound_id][supplier_name]) {
                    data_map[compound_id][supplier_name] = {};
                }

                if(!data_map[compound_id][supplier_name][lot]) {
                    data_map[compound_id][supplier_name][lot] = receipt_date;
                }
            });
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});
