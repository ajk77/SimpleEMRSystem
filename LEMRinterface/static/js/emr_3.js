$(document).ready(function () {

    var navHeight = $('.navbar').outerHeight(true) + 10;
    $(document.body).scrollspy({
        target: '.bs-sidebar',
        offset: navHeight
    });

    $(window).on('load', function () {
        $(document.body).scrollspy('refresh')
    });

    $('a[data-toggle="tab"]').on('shown.bs.tab', function () {
        $(window).trigger('resize')
    });

    $("#progress-notes").addClass('active');


    // bottom labs scroll event
    $(".labbox").bind("scroll", function() {
        send_div_locations();
    });
    $(".half-vitmedbox").bind("scroll", function() {
        send_div_locations();
    });
    $(".medbox").bind("scroll", function() {
        send_div_locations();
    });
    
    // notes scroll
    $(".report").bind("scroll", function() {
        //note_tracking();
        note_scroll(this.id);
    });
    // note tabs change
    $('.nav-track').on('shown.bs.tab', function () {
        note_tracking();
    });
    // note selection change
    $('.tab-pane').on('shown.bs.tab', function () {
        note_tracking();
    });

    // Update extremes which hides items that do not have data within current time selection
    updateExtremes();

    $('#directions_button').removeAttr("disabled");
    $('#break_button').removeAttr("disabled");

});

// send timestamp when leaving or refreshing a patient page
window.onbeforeunload = function () {
    if(in_study){
        var curr_timestamp = Date.now();
        create_post(patient_id.toString(), curr_timestamp.toString(), '0', '0')
    }
};


// Listener for whether the mouse is clicked or not.
// Needed so that charts don't update until new time range is selected (prevents lag)
$(document).mousedown(function() {
    down = true;
}).mouseup(function() {
    down = false;
});

function send_div_locations(){
    // Save pixelmap as long as within study or in test (99) mode
    if(in_study && dynamic_interface_storage && false){ // turned off storing of screen layout. This functionality is for automated eye tracking analysis
        // variables
        var lab_window, vit_window, io_window, med_window;
        var curr_pixelmap = [];
        var curr_groups = [];
        // timestamp
        var curr_timestamp = Date.now();
        if (!(screen.width === window.innerWidth && (screen.height === window.innerHeight))){
            sendAlert("Please press F11 to go to full screen!");
            //send_div_locations();
        }else {
            if (paused_study) {  // while loading
                create_post(patient_id.toString(), curr_timestamp.toString(), 'PausedScreen,0,0,0,0', 'PausedScreen,0,0,0,0');
            } else {
                if (first_view) {
                    curr_pixelmap.push('FirstView,0,0,0,0');
                } else {
                    curr_pixelmap.push('SecondView,0,0,0,0');
                }
                // Tracking window position
                $("#lab_tracking").each(function () {
                    lab_window = this.getBoundingClientRect();
                });
                $("#vit_tracking").each(function () {
                    vit_window = this.getBoundingClientRect();
                });
                $("#io_tracking").each(function () {
                    io_window = this.getBoundingClientRect();
                });
                $("#med_tracking").each(function () {
                    med_window = this.getBoundingClientRect();
                });
                // Lab positions
                $(".chartrow").each(function () {
                    var edges = this.getBoundingClientRect();
                    var t = edges.top;
                    var b = edges.bottom;
                    var curr_array = [this.id.replace(',', ''), Math.round(t), Math.round(edges.left), Math.round(b),
                        Math.round(edges.right)];
                    if (curr_array[1] < lab_window.bottom && curr_array[3] > lab_window.top) {
                        // object top is < (above) window bottom and object bottom is > (below) window top
                        curr_pixelmap.push(curr_array);
                    }
                });
                // vital positions
                $(".vitalrow").each(function () {
                    var edges = this.getBoundingClientRect();
                    var t = edges.top;
                    var b = edges.bottom;
                    var curr_array = [this.id.replace(',', ''), Math.round(t), Math.round(edges.left), Math.round(b),
                        Math.round(edges.right)];
                    if (curr_array[1] < vit_window.bottom && curr_array[3] > vit_window.top) {
                        // div top (1) is < (pixel count) view bottom (3) and div bottom (3) is > view top (1)
                        curr_pixelmap.push(curr_array);
                    }
                });
                // IO positions
                $(".iorow").each(function () {
                    var edges = this.getBoundingClientRect();
                    var t = edges.top;
                    var b = edges.bottom;
                    var curr_array = [this.id.replace(',', ''), Math.round(t), Math.round(edges.left), Math.round(b),
                        Math.round(edges.right)];
                    if (curr_array[1] < io_window.bottom && curr_array[3] > io_window.top) {
                        // div top (1) is < (pixel count) view bottom (3) and div bottom (3) is > view top (1)
                        curr_pixelmap.push(curr_array);
                    }
                });
                // Med positions
                $(".medrow").each(function () {
                    var edges = this.getBoundingClientRect();
                    var t = edges.top;
                    var b = edges.bottom;
                    var curr_array = [this.id.replace(',', ''), Math.round(t), Math.round(edges.left), Math.round(b),
                        Math.round(edges.right)];
                    if (curr_array[1] < med_window.bottom && curr_array[3] > med_window.top) {
                        // div top (1) is < (pixel count) view bottom (3) and div bottom (3) is > view top (1)
                        curr_pixelmap.push(curr_array);
                    }
                });
                // Lab group positions
                $(".lab-group").each(function () {
                    var edges = this.getBoundingClientRect();
                    var t = edges.top;
                    var b = edges.bottom;
                    var curr_array = [this.id.replace(',', ''), Math.round(t), Math.round(edges.left), Math.round(b),
                        Math.round(edges.right)];
                    curr_groups.push(curr_array)
                });

                create_post(patient_id.toString(), curr_timestamp.toString(), curr_pixelmap.toString(), curr_groups.toString());
            }
        }
    }
}


