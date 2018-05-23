//$(document).ready(function () {
///   console.log("Hello from script!");
//});
//THIS IS THE FILE GETTING ACCESSED

$(document).ready(function () {
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    $.ajax({
        url: "/assays_ajax/",
        type: "POST",
        dataType: "json",
        data: {
            // Function to call - defined in ajax.py
            call: 'fetch_test_filter',
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
            //mysend01: 'anystring'
        },
        success: function (json) {

            /////////////
            //START BASIC DATA Manipulation SECTION
            /////////////

            var keylist = json.keylist;
            var vallist = json.vallist;

            var mpsmodellist = json.mpsmodellist;
            var datagrouplist = json.datagrouplist;
            var studynamelist = json.studynamelist;
            var devicelist = json.devicelist;
            var chipmatrixlist = json.chipmatrixlist;
            var chipnamelist = json.chipnamelist;
            var datapointmethodkitlist = json.datapointmethodkitlist;
            var datapointtargetlist = json.datapointtargetlist;
            var datapointreportingunitlist= json.datapointreportingunitlist;
            var compoundnamelist = json.compoundnamelist;
            var diseaselist = json.diseaselist;
            var datapointlocationlist = json.datapointlocationlist;

            var dgrouplist = [];
            var dgroupnumberlist = [];
            var tiernumlist = [];
            var filteredbylist = [];
            var groupbylist =[];
            var convarlist = [];

            for (var j = 0; j < vallist.length; j++) {
                var mykey = keylist[j];
                var myval = vallist[j];

                var dgroup = mykey.substr(0, 1);
                var dgroupnum = mykey.substr(1, 2);
                var tiernum = mykey.substr(4, 1);
                var filterby = mykey.substr(6, 1);
                var groupby = mykey.substr(8, 1);
                var convar = mykey.substr(10,30) + "list";

                dgrouplist.push(dgroup);
                dgroupnumberlist.push(dgroupnum);
                tiernumlist.push(tiernum);
                filteredbylist.push(filterby);
                groupbylist.push(groupby);
                convarlist.push(convar);
            }

            $('#header_tier1').html('<br>Most Common Filter/Group By');
            $('#header_tier2').html('<br>Data Point Filter/Group By');
            $('#header_tier3').html('<br>Study Filter/Group By');
            $('#header_tier4').html('<br>Compound Filter/Group By');
            $('#header_tier5').html('<br>Cell Filter/Group By');
            $('#header_tier6').html('<br>Setting Filter/Group By');

            var htmld = "<table class='table table-striped table-bordered'>";
            htmld += "<tr><th>F</th><th>G</th><th>Data Element</th></tr>";

            var htmld1 = htmld;
            var htmld2 = htmld;
            var htmld3 = htmld;
            var htmld4 = htmld;
            var htmld5 = htmld;
            var htmld6 = htmld;

            var t1c = 0;
            var t2c = 0;
            var t3c = 0;
            var t4c = 0;
            var t5c = 0;
            var t6c = 0;

            var myfilter;
            var mygroup;
            var myfstring;
            var mygstring;

            var filtertable = "";

            var cc=1; //current column of table (1,2,3)
            var ccmax=3; //max columns allowed


            //build the strings
            //Build for the Filter and Group intro table
            for (var i = 0; i < vallist.length; i++) {
                var myfilter = filteredbylist[i];
                if (myfilter == 'y') {
                    myfstring = "checked";
                } else {
                    myfstring = "";
                }
                var mygroup = groupbylist[i];
                if (mygroup == 'y') {
                    mygstring = "checked";
                } else {
                    mygstring = "";
                }
                if (tiernumlist[i] == 1) {
                    htmld1 += '<tr>';
                    htmld1 += '<td >' + '<input id="tier1f"' + t1c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld1 += '<td >' + '<input id="tier1g"' + t1c + ' type="checkbox" ' + mygstring +'>' + '</td>';
                    htmld1 += '<td  id="tier1v"'+t1c+'">' + vallist[i] + '</td>';
                    htmld1 += '</tr>';
                    t1c++;
                }
                else if (tiernumlist[i] == 2) {
                    htmld2 +='<tr>';
                    htmld2 += '<td >' + '<input id="tier2f"' + t2c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld2 += '<td >' + '<input id="tier2g"' + t2c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld2 += '<td  id="tier2v"'+t2c+'">' + vallist[i] + '</td>';
                    htmld2 += '</tr>';
                    t2c++;
                }
                else if (tiernumlist[i] == 3) {
                    htmld3 += '<tr>';
                    htmld3 += '<td >' + '<input id="tier3f"' + t3c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld3 += '<td >' + '<input id="tier3g"' + t3c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld3 += '<td  id="tier3v"'+t3c+'">' + vallist[i] + '</td>';
                    htmld3 += '</tr>';
                    t3c++;
                }
                else if (tiernumlist[i] == 4) {
                    htmld4 += '<tr>';
                    htmld4 += '<td >' + '<input id="tier4f"' + t4c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld4 += '<td >' + '<input id="tier4g"' + t4c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld4 += '<td  id="tier4v"'+t4c+'">' + vallist[i] + '</td>';
                    htmld4 += '</tr>';
                    t4c++;
                }
                else if (tiernumlist[i] == 5) {
                    htmld5 += '<tr>';
                    htmld5 += '<td >' + '<input id="tier5f"' + t5c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld5 += '<td >' + '<input id="tier5g"' + t5c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld5 += '<td  id="tier5v"'+t5c+'">' + vallist[i] + '</td>';
                    htmld5 += '</tr>';
                    t5c++;
                }
                else {
                    htmld6 += '<tr>';
                    htmld6 += '<td >' + '<input id="tier6f"' + t6c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld6 += '<td >' + '<input id="tier6g"' + t6c + ' type="checkbox" ' + myfstring + '>' + '</td>';
                    htmld6 += '<td  id="tier6v"'+t6c+'">' + vallist[i] + '</td>';
                    htmld6 += '</tr>';
                    t6c++;
                }

                //Build for the Apply/Remove Filter section
                if (myfilter == 'y') {
                    //console.log(convarlist[i]);
                    //for each three, make a new row
                    //put three on each row
                    var econvar = eval(convarlist[i]);
                    var colwit =(100/ccmax).toString()+'%';

                    if (cc == 1) {filtertable += '<tr>';}

                    filtertable     += '  <td class="filterboxcell" valign="top" width=' + colwit + '>';
                    filtertable     += '    <p class="text-left">';
                    filtertable     += '    <label>' + vallist[i] + '<br>';
                    filtertable     += '    <input class="table-filter" id="notfunctional_filter">';
                    filtertable     += '    </label>';
                    filtertable     += '    </p>';
                    filtertable     += '    <div class="table-responsive">';
                    filtertable     += '    <table>';
                    filtertable     += '    <tr>';
                    filtertable     += '       <td title="Check to select all.">';
                    filtertable     += '         <input id="all_target_types" type="checkbox">';
                    filtertable     += '       </td>';
                    filtertable     += '       <td>';
                    filtertable     += '         Check to Include All';
                    filtertable     += '       </td>';
                    filtertable     += '    </tr>';

                    //loop the list of this elements content and add a row for each
                    for (var ll = 0; ll < econvar.length; ll++) {
                        filtertable += '    <tr>';
                        filtertable += '       <td>';
                        filtertable += '         <input id="nofunctional" type="checkbox">';
                        filtertable += '       </td>';
                        filtertable += '       <td>';
                        filtertable +=           econvar[ll];
                        filtertable += '       </td>';
                        filtertable += '    </tr>';
                        //end loop
                    }

                    filtertable     += '    </table>';
                    filtertable     += '    </div>';
                    filtertable     += '  </td>';

                    if ((cc == ccmax) || (i == vallist.length-1) || (vallist.length) < ccmax) {
                        filtertable += '</tr>';
                    }

                    cc++;
                    if (cc>ccmax) {cc=1}
                }
            }

            htmld1+="</table>";
            htmld2+="</table>";
            htmld3+="</table>";
            htmld4+="</table>";
            htmld5+="</table>";
            htmld6+="</table>";

            $('#mytable_tier1').html(htmld1);
            $('#mytable_tier2').html(htmld2);
            $('#mytable_tier3').html(htmld3);
            $('#mytable_tier4').html(htmld4);
            $('#mytable_tier5').html(htmld5);
            $('#mytable_tier6').html(htmld6);

            $('#mysection_filtering').html(filtertable);


        /////////////
        // END data manipulation section
        /////////////

        /////////////
        // START EVENTS Section
        /////////////

        window.onload=function() {
            // when page loads, hide the advanced section
            document.getElementById("gallery-box").style.display = "none";
            document.getElementById("post-format-hide").checked = true;
            document.getElementById("post-format-show").checked = false;


            // attach event listener to links using onclick, fire the function
             document.getElementById("post-format-show").onclick = function() {
                 toggleadvanced("post-format-show");
                 return false;
             };
             document.getElementById("post-format-hide").onclick = function() {
                 toggleadvanced("post-format-hide");
                 return false;
             };
        };

        function toggleadvanced(advancedid) {
            if (advancedid == "post-format-hide") {
                document.getElementById("gallery-box").style.display = "none";
                document.getElementById("post-format-hide").checked= true;
                document.getElementById("post-format-show").checked = false;
                document.getElementById("radioshowhide").value="hide";
            } else {
                document.getElementById("gallery-box").style.display = "block";
                document.getElementById("post-format-hide").checked = false;
                document.getElementById("post-format-show").checked = true;
                document.getElementById("radioshowhide").value="show";
                }
        };

        /////////////
        // END EVENTS Section
        /////////////

        },
        error: function (xhr, errmsg, err) {
            alert('An unknown error has occurred.');
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});
