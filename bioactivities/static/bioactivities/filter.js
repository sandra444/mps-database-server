//    // Expose only what is needed for submission
//    window.FILTER = {
//        'target_types': target_types,
//        'organisms': organisms,
//        'log_scale': log_scale,
//        'normalize_bioactivities': normalize_bioactivities,
//        'metric': metric,
//        'method': method,
//        'chemical_properties': chemical_properties
//    };
// window.FILTER.

// This is how to expose variables for use in the respective scripts
window.FILTER = {
    bioactivities_filter: {},
    targets_filter: {},
    compounds_filter: {},
    drugtrials_filter: {}
};

$(document).ready(function () {
    // Get a list for checkboxes from returned AJAX data
    // Min is a boolean value to see if data should be restricted on min_feat_count
    function get_list(data, min) {
        if (!data || data.length === 0) {
            return [];
        }

        var result = [];
        var i;
        for (i = 0; i < data.length; i += 1) {
            // Consider refactor for min_feat_count restriction
            if (!min || data[i][1] >= min_feat_count) {
                result.push({
                    name: data[i][0],
                    is_selected: false
                });
            }
        }

        // Case insensitive sort
        result = _.sortBy(result, function (i) {
            return i.name.toLowerCase();
        });

        return result;
    }

    // Function to reset the rows after refresh
    // PLEASE BE CERTAIN TO ESCAPE CHARACTERS LIKE ' (for prime)
    function reset_rows(name, list, add) {
        // Clear current
        $('#' + name).html('');

        // Check if all checked
        var all_checked = true;
        var lookup_current = {};

        // Add from list
        for (var i in list) {
            var row = '';

            var checked = false;
            if (!window.FILTER[name + '_filter'][list[i].name.replace(/'/g, "&#39;")]) {
                all_checked = false;
            }
            else {
                checked = ' checked';
            }
            // Note added 'c' to avoid confusion with graphic
            if (add) {
                var data = list[i].name.split('|');
                var compound_name = data[0];
                var is_drug = data[1];
                var LogP = data[2];
                var molecular_weight = data[3];
                var mps = data[4];
                var epa = data[5];
                var tctc = data[6];
                row = "<tr id='" + add + compound_name.replace(/ /g, "_").replace(/'/g, "&#39;")
                    + "' data-is_drug=" + is_drug
                    + " data-LogP=" + LogP
                    + " data-molecular_weight=" + molecular_weight
                    + " data-mps=" + mps
                    + " data-epa=" + epa
                    + " data-tctc=" + tctc
                    + " data-contains= true"
                    + ">";
                row += "<td>" + "<input type='checkbox' value='" + compound_name.replace(/'/g, "&#39;") + "'" + checked + "></td>";
                row += "<td>" + compound_name + "</td>";
                row += "</tr>";
                $('#' + name).append(row);
            }
            else {
                row = "<tr id='" + list[i].name.replace(/ /g, "_").replace(/'/g, "&#39;") + "'>";
                row += "<td>" + "<input type='checkbox' value='" + list[i].name.replace(/'/g, "&#39;") + "'" + checked + "></td>";
                row += "<td>" + list[i].name + "</td>";
                row += "</tr>";
                $('#' + name).append(row);
            }

            lookup_current[list[i].name.replace(/'/g, "&#39;")] = true;
        }

        var keys_of_interest = _.keys(window.FILTER[name + '_filter']);

        $.each(keys_of_interest, function(index, key) {
            if (!lookup_current[key]) {
                delete window.FILTER[name + '_filter'][key];
            }
        });

        // Reset select all box if necessary
        $("#all_" + name).prop('checked', all_checked);
    }

    function refresh(changed) {
        // Disable everything
        $("#selection_form :input").prop("disabled", true);

        $.ajax({
            url: '/bioactivities/all_data/',
            type: "GET",
            dataType: 'json',
            data: {
                pubchem: FILTER.pubchem,
                exclude_questionable: FILTER.exclude_questionable,
                target_types: JSON.stringify(FILTER.target_types),
                organisms: JSON.stringify(FILTER.organisms),
                csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
            },
            success: function (json) {
                //console.log(json);
                targets = get_list(json.targets, true);
                compounds = get_list(json.compounds, true);
                bioactivities = get_list(json.bioactivities, true);
                drugtrials = get_list(json.drugtrials, false);
                //console.log(targets);
                //console.log(compounds);
                //console.log(bioactivities);
                //console.log(drugtrials);

                // Clear targets
                reset_rows('targets', targets, '');
                $('#target_filter').val('');

                if (changed === 'all') {
                    // Clear bioactivities
                    reset_rows('bioactivities', bioactivities, '');

                    // Clear compounds
                    reset_rows('compounds', compounds, 'c');

                    // Clear drugtrials
                    reset_rows('drugtrials', drugtrials, '');

                    $('.table-filter').val('');
                }

                compound_search.trigger('input');

                // Enable everything
                $(":input").prop("disabled", false);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);

                // Enable everything
                $(":input").prop("disabled", false);
            }
        });
    }

//    // Initial hash change
//    document.location.hash = "";

    // Currently testing, should grab these with a function in refresh (KEEP THIS FORMAT)
    window.FILTER.target_types = [];
    window.FILTER.organisms = [];
    $("#control_target_types input[type='checkbox']:checked").each(function () {
        window.FILTER.target_types.push({"name": this.value, "is_selected": this.checked});
    });
    $("#control_organisms input[type='checkbox']:checked").each(function () {
        window.FILTER.organisms.push({"name": this.value, "is_selected": this.checked});
    });

    // Functions to acquire new lists for target_types
    var control_target_types = $("#control_target_types input[type='checkbox']");
    control_target_types.change(function (evt) {
        window.FILTER.target_types = [];
        if ($("#control_target_types input[type='checkbox']:checked").length == control_target_types.length) {
            $('#all_target_types').prop('checked', true);
        }
        else {
            $('#all_target_types').prop('checked', false);
        }

        control_target_types.each(function () {
            //console.log(this.value);
            window.FILTER.target_types.push({"name": this.value, "is_selected": this.checked});
        });

        refresh('target');
    });
    //Change all target_types
    $('#all_target_types').change(function (evt) {
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
    control_organisms.change(function (evt) {
        window.FILTER.organisms = [];
        if ($("#control_organisms input[type='checkbox']:checked").length == control_organisms.length) {
            $('#all_organisms').prop('checked', true);
        }
        else {
            $('#all_organisms').prop('checked', false);
        }

        control_organisms.each(function () {
            //console.log(this.value);
            window.FILTER.organisms.push({"name": this.value, "is_selected": this.checked});
        });

        refresh('target');
    });
    //Change all organisms
    $('#all_organisms').change(function (evt) {
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
        $('#all_' + name).change(function (evt) {
            // If the "all" box is checked, select all visible checkboxes
            if (this.checked) {
                $("#" + name + " input[type='checkbox']:visible").prop('checked', true).each(function() {
                    window.FILTER[name + '_filter'][this.value] = true;
                });
            }
            // Otherwise deselect all checkboxes
            else {
                $("#" + name + " input[type='checkbox']:visible").prop('checked', false).each(function() {
                    delete window.FILTER[name + '_filter'][this.value];
                });
            }
        });

        // Track when any row checkbox is clicked and discern whether all visible check boxes are checked, if so then check the "all" box
        $("body").on("change", "#" + name + " input[type='checkbox']", function (event) {
            if ($("#" + name + " input[type='checkbox']:checked:visible").length === $("#" + name + " input[type='checkbox']:visible").length) {
                $('#all_' + name).prop('checked', true);
            }
            else {
                $('#all_' + name).prop('checked', false);
            }

            if (this.checked) {
                window.FILTER[name + '_filter'][this.value] = true;
            }
            else {
                delete window.FILTER[name + '_filter'][this.value];
            }
        });
    }

    // Change all bioactivities
    track_selections('bioactivities');

    // Change all targets
    track_selections('targets');

    // Change all compounds
    track_selections('compounds');

    // Change all drugtrials
    track_selections('drugtrials');

    // Initial min_feature count
    var min_feat_count = $('#minimum_feature_count').val();
    // Listen min feature count
    $('#apply_minimum_feature_count').click(function (evt) {
        min_feat_count = $('#minimum_feature_count').val();
        refresh('all');
    });

    var pubchem = $('#pubchem');
    var exclude_questionable = $('#exclude_questionable');
    var log_scale = $('#log_scale');
    var normalize_bioactivities = $('#normalize_bioactivities');
    var chemical_properties = $('#chemical_properties');
    var metric = $('#metric');
    var method = $('#method');

    // Initial truth pubchem
    window.FILTER.pubchem = pubchem.prop('checked');
    // Listen pubchem
    pubchem.change(function (evt) {
        window.FILTER.pubchem = pubchem.prop('checked');
        refresh('all');
    });

    // Initial truth exclude_questionable
    window.FILTER.exclude_questionable = exclude_questionable.prop('checked');
    // Listen exclude_questionable
    exclude_questionable.change(function (evt) {
        window.FILTER.exclude_questionable = exclude_questionable.prop('checked');
        refresh('all');
    });

    // Initial truth log scale
    window.FILTER.log_scale = log_scale.prop('checked');
    // Listen log_scale
    log_scale.change(function (evt) {
        window.FILTER.log_scale = log_scale.prop('checked');
    });

    // Initial truth normalize
    window.FILTER.normalize_bioactivities = normalize_bioactivities.prop('checked');
    // Listen normalize
    normalize_bioactivities.change(function (evt) {
        window.FILTER.normalize_bioactivities = normalize_bioactivities.prop('checked');
    });

    // Initial truth chem properties
    window.FILTER.chemical_properties = chemical_properties.prop('checked');
    // Listen chemical properties
    chemical_properties.change(function (evt) {
        window.FILTER.chemical_properties = chemical_properties.prop('checked');
    });

    // Initial metric
    window.FILTER.metric = metric.val();
    // Listen metric
    metric.change(function (evt) {
        window.FILTER.metric = metric.val();
    });

    // Initial method
    window.FILTER.method = method.val();
    // Listen method
    method.change(function (evt) {
        window.FILTER.method = method.val();
    });

    var targets = [];
    var compounds = [];
    var bioactivities = [];
    var drugtrials = [];

    refresh('all');

    var bioactivity_search = $('#bioactivity_filter');
    var target_search = $('#target_filter');
    var compound_search = $('#compound_filter');
    var drugtrial_search = $('#drugtrial_filter');

    var bioactivity_string = bioactivity_search.val().toLowerCase().replace(/ /g, "_");
    var target_string = target_search.val().toLowerCase().replace(/ /g, "_");
    // Note added 'c' to compound string
    var compound_string = 'c' + compound_search.val().toLowerCase().replace(/ /g, "_");

    // Drug trials is not part of the table filter; check if exists
    if (drugtrial_search[0]) {
        var drugtrial_string = drugtrial_search.val().toLowerCase().replace(/ /g, "_");
    }

    var drugs = $('#drugs');
    var non_drugs = $('#non_drugs');

    var mps = $('#mps');
    var epa = $('#epa');
    var tctc = $('#tctc');
    var unlabelled = $('#unlabelled');

    var logp = $('#logp');
    var logp_gtlt = $('#logp_gtlt');

    var molecular_weight = $('#molecular_weight');
    var molecular_weight_gtlt = $('#molecular_weight_gtlt');

    $.each([drugs, non_drugs, mps, epa, tctc, unlabelled, logp, logp_gtlt, molecular_weight, molecular_weight_gtlt], function(index, element) {
        element.change(function() {
            compound_search.trigger('input');
        });
    });

    function gtlt_check(operator, value, compare_against) {
        // If the value to compare against is not valid, just return true
        if (isNaN(compare_against) || $.trim(compare_against) === '') {
            return true;
        }

        value = Math.floor(value);
        compare_against = Math.floor(compare_against);

        // If greater than
        if (operator == '>') {
            if (value > compare_against) {
                return true;
            }
            else {
                return false;
            }
        }
        // If less than
        else {
            if (value < compare_against) {
                return true;
            }
            else {
                return false;
            }
        }
    }

    function filter_compounds() {
        var drugs_checked = drugs.prop('checked');
        var non_drugs_checked = non_drugs.prop('checked');
        var mps_checked = mps.prop('checked');
        var epa_checked = epa.prop('checked');
        var tctc_checked = tctc.prop('checked');
        var unlabelled_checked = unlabelled.prop('checked');

        var logp_compare_against = logp.val();
        var logp_gtlt_operator = logp_gtlt.val();

        var molecular_weight_compare_against = molecular_weight.val();
        var molecular_weight_gtlt_operator = molecular_weight_gtlt.val();

        $("#compounds tr").each(function(index) {
            var row_values = {};
            for (var attribute, i=0, attributes=this.attributes, n=attributes.length; i<n; i++) {
                attribute = attributes[i];
                row_values[attribute.nodeName] = attribute.nodeValue;
            }

            if(
                ((drugs_checked && row_values['data-is_drug'] === 'True') || (non_drugs_checked && row_values['data-is_drug'] !== 'True'))
                &&
                (
                    (mps_checked && row_values['data-mps'] === 'True')
                    ||
                    (epa_checked && row_values['data-epa'] === 'True')
                    ||
                    (tctc_checked && row_values['data-tctc'] === 'True')
                    ||
                    (unlabelled_checked && row_values['data-mps'] !== 'True' && row_values['data-epa'] !== 'True' && row_values['data-tctc'] !== 'True')
                )
                && gtlt_check(logp_gtlt_operator, row_values['data-logp'], logp_compare_against)
                && gtlt_check(molecular_weight_gtlt_operator, row_values['data-molecular_weight'], molecular_weight_compare_against)
                && row_values['data-contains'] === 'true'
            ) {
                this.hidden = false;
            }
            else {
                this.hidden = true;
            }
        });
    }

    function reset_all_checkbox(selector) {
        // Check or uncheck all as necessary
        if ($("#" + selector + " input[type='checkbox']:checked:visible").length === $("#" + selector + " input[type='checkbox']:visible").length) {
            $('#all_' + selector).prop('checked', true);
        }
        else {
            $('#all_' + selector).prop('checked', false);
        }
    }

    // Function to reduce code
    // search = selector for search filter
    // string = the string typed into the input box
    // selector = the string (no #) to identify what is being acted on
    function search_filter(search, string, selector, add) {
        search.on('input', function () {
            string = search.val().toLowerCase().replace(/ /g, "_");

            // For compounds
            if (add) {
                // For every row in the given table
                $("#" + selector + " tr").each(function () {
                    if (this.id.toLowerCase().indexOf(string) > -1) {
                        this.setAttribute('data-contains', true);
                    }
                    // If it does not contain the string hide it
                    else {
                        this.setAttribute('data-contains', false);
                    }
                });
                filter_compounds();
            }
            // For every other type of data
            else {
                // For every row in the given table
                $("#" + selector + " tr").each(function () {
                    // If the row contains the requested string, do not hide it
                    if (this.id.toLowerCase().indexOf(string) > -1) {
                        this.hidden = false;
                    }
                    // If it does not contain the string hide it
                    else {
                        this.hidden = true;
                    }
                });
            }
            // Check or uncheck all as necessary
            reset_all_checkbox(selector);
        }).trigger('input');
    }

    // When the bioactivity search changes
    search_filter(bioactivity_search, bioactivity_string, 'bioactivities', '');

    // When the target search changes
    search_filter(target_search, target_string, 'targets', '');

    // When the compound search changes
    search_filter(compound_search, compound_string, 'compounds', 'c');

    // Drug trials is not part of the table filter; check if exists
    if (drugtrial_search[0]) {
        // When the drugtrial search changes
        search_filter(drugtrial_search, drugtrial_string, 'drugtrials', '');
    }

    window.onhashchange = function() {
        if (location.hash !== '#show') {
            $('#graphic').prop('hidden', true);
            $('#selection').prop('hidden', false);
            // Ensure table header (if present) is hidden
            $('#table_header').hide();
        }
        else {
            $('#graphic').prop('hidden', false);
            $('#selection').prop('hidden', true);
            // Ensure table header (if present) is shown
            $('#table_header').show();
        }
    };
});