// this function send the note name and window position on each note navigated to, as well as the note scroll position on each scroll
function note_tracking(){
    var curr_timestamp = Date.now();
    if(in_study && dynamic_interface_storage && false){
        var curr_array = false;
        var active_note_type = 'none';
        // Find active tab
        $('.nav-track.active').each(function () {
            active_note_type = this.id;
        });
        // Find active note location
        $('.active.report.tab-pane').each(function () {
            var edges = this.getBoundingClientRect();
            var t = edges.top;
            var b = edges.bottom;
            if (edges.top > 0) {
                curr_array = [this.id, Math.round(t), Math.round(edges.left), Math.round(b),
                              Math.round(edges.right)];
            }
        });
        // Test if active note existed: post location and scroll, else, post note name and empty
        if (curr_array) {
            create_post(patient_id.toString(), '', curr_array.toString(), '');
            note_scroll(curr_array[0]);
        } else {
            curr_array = [active_note_type, 0, 0, 0, 0];
            create_post(patient_id.toString(), '', curr_array.toString(), '');
        }
    }
}

// this function send the note scroll position on each scroll
function note_scroll(curr_id){
    if(in_study){
        var scroll_top = $('#'+curr_id).scrollTop();
        if (scroll_top === null){scroll_top = 0}
        var curr_pixelmap = Date.now().toString() + ',' + scroll_top;
        create_post(patient_id.toString(), '', curr_pixelmap, '');
    }
}

// Creates post for saving manual selections, case difficulty rating, and clinical impact rating.
function create_manual_input_post(new_link) {
    if(in_study){
        console.log("-saving manual input-"); // sanity check
        var csrf_token = getCookie('csrftoken');
        var return_selected_items = '';
        if (study_arm === 'C'){
            return_selected_items = selected_items.toString()
        }
        $.ajax({
            url : "http://127.0.0.1:8000/LEMRinterface/save_input/", // the endpoint
            type : "POST", // http method
            data : { csrfmiddlewaretoken: csrf_token, the_timestamp : Date.now().toString(), pat_id : patient_id, selections : return_selected_items, rating : case_difficulty, reason: clinical_impact }, // data sent with the post request
            // handle a successful response
            success : function(msg) {
                console.log(msg); // another sanity check
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
               console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            },
            complete :  function() {link_press(new_link)}
        });
        return false;
    }else{
        link_press(new_link);
    }
}

// Creates post to save pixelmaps
function create_post(id, curr_timestamp, curr_pixelmap, curr_groups) {
    if (dynamic_interface_storage  && false){
        var csrf_token = getCookie('csrftoken');
        $.ajax({
            url : "http://127.0.0.1:8000/LEMRinterface/save_pixelmap/", // the endpoint
            type : "POST", // http method
            data : { csrfmiddlewaretoken: csrf_token, the_pixelmap : curr_pixelmap, the_timestamp : curr_timestamp, pat_id : id, the_groups : curr_groups  }, // data sent with the post request
            // handle a successful response
            success : function(msg) {
                console.log(msg); // another sanity check
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
               console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        })}
    return false;
}

// Gets cookie from webpage
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1);
        if (c.indexOf(name) === 0) return c.substring(name.length,c.length);
    }
    return "";
}

// console log function (not used)
function jsTest(jsTest) {
    console.log(jsTest);
}

// window alert function (not used)
function sendAlert(myalert){
         window.alert(myalert);
}

function get2D( num ) {
    return ( num.toString().length < 2 ? "0"+num : num ).toString();
}

