$(document).ready(function () {

    function table(data, link) {

        // Show graphic
        $('#graphic').prop('hidden',false);
        // Hide error
        $('#error_message').prop('hidden',true);

        // Clear old (if present)
        $('#full').dataTable().fnDestroy();
        $('#table').html('');

        // Set href
        $('#download').attr('href',link);

        for (var i in data) {
            var bio = data[i];
            //console.log(bio);
            var row = "<tr>";
            row += "<td><a href='/compounds/"+bio.compoundid+"'>" + bio.compound + "</a></td>";
            row += "<td>" + bio.target + "</td>";
            row += "<td>" + bio.organism + "</td>";
            row += "<td>" + bio.standard_name + "</td>";
            row += "<td>" + bio.operator + "</td>";
            row += "<td>" + bio.standardized_value + "</td>";
            row += "<td>" + bio.standardized_units + "</td>";
            row += "<td><a href='https://www.ebi.ac.uk/chembl/assay/inspect/"+bio.chemblid+"'>" + bio.chemblid + "</a></td>";
//            row += "<td>" + bio.bioactivity_type + "</td>";
//            row += "<td>" + bio.value + "</td>";
//            row += "<td>" + bio.units + "</td>";
            row += "</tr>";
            $('#table').append(row);
        }

        $('#full').DataTable({
            "iDisplayLength": 100,
            // Needed to destroy old table
            "bDestroy": true
        });

        // Swap positions of filter and length selection
        $('.dataTables_filter').css('float','left');
        $('.dataTables_length').css('float','right');
    }

    function submit() {

        // Clear all filters
        bioactivities_filter = [];
        targets_filter = [];
        compounds_filter = [];

        // Get bioactivities
        $("#bioactivities input[type='checkbox']:checked").each( function() {
            bioactivities_filter.push({"name":this.value, "is_selected":this.checked});
        });

        // Get targets
        $("#targets input[type='checkbox']:checked").each( function() {
            targets_filter.push({"name":this.value, "is_selected":this.checked});
        });

        // Get compounds
        $("#compounds input[type='checkbox']:checked").each( function() {
            compounds_filter.push({"name":this.value, "is_selected":this.checked});
        });

        // Hide Selection html
        $('#selection').prop('hidden',true);
        // Hide error
        $('#error_message').prop('hidden',true);

        // Show spinner
        window.spinner.spin(
            document.getElementById("spinner")
        );

        $.ajax({
            url:  '/bioactivities/gen_table/',
            type: 'POST',
            contentType: 'application/json',
            // Remember to convert to string
            data: JSON.stringify({
                'bioactivities_filter': bioactivities_filter,
                'targets_filter': targets_filter,
                'compounds_filter': compounds_filter,
                'target_types_filter': target_types,
                'organisms_filter': organisms
            }),
            success: function (json) {
                // Stop spinner
                window.spinner.stop();
                //console.log(json);

                if (json.data_json) {
                    //console.log(json);
                    table(json.data_json, json.table_link);
//                    document.location.hash = "display";

                    if (json.length > 5000) {
                        $('#overflow').prop('hidden', false);
                        $('#length').html('Displaying 5000 of ' + json.length);
                    }
                    else {
                        $('#overflow').prop('hidden', true);
                        $('#length').html('');
                    }
                }
                else {
                    if (json.error) {
                        $('#error').html(json.error);
                    }
                    // Show error
                    $('#error_message').prop('hidden',false);
                    // Show Selection
                    $('#selection').prop('hidden',false);
                }

            },
            error: function (xhr, errmsg, err) {
                // Stop spinner
                window.spinner.stop();

                console.log(xhr.status + ": " + xhr.responseText);

                // Show error
                $('#error_message').prop('hidden',false);
                // Show Selection
                $('#selection').prop('hidden',false);
            }
        });
    }

    // Get a list for checkboxes from returned AJAX data
    function get_list(data) {
        if (!data || data.length == 0) {
            return [];
        }

        var result = [];
        var i;
        for (i = 0; i < data.length; i += 1) {
            if (data[i][1] >= min_feat_count) {
                result.push({
                    name: data[i][0],
                    is_selected: false
                });
            }
        }

        // Case insensitive sort
        result = _.sortBy(result, function (i) { return i.name.toLowerCase(); });

        return result;
    }

    // Function to reset the rows after refresh
    function reset_rows(name,list,add) {
        // Clear current
        $('#' + name).html('');
        // Add from list
        for (var i in list) {
            // Note added 'c' to avoid confusion with graphic
            var row = "<tr id='" + add + list[i].name.replace(/ /g,"_") + "'>";
            row += "<td>" + "<input type='checkbox' value='" + list[i].name + "'></td>";
            row += "<td>" + list[i].name + "</td>";
            $('#' + name).append( row );
        }

        // Reset select all box
        $("#all_" + name).prop('checked',false);
    }

    function refresh() {

        // Disable everything
        $(":input").prop("disabled",true);

        $.ajax({
            url:  '/bioactivities/all_data',
            type: "GET",
            dataType: "json",
            data: {
                target_types: JSON.stringify(target_types),
                organisms: JSON.stringify(organisms)
            },
            success: function (json) {
                //console.log(json);
                targets = get_list(json.targets);
                compounds = get_list(json.compounds);
                bioactivities = get_list(json.bioactivities);

                // Clear bioactivities
                reset_rows('bioactivities',bioactivities,'');

                // Clear targets
                reset_rows('targets',targets,'');

                // Clear compounds
                reset_rows('compounds',compounds,'c');

                // Enable everything
                $(":input").prop("disabled",false);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);

                // Enable everything
                $(":input").prop("disabled",false);
            }
        });
    }

//    // Initial hash change
//    document.location.hash = "";

    // Currently testing, should grab these with a function in refresh (KEEP THIS FORMAT)
    var target_types = [];
    var organisms = [];
    $("#control_target_types input[type='checkbox']:checked").each( function() {
        target_types.push({"name":this.value, "is_selected":this.checked});
    });
    $("#control_organisms input[type='checkbox']:checked").each( function() {
        organisms.push({"name":this.value, "is_selected":this.checked});
    });

    // Functions to acquire new lists for target_types
    var control_target_types = $("#control_target_types input[type='checkbox']");
    control_target_types.change(function(evt) {
        target_types = [];
        if ($("#control_target_types input[type='checkbox']:checked").length == control_target_types.length) {
            $('#all_target_types').prop('checked', true);
        }
        else {
            $('#all_target_types').prop('checked', false);
        }

        control_target_types.each(function() {
            //console.log(this.value);
            target_types.push({"name":this.value, "is_selected":this.checked});
        });

        refresh();
    });
    //Change all target_types
    $('#all_target_types').change(function(evt) {
        if (this.checked) {
            control_target_types.prop('checked', true);
        }
        else {
            control_target_types.prop('checked', false);
        }
        // Please note the use of first to prevent redundant calls
        control_target_types.first().trigger('change');
    });

    // Functions to acquire new lists for organisms
    var control_organisms = $("#control_organisms input[type='checkbox']");
    control_organisms.change(function(evt) {
        organisms = [];
        if ($("#control_organisms input[type='checkbox']:checked").length == control_organisms.length) {
            $('#all_organisms').prop('checked', true);
        }
        else {
            $('#all_organisms').prop('checked', false);
        }

        control_organisms.each(function() {
            //console.log(this.value);
            organisms.push({"name":this.value, "is_selected":this.checked});
        });

        refresh();
    });
    //Change all organisms
    $('#all_organisms').change(function(evt) {
        if (this.checked) {
            control_organisms.prop('checked', true);
        }
        else {
            control_organisms.prop('checked', false);
        }
        // Please note the use of first to prevent redundant calls
        control_organisms.first().trigger('change');
    });

    // Function to refactor redundant code
    // Name is the general selector without #
    function track_selections(name) {
        // Check to see if the "select all" button has been clicked
        $('#all_' + name).change(function(evt) {
            // If the "all" box is checked, select all visible checkboxes
            if (this.checked) {
                $("#" + name + " input[type='checkbox']:visible").prop('checked', true);
            }
            // Otherwise deselect all checkboxes
            else {
                $("#" + name + " input[type='checkbox']:visible").prop('checked', false);
            }
        });

        // Track when any row checkbox is clicked and discern whether all visible check boxes are checked, if so then check the "all" box
        $("body").on( "change", "#" + name + " input[type='checkbox']", function(event) {
            if ($("#" + name + " input[type='checkbox']:checked:visible").length == $("#" + name + " input[type='checkbox']:visible").length) {
                $('#all_' + name).prop('checked', true);
            }
            else {
                $('#all_' + name).prop('checked', false);
            }
        });
    }

    // Change all bioactivities
    track_selections('bioactivities');

    // Change all targets
    track_selections('targets');

    // Change all compounds
    track_selections('compounds');

    // Initial min_feature count
    var min_feat_count = $('#minimum_feature_count').val();
    // Listen min feature count
    $('#apply_minimum_feature_count').click(function(evt) {
        min_feat_count = $('#minimum_feature_count').val();
        refresh();
    });

    var targets = [];
    var compounds = [];
    var bioactivities = [];

    var targets_filter = [];
    var compounds_filter = [];
    var bioactivities_filter = [];

    refresh();

    $('#submit').click(function(evt) {
        submit();
    });

    // Return to selection
    $('#back').click(function(evt) {
        $('#graphic').prop('hidden',true);
        $('#selection').prop('hidden',false);
//        document.location.hash = "";
//        //Why does microsoft want me to suffer?
//        if (browser.isIE && browser.verIE >= 11) {
//            $('#graphic').prop('hidden',true);
//            $('#selection').prop('hidden',false)
//        }
    });

    var bioactivity_search = $('#bioactivity_filter');
    var target_search = $('#target_filter');
    var compound_search = $('#compound_filter');

    var bioactivity_string = bioactivity_search.val().toLowerCase().replace(/ /g,"_");
    var target_string = target_search.val().toLowerCase().replace(/ /g,"_");
    // Note added 'c' to compound string
    var compound_string = 'c' + compound_search.val().toLowerCase().replace(/ /g,"_");

    // Function to reduce code
    // search = selector for search filter
    // string = the string typed into the input box
    // selector = the string (no #) to identify what is being acted on
    // add = string to add to the search values (used for compounds)
    function search_filter(search,string,selector,add) {
        search.on('input',function() {
        // Note the added 'c' to avoid confusion in compounds
        string = add + search.val().toLowerCase().replace(/ /g,"_");

        // For every row in the given table
        $("#" + selector + " tr").each(function() {
                // If the row contains the requested string, do not hide it
                if (this.id.toLowerCase().indexOf(string) > -1) {
                    this.hidden = false;
                }
                // If it does not contain the string hide it
                else {
                    this.hidden = true;
                }
            });

            // Check or uncheck all as necessary
            if ($("#" + selector + " input[type='checkbox']:checked:visible").length == $("#" + selector + " input[type='checkbox']:visible").length) {
                $('#all_' + selector).prop('checked', true);
            }
            else {
                $('#all_' + selector).prop('checked', false);
            }
        }).trigger('input');
    }

    // When the bioactivity search changes
    search_filter(bioactivity_search,bioactivity_string,'bioactivities','');

    // When the target search changes
    search_filter(target_search,target_string,'targets','');

    // When the compound search changes
    search_filter(compound_search,compound_string,'compounds','c');

//    function hashChange() {
//
//        if (document.location.hash == "") {
//            $('#graphic').prop('hidden',true);
//            $('#selection').prop('hidden',false)
//        }
//
//        else {
//            $('#graphic').prop('hidden',false);
//            $('#selection').prop('hidden',true)
//        }
//    }
//
//    //This will call the hashchange function whenever the hashchanges (does not work on outdated versions of IE)
//    window.onhashchange = hashChange;
});