// Global Variables
var only_show_highlights = false; // Set true when non highlighted data fields should be hidden
var chartsContainers = []; // Holds all of the promoted charts
var selected_items = []; // The names of the labs that are in the promoted region
var chartrowids = []; // The ids of all the chart rows
var selectedMin; // The min time taken from the time chart range selector
var selectedMax; // The max time taken from the time chart range selector
var data_max; // the max time loaded to interface
var down = false; // True is the mouse is currently clicked.
var patient_id = 0; // holds current patient id
var short_patient_id = 0; // holds a string of the last three digits of the patient id
var user_id = '';  // holds the current user id
var in_study = false; // false if first_four (interface demo), true otherwise
var selection_screen = false; // true when on seelection screen
var case_difficulty = false;
var paused_study = true;
var first_view = true;
var recording = false;
var issue_box = false;
var clinical_impact = 0;
var next_patient_link = '';
var study_arm = '';
var dynamic_interface_storage = false;  // set true if using eye tracking

// sets global patient_id
function set_ids(curr_id, curr_user_id){
    patient_id = curr_id;
    var str_id = String(patient_id);
    short_patient_id = str_id.slice(-3);
    user_id = curr_user_id;
    if (curr_user_id !== 'first_four'){
        in_study = true
    }
}

// sets only_show_highlights variable
function set_only_show_highlights(bool_val){
    only_show_highlights = bool_val;
}

// sets arm variable [C: SV, 1: AHV, 2: APV]
function set_arm(arm_val){
    study_arm = arm_val;
}

// sets view. first view is not bit-tracked
function set_view(view_value){
    if (view_value === 'False'){
        first_view = false;
    }
}

// Assigns the global min and max time to global variables (called once when page is loading)
function setDefaultTimes(global_time){
    selectedMin = global_time.min_t;
    selectedMax = global_time.max_t;
    data_max = global_time.max_t;
}

// Shows loading screen after navigation buttons have been clicked
function show_loading(){
    $('#loading_new_patient').show();
}

// Removes directions div and hides loading text
function remove_directions(){
    $('#directions').hide();
    $('#loading_new_patient').hide();
    paused_study = false;
    // send_div_locations();  This function is for storing screen layout
    note_tracking();
}

// Allows user to take a break and shows calibration screen on resume.
function take_a_break(user_id){
    $('#break_button').attr("disabled", true);
    link_press("http://127.0.0.1:8000/LEMRinterface/home/" + user_id + '/');

    return false;
}

function get_formatted_date(ms_date){
    var js_date = new Date(ms_date);
    var display_date = 0;
    if (js_date.getHours() < 20) {
        display_date = ' ' + get2D(js_date.getMonth() + 1) + '/' + get2D(js_date.getDate()) + ' ' + get2D(js_date.getHours() + 4) + ':' + get2D(js_date.getMinutes());
    }else{
        display_date = ' ' + get2D(js_date.getMonth() + 1) + '/' + get2D(js_date.getDate() + 1) + ' ' + get2D(js_date.getHours() - 20) + ':' + get2D(js_date.getMinutes());
    }

    return display_date;
}

// Updates the min and max time for each of the promoted labs (called every time the time selector moves and...
// ...every time a lab is promoted)
function updateExtremes(){
    //update time axes
    $("#selectedTimes").text(get_formatted_date(selectedMin) + ' to ' + get_formatted_date(selectedMax));
    try {
        $("#lab-time1").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time2").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time3").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time4").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time5").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time6").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time11").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time12").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time13").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time14").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time15").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        $("#lab-time16").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
    }catch(err){}
    // search for charts that do not have points within defined axes.
    for (var i = 0; i < chartsContainers.length; i++) {
        var notPoints = true;
        var currData = [];
        for (var q=0; q < chartsContainers[i].xAxis[0].series.length; q++) {
            currData = currData.concat(chartsContainers[i].xAxis[0].series[q].xData);
        }
        for(q=0;q<currData.length;q++){ // Lookes for data point with currently selected time range
            if (currData[q] >= selectedMin && currData[q] <= selectedMax){
                notPoints = false;
                break;
            }
        }
        //console.log (only_show_highlights);
        //console.log(jQuery.inArray( chartrowids[i], selected_items ));
        if (notPoints || only_show_highlights && jQuery.inArray( chartrowids[i], selected_items ) === -1 ){ // Hides points when they are not in the currently selected time range
            $("div[id='"+chartrowids[i]+"']").hide();
        }else{
            chartsContainers[i].xAxis[0].setExtremes(selectedMin, selectedMax);
            $("div[id='"+chartrowids[i]+"']").show();
            chartsContainers[i].reflow();
        }
    }
    // send_div_locations();  This function is for storing screen layout
}

// Shows group when it contains items (prevents empty groups from being displayed, called during page loading)
function showgroup(id) {
    $("div[id='"+id+"']").show();
}


//highlight labs
function highlight(id){
    var curr = "div[id='"+id+"']";
    $(curr).css("background-color","#FFC300");//.css("border-style", "solid").css("border-width", "thin");
    selected_items.push(id);
    if (case_difficulty){
        $('#next_case_button').css("background-color","green");
    }else{
        $('#next_case_button').css("background-color","#82E0AA");
    }
}

//highlight labs
function un_highlight(id){
    var curr = "div[id='"+id+"']";
    $(curr).css("background-color","#eeeeee");
    selected_items.splice(selected_items.indexOf(id), 1);
}

//hid data field
function hid(id){
    var curr = "div[id='"+id+"']";
    $(curr).css("background-color","#FFC300");//.css("border-style", "solid").css("border-width", "thin");
    selected_items.push(id);
}

//changes note button colors
function setColor(curr){
    $(curr).parent().parent().children().children().removeClass('red-text');
    $(curr).addClass('n-button');
    $(curr).addClass('v-button');
    $(curr).addClass('red-text');
    //remove_vertical_point(false);  // this removes bands and dotted lines
}

//  Add vertical plot line to each graph
function add_vertical_point(point_time, from_note){
    if (typeof from_note !== 'undefined'){
        setColor(this.previousSibling.previousElementSibling);
        // floor to start of day
        var coeff = 1000 * 60 * 60 * 24;
        var round_time = point_time - (point_time%coeff) + 3600000;
        var band_start = new Date(round_time);
        var band_end = band_start.getTime() + coeff;
        for (i = 0; i < chartsContainers.length; i++) {
            chartsContainers[i].xAxis[0].addPlotBand({
                from: band_start,
                to: band_end,
                color: '#E0E0E0',
                id: 'plot-line-1'
            });
        }
        if (band_start < selectedMin){
            selectedMin = band_start;
            // select time selector and update
            $("#time_selector").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        }
        if (band_end > selectedMax) {
            selectedMax = band_end;
            // select time selector and update
            $("#time_selector").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        }
        var st_display = ' ' + get2D(band_start.getMonth() + 1) + '/' + get2D(band_start.getDate() + 1);
        $("#selectedTime").text(st_display);
        $("#selectedP").css('background', 'white');
    }else{
        remove_vertical_point(true);
        for (var i = 0; i < chartsContainers.length; i++) {
            chartsContainers[i].xAxis[0].addPlotLine({
                value: point_time,
                color: 'black',
                dashStyle: 'dash',
                width: 1,
                id: 'plot-line-1'
            });
        }
        if (point_time < selectedMin) {
            selectedMin = point_time;
            // select time selector and update
            $("#time_selector").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        }
        if (point_time > selectedMax) {
            selectedMax = point_time;
            // select time selector and update
            $("#time_selector").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax);
        }
        $("#selectedTime").text(get_formatted_date(point_time));
        $("#selectedP").css('background', 'white');
    }
}

//  Add vertical plot line to each graph
function remove_vertical_point(display_recent_24){
    for (var i = 0; i < chartsContainers.length; i++) {
        chartsContainers[i].xAxis[0].removePlotLine('plot-line-1');
        if (display_recent_24){
            chartsContainers[i].xAxis[0].addPlotBand({
                from: data_max-86400000,
                to: data_max,
                color: '#fce1c9',
                id: 'plot-line-1'
                });
        }
    }
    $("#selectedP").css('background', '#222222');
}

function activate_continue_button(selection, is_case_difficulty){
    if (!(issue_box || recording)){
        $('#next_case_button').removeAttr("disabled");
    }
    if (selected_items.length > 0){
        $('#next_case_button').css("background-color","green");
    }else{
        $('#next_case_button').css("background-color","#ED1D1D");
    }

    if (is_case_difficulty) {
        case_difficulty = selection;
    }
    else{
        clinical_impact = selection;
    }
}

// Creates rounding report screen
function create_rounding_report_screen(next_link) {
    selection_screen = true;
    next_patient_link = next_link;
    var task_text =
        "<p>Now that you are up to date with this patient’s problems and latest data, could you please present the "
        + "patient as if you were presenting during morning rounds, including pertinent positives and negatives, as "
        + "well as your assessment and management plan for the day. Try to make it concise.</p>"
        + "<p>Use the audio recorder to record your presentation.</p>"
        + "<p>Start the recording with '<b>" + user_id + "</b> rounding for <b>" + short_patient_id + "</b>.'</p>"
        + "<hr>Then click <input id='rate_complexity_continue' type='button' value='continue' "
        + "onclick='create_rate_complexity_screen()'>.";
    $("#task").html(task_text);
    create_post(patient_id.toString(), Date.now().toString(), 'RoundingReport,0,0,0,0', 'RoundingReport,0,0,0,0');
    //next is create rate complexity screen
}

// Creates complexity rating screen
function create_rate_complexity_screen(){
    var task_text =
        "Rate the level of effort you exerted when becoming up to date with this patient’s problems and latest data:<br> "
        + '<form><input type="radio" name="diff" value="1" onclick="activate_continue_button(1, true);">  1. low<br>'
        + '<input type="radio" name="diff" value="2" onclick="activate_continue_button(2, true);">  2. below-average<br>'
        + '<input type="radio" name="diff" value="3" onclick="activate_continue_button(3, true);">  3. average<br>'
        + '<input type="radio" name="diff" value="4" onclick="activate_continue_button(4, true);">  4. above-average<br>'
        + '<input type="radio" name="diff" value="5" onclick="activate_continue_button(5, true);">  5. high<br>'
        + '</form>';

    if (study_arm === 'C') { // if control -> next is selection screen
        task_text +=
            "<hr>Then click <input id='selection_screen_continue' type='button' value='continue' "
            + "onclick='create_selection_screen()'>.";
    } else if (study_arm === '1') {// if arm one -> next is next_link press
        task_text +=
            "<hr>Then click <input id='next_case_continue' type='button' value='next case' "
            + "onclick='next_case_link_press()'>";
    } else if (study_arm === '2'){    // if arm two -> next is show additional information
        task_text +=
           "<hr>Then click <input id='show_additional_info_continue' type='button' value='continue' "
           + "onclick='show_additional_information()'>.";
    }
    $("#task").html(task_text);
    create_post(patient_id.toString(), Date.now().toString(), 'ComplexityRating,0,0,0,0', 'ComplexityRating,0,0,0,0');
}

// Creates selection screen
function create_selection_screen(){
    var task_text =
            "Select the pertinent information that you used when becoming up to date with this patient’s problems and latest data.\n"
            + "<hr>Then click <input id='rounding_report_continue' type='button' value='next case' "
            + "onclick='next_case_link_press()'>";
    $('.chartcol1').each(function (i, obj) {
        $(obj).html("<span class='glyphicon glyphicon-unchecked' aria-hidden='true'></span>");
    });
    $('.shower').show();
    $("#task").html(task_text);
    send_div_locations();
    create_post(patient_id.toString(), Date.now().toString(), 'SelectionScreen,0,0,0,0', 'SelectionScreen,0,0,0,0');
}

// Show all information for patient case
function show_additional_information(){
    // show all the hidden labs
    // this function will call create selection screen
    only_show_highlights = false;
    selection_screen = false;
    var task_text =
        "<p>Additional information in now being displayed.</p>"
        + "<p>Considering the additional information, if you would like to revise your presentation, please do so now."
        + "</p><p>Start the recording with "
        + "'<b>" + user_id + "</b> revisions for <b>" + short_patient_id + "</b>.'</p>"
        + "<hr>Then click <input id='selection_screen_continue' type='button' value='continue' "
        + "onclick='create_rate_clinical_impact_screen()'>.";
    $("#task").html(task_text);
    create_post(patient_id.toString(), Date.now().toString(), 'ReviseReport,0,0,0,0', 'ReviseReport,0,0,0,0');
    updateExtremes();
}

// Creates clinical impact rating screen
function create_rate_clinical_impact_screen(){
    // next is next_link press
    selection_screen = true;
    var task_text =
        "If you revised your presentation, rate the clinical impact those revisions would have on patient care:"
        + '<form>'
        + '<input type="radio" name="impact" value="1" onclick="activate_continue_button(1, false);">&nbsp;1. no impact<br>'
        + '<input type="radio" name="impact" value="2" onclick="activate_continue_button(2, false);">&nbsp;2. minor impact<br>'
        + '<input type="radio" name="impact" value="3" onclick="activate_continue_button(3, false);">&nbsp;3. major impact<br><br>'
        + '<input type="radio" name="impact" value="0" onclick="activate_continue_button(0, false);">&nbsp;I did not revise<br>'
        + '</form>'
        + "<hr>Then click <input id='rounding_report_continue' type='button' value='next case' "
        + "onclick='next_case_link_press()'>";
    $("#task").html(task_text);
    create_post(patient_id.toString(), Date.now().toString(), 'ClinicalImpact,0,0,0,0', 'ClinicalImpact,0,0,0,0');
}

// advances to next patient case
function next_case_link_press() {
    create_manual_input_post(next_patient_link);
}

function link_press(curr_url){
    window.location.href = curr_url;
}

// used when selection is made
function activate(id){
    var curr = 'div[id="' + id + '"]';
    var child_2 = $(curr).find('.chartcol1');
    var child_2_html = child_2.html();
    if (child_2_html.length > 1) {
        if (child_2_html.split('-')[1][0] === 'u') {
            child_2.html("<span class='glyphicon glyphicon-check' aria-hidden='true'></span>");
            highlight(id);

        } else {
            child_2.html("<span class='glyphicon glyphicon-unchecked' aria-hidden='true'></span>");
            un_highlight(id);
        }
    }
}

function get_chart(chartTitle, type, predata, displayText){
    //console.log(displayText);
    predata = predata.replace(/'/g, '"');
    var post_data = $.parseJSON(predata);

    // [high, norm, low], curr_data['text'], abs_ranges, norm_ranges, curr_recent_result, curr_recent_units
    if (chartTitle === 'VTDIAA'){
        get_bp_chart(chartTitle, post_data, 'Pulmonary artery BP')
    }else if (chartTitle === 'VTDIAV'){
        get_bp_chart(chartTitle, post_data, 'Systemic BP')
    }else{
        get_lab_chart(chartTitle, post_data, displayText);
    }
}


// lower labs
function get_lab_chart(chartTitle, post_data, displayText) {
    var container = 'lab' + chartTitle;
    var show_y_axis_labels = true;
    var left_spacing = 10;
    var title_x_spacing = 0;

    if (post_data[0][0].data.length === 0 || post_data[0][0].name === 'discrete_values'){
        show_y_axis_labels = false;
        left_spacing = 34;
        title_x_spacing = -24
    }
    var currChart = new Highcharts.Chart({
        chart: {
            renderTo: container,
            height: 80,
            spacingLeft: left_spacing,
            //spacingLeft: 5 - post_data[2][1].toString().length,
            spacingBottom: 6,
            spacingTop: 6,
            spacingRight: 6,
            type: 'scatter',
            events: {
                click: function () {
                    this.tooltip.hide();
                }
            }
        },
        credits: {
            text: '<p style="font-size:13px">' + post_data[4] + '</p><br><p style="font-size:10px">'
                  + String(post_data[5]).replace('null','') + '</p>',
            href: "",
            zIndex: 0,
            position: {align: "right", verticalAlign: "bottom", x: -8, y: -66},
            style: {"fontSize": "14px", "color": "black", "cursor": "default"}
        },
        title: {text: displayText, margin: 5, style: {"fontSize": "12px"}, align: "left", x: title_x_spacing},
        legend: {enabled: false},
        yAxis: {
            labels: {enabled: show_y_axis_labels},
            title: {text: null},
            gridLineColor: 'grey',
            plotBands: [{
                from: post_data[3][0],
                to: post_data[3][1],
                color: 'rgba(68, 170, 213, 0.4)'
            }],
            min: post_data[2][0],
            max: post_data[2][1]
        },
        xAxis: [
            {
                tickLength: 0,
                labels: {
                    enabled: false,
                    formatter: function () {
                        return Highcharts.dateFormat('%b %e %H:%M:%S', this.value);
                    }
                },
                min: selectedMin,
                max: selectedMax,
                lineWidth: 0,
                plotBands: [{
                    from: data_max-86400000,
                    to: data_max,
                    color: '#fce1c9',
                    id: 'plot-line-1'
                }]
            }
        ],
        series: post_data[0],
        plotOptions: {
            series: { point: { events: { click: function () { add_vertical_point(this.x); }}}}
        }, tooltip: {
            shared: false,
            positioner: function (labelWidth, labelHeight, point) {
                return {x: currChart.chartWidth / 2 - (labelWidth + 2), y: 0};

            },
            formatter: function () {
                if(this.series.name === 'numeric_values') {
                    var text = post_data[1][this.series.data.indexOf( this.point )];
                    if (text !== null && text !== undefined){
                        return text;
                    }else{
                        return '<p style="font-size:12px">' + this.y + '</p>'
                    }
                }else{
                    return '<p style="font-size:12px">' + post_data[6][this.y] + '</p>'
                }
            },
            backgroundColor: "rgba(256,256,256,1)",
            padding: 4,
            crosshairs: [false, false]
        }
    });
    chartsContainers.push(currChart);
    chartrowids.push(chartTitle);
}

function get_med_chart(chartTitle, predata, displayName) {
    predata = predata.replace(/'/g, '"');
    var post_data = $.parseJSON(predata);
    var container = 'med'+chartTitle;
    var currChart;
    var chart_height = 60 + 15*Math.floor(displayName.length/30);
    // Create chart
    currChart = new Highcharts.Chart({
        chart: {
                renderTo: container,
                height: chart_height,
                spacingLeft: 6,
                spacingBottom: 6,
                spacingTop: 6,
                spacingRight: 6,
                type: 'scatter',
                events: {
                    click: function () {
                        this.tooltip.hide()
                    }
                }
        },
        credits: {
            text: '<p style="font-size:13px">' + post_data[1][post_data[0][0].data.length-1][0] + '</p><br><p style="font-size:10px">' + post_data[1][post_data[0][0].data.length-1][1] + '</p>',
            //text: 'test',
            href: "",
            zIndex: 0,
            position: {align: "right",verticalAlign: "bottom",x: -8,y: -chart_height+14},
            style: {"fontSize": "14px", "color": "black", "cursor": "default"}
        },
        title: {text: displayName, margin: 5, style: {"fontSize": "12px"}, align: "left"},
        legend: {enabled: false},
        yAxis: {
            labels: {enabled: true},
            title: {text: null},
            gridLineColor: 'grey',
            min: post_data[2][0],
            max: post_data[2][1]
        },
        xAxis: [
            {
                tickLength: 0,
                labels: { enabled: false },
                min: selectedMin,
                max: selectedMax,
                lineWidth: 0,
                plotBands: [{
                    from: data_max-86400000,
                    to: data_max,
                    color: '#fce1c9',
                    id: 'plot-line-1'
                }]
            }
        ],
        series: post_data[0],
        plotOptions: {
            series: {
                point: {
                    events: {
                        click: function () {
                            add_vertical_point(this.x);
                        }
                    }
                }
            }
        },
        tooltip: {
            positioner: function (labelWidth, labelHeight, point) {
                return {x: currChart.chartWidth/2 - (labelWidth + 2), y: 0};
            },
            formatter: function() {return post_data[1][this.series.data.indexOf( this.point )][0]+' '+post_data[1][this.series.data.indexOf( this.point )][1]},
            padding: 4,
            crosshairs: [false, false]
        }
    });
    //}
    chartsContainers.push(currChart);
    chartrowids.push(chartTitle);
}


function get_bp_chart(chartTitle, post_data, displayText) {
    var container = 'lab'+chartTitle;
    var currChart;

    currChart = new Highcharts.Chart({
        chart: {
         renderTo: container,
         height: 120,
         spacingLeft: 6,
         spacingBottom: 6,
         spacingTop: 6,
         spacingRight: 10,
         type: 'scatter',
         events: {click: function (e) {this.tooltip.hide()}}
     }, credits: {
            text: '<p style="font-size:13px">' + post_data[3] + '</p><br><p style="font-size:10px">mm Hg</p>',
            //text: recentValue,
            href: "",
            zIndex: 0,
            position: {align: "right",verticalAlign: "bottom",x: -8,y: -106},
            style: {"fontSize": "14px", "color": "black", "cursor": "default"}
    }, title: {
            text: '<div style="float:right">'+displayText+'</div>', margin: 5, style: {"fontSize": "12px"}, "align": "left"
    }, legend: {enabled: false},
    yAxis: {
        labels: {enabled: true},
        title: {text: null},
        tickPixelInterval: 30,
        max: post_data[2][1],
        min: post_data[2][0]
    }, xAxis: {
         tickLength: 0,
         labels: {
             enabled: false,
             formatter: function () {
                 return Highcharts.dateFormat('%b %e %H:%M:%S', this.value);
             }
         },
         min: selectedMin,
         max: selectedMax,
         lineWidth: 0,
            plotBands: [{
                from: data_max-86400000,
                to: data_max,
                color: '#fce1c9',
                id: 'plot-line-1'
            }]
    }, series: post_data[0],
    plotOptions: {
    series: {
         point: {
             events: {
                 click: function () {
                     add_vertical_point(this.x);
                 }
             }
         }
     }
    },
    tooltip: {
            shared: false,
            formatter: function () { // I need to show all the data in the tooltip, as well as the selected dot value to tell which one is selected
                var series = this.point.series.chart.series,
                    index = this.point.series.xData.indexOf(this.point.x),
                    sys = '',
                    dia = '';

                $.each(series, function(i, s) {
                    if (s.name === 'dias' || s.name === 'art_dia'){
                        dia = s.processedYData[index]
                    }else if (s.name === 'syst' || s.name === 'art_sys') {
                        sys = s.processedYData[index];
                    }
                });
                return sys + '/' + dia;
            },
            positioner: function (labelWidth, labelHeight, point) {
                return {x: currChart.chartWidth/2 - (labelWidth + 2), y: 0};
            },
            backgroundColor: "rgba(255,255,255,1)",
            padding: 4,
            crosshairs: [false, false]
    }
    });
    chartsContainers.push(currChart);
    chartrowids.push(chartTitle);

 }

function get_io_chart(chartTitle, predata, displayText) {
    predata = predata.replace(/'/g, '"');
    var post_data = $.parseJSON(predata);

    var container = 'lab'+chartTitle;
    var currChart;

    currChart = new Highcharts.Chart({
        chart: {
            renderTo: container,
            height: 150,
            spacingLeft:6,
            spacingBottom:6,
            spacingTop:6,
            spacingRight:10,
            type: 'column',
            events:{click: function() {this.tooltip.hide()}}
        },
        credits: {  enabled:false},
        title: {text: '<div style="float:right">Daily Intake and Output</div>', margin: 5, style: {"fontSize": "12px"}, "align": "left"},
        legend: { enabled: false},
        yAxis:
            {
                labels: { enabled:true },
                title: { text: null},
                tickPixelInterval: 50,
                plotLines:[{color:'black', width: 1, value:0}]//,
                //max: Math.min(5000, post_data[2][1]),
                //min: Math.max(-5000, post_data[2][0])
            },
        xAxis: [
            {
                tickLength: 0,
                labels: {
                    enabled:false,
                    formatter: function () { return Highcharts.dateFormat('%b %e %H:%M:%S', this.value);}
                },
                min: selectedMin,
                max: selectedMax,
                lineWidth: 0,
                plotBands: [{
                    from: data_max-86400000,
                    to: data_max,
                    color: '#fce1c9',
                    id: 'plot-line-1'
                }]
            }
        ],
        series: post_data[0],
        plotOptions: {
            series: {point: { events: {click: function () {add_vertical_point(this.x);}}}},
            column: {stacking: 'normal'}
        },
        tooltip: {
            positioner: function (labelWidth, labelHeight, point) {
                return {x: currChart.chartWidth/2 - (labelWidth/2), y: 0};
            },
            formatter: function() {return  this.series.name + ' | ' + Math.round(this.y)},
            crosshairs: [false, false]
         }
    });

    // discrete values
    chartsContainers.push(currChart);
    chartrowids.push(chartTitle);
}

// Creates the time selector chart
// updateExtremes function is called whenever the slider is moved
function getchartT(id,global_time) {
    $(id).highcharts('StockChart', {
            chart: {
                height:25,
                spacingLeft:40,
                spacingBottom:0,
                spacingTop:2,
                spacingRight:6,
                events: {load: function () {
                    var range = this.xAxis[0].getExtremes();
                    this.xAxis[0].setExtremes(Math.max(range.min, range.max-216000000), range.max);}} // On load update selected range // 2.5 days
            },
            scrollbar: {enabled: false},
            navigator: {enabled: false, height: 1, top:4},
            //navigator: {enabled: true, height: 500, top:40},
			rangeSelector : {
                enabled: false,
				selected : 1,
                inputEnabled: true
            },
            series:
                [
                {type: 'scatter',name:'min_max',data: [[global_time.min_t,0],[global_time.max_t,0]], visible: false,tooltip: {enabled: false}}
                ],
            tooltip:{enabled: false},
            title: {text: null},
            legend: { enabled: false},
            credits: { enabled:false},
            xAxis: {top: 2,
                labels: {format: '{value:%m/%d}', padding: 1},
                //tickPixelInterval: 25,
                min: global_time.min_t,
                max: global_time.max_t
            },
            yAxis:{ labels: { enabled:false }, title: { text: null}, top: 40} // top is what flips the navigator
		});
}

// Creates the time selector chart
// updateExtremes function is called whenever the slider is moved
function getchartTS(id,global_time) {

    $(id).highcharts('StockChart', {
            chart: {
                height:35,
                spacingLeft:5,
                spacingBottom:2,
                spacingTop:2,
                spacingRight:5,
                events: {load: function () {
                    var range = this.xAxis[0].getExtremes();
                    this.xAxis[0].setExtremes(Math.max(range.min, range.max-216000000), range.max);
                }} // On load update selected range // 2.5 days
                },
            scrollbar: {enabled: false},
            navigator: {enabled: true, height: 35, top:0},
            //navigator: {enabled: true, height: 500, top:40},
            rangeSelector : {
                enabled: false,
                selected : 1,
                inputEnabled: true,
                buttons: [{type: 'day',count: 1,text: '1d'},{type: 'day',count: 2,text: '2d'},{type: 'week',count: 1,text: '1w'},{type: 'all',text:'All'}]},
            series:
                [
                {type: 'scatter',name:'min_max',data: [[global_time.min_t,0],[global_time.max_t,0]], visible: false,tooltip: {enabled: false}}
                ],
            tooltip:{enabled: false},
            title: {text: null},
            legend: { enabled: false},
            credits: { enabled:false},
            xAxis: {top: -10,labels: {enabled: false}, min: global_time.min_t, max: global_time.max_t,
                events: {afterSetExtremes: function (e) {selectedMin = e.min;selectedMax = e.max;onUpdateOfExtremes();}}},
            yAxis:{ labels: { enabled:false }, title: { text: null}} // top is what flips the navigator
    });
}

function onUpdateOfExtremes(){
    if (!down){
        updateExtremes();
    }
}
