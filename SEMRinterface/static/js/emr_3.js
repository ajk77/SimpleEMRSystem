
// Global Variables // 
var selected_items = []; // The names of the labs that are in the promoted region
var chartsContainers = []; // The ids of all the chart containers 
var chartrowids = []; // The ids of all the chart rows
var selectedMin; // The min time currently displayed across all charts
var selectedMax; // The max time currently displayed across all charts
var displayed_min_t = null; // The min time of the current time step
var displayed_max_t = null; // The max time of the current time step
var step = 0; // The step in case_details.json
var case_details; // the case details
var case_complete_url; // url runs when case if finished


// Page loading activites //
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

    // Update extremes which hides items that do not have data within current time selection
    updateExtremes();

    $('#directions_button').removeAttr("disabled");
    $('#break_button').removeAttr("disabled");

});

// Shows loading screen after navigation buttons have been clicked // 
function show_loading(){
    $('#loading_new_patient').show();
}

// Removes directions div and hides loading text // 
function remove_directions(){
    $('#directions').hide();
    $('#loading_new_patient').hide();
}

// function to save case detials //
function set_case_details(details){
	case_details = details;
}

// function to save case compelte url //
function set_case_complete_url(case_id, user_id){
	case_complete_url = '/SEMRinterface/'+case_id+'/'+user_id+'/';
}

// Functionality for the continue button //
function next_step(){
	if (case_details.length-1 > step) {
		step+=1;
		getchartTS($(time_selector),case_details,step);
		remove_vertical_point(true);  // updates bands
		updateExtremes();
	} else {

		link_press(case_complete_url);
	}
}

// link press helper //
function link_press(curr_url){
    window.location.href = curr_url;
}

// string formatting function //
function get2D( num ) {
    return ( num.toString().length < 2 ? "0"+num : num ).toString();
}

// String formatting function //
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

// 	Updates the min and max time for each chart on change of the time selector //
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
        if (notPoints){ // Hides charts when no points in selected range
            $("div[id='"+chartrowids[i]+"']").hide();
        }else{
            chartsContainers[i].xAxis[0].setExtremes(selectedMin, selectedMax);
            $("div[id='"+chartrowids[i]+"']").show();
            chartsContainers[i].reflow();
        }
    }
}

// highlight chart //
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

// unhighlight chart //
function un_highlight(id){
    var curr = "div[id='"+id+"']";
    $(curr).css("background-color","#eeeeee");
    selected_items.splice(selected_items.indexOf(id), 1);
}

//changes note button colors
function setColor(curr){
    $(curr).parent().parent().children().children().removeClass('red-text');
    $(curr).addClass('n-button');
    $(curr).addClass('v-button');
    $(curr).addClass('red-text');
    //remove_vertical_point(false);  // this removes bands and dotted lines
}

//  Add vertical plot line to each graph //
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

//  Remove vertical plot line to each graph // 
function remove_vertical_point(display_recent_24){
    for (var i = 0; i < chartsContainers.length; i++) {
        chartsContainers[i].xAxis[0].removePlotLine('plot-line-1');
        if (display_recent_24){
            chartsContainers[i].xAxis[0].addPlotBand({
                from: displayed_max_t-86400000,
                to: displayed_max_t,
                color: '#fce1c9',
                id: 'plot-line-1'
                });
        }
    }
    $("#selectedP").css('background', '#222222');
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

// Create lab chart helper //
function add_observation_chart(obs_id, observation_details, variable_details, panel_1_groups){
	/*
		observation_details is from observations.json
		variable_details is from variable_details.json
	*/
	var chart_container_id = 'chart'+obs_id
	if (panel_1_groups.includes(variable_details.display_group)) {
		div_str = '<div class="vitalrow" id="row'+obs_id+'">' 	
	} else {
		div_str = '<div class="chartrow" id="row'+obs_id+'">' 
	}
	div_str += '<div class="chartcol1 shower"> </div>'
	div_str += '<div class="chartcol3" id="'+chart_container_id+'"></div></div>'
	$('#'+variable_details.display_group).append(div_str);		
	get_lab_chart(chart_container_id, observation_details, variable_details);
}

// Create lab chart //
function get_lab_chart(chart_container_id, observation_details, variable_details) {
	// determine if lab is numberic or descrete //
	if (observation_details.numeric_lab_data.length > 0) {
		var chart_data = observation_details.numeric_lab_data;
		var show_y_axis_labels = true;
		var left_spacing = 10;
		var title_x_spacing = 0;
	} else if (observation_details.discrete_lab_data.length > 0) {
		console.log('in descrete values');
		var chart_data = observation_details.discrete_lab_data;
		var show_y_axis_labels = false;
        var left_spacing = 34;
        var title_x_spacing = -24
	} else {
		console.log('no lab for' + variable_details.display_name);
		return;
	}

	// find most recent value that is < displayed_max_t //
	var most_recent_val = '';
	for (var i = chart_data[0].data.length - 1; i >= 0; i--) {
		if(chart_data[0].data[i][0] <= displayed_max_t){
			most_recent_val = chart_data[0].data[i][1];
			break;
		}
	}
	
	//	console.log(chart_container_id, chart_data[0].data.length, variable_details.display_name);

	// create and render chart //
    var currChart = new Highcharts.Chart({
        chart: {
            renderTo: chart_container_id,
            height: 80,
            spacingLeft: left_spacing,
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
            text: '<p style="font-size:13px">' + most_recent_val + '</p><br><p style="font-size:8px">' + variable_details.units + '</p>',
            href: "",
            zIndex: 0,
            position: {align: "right", verticalAlign: "bottom", x: -8, y: -66},
            style: {"fontSize": "14px", "color": "black", "cursor": "default"}
        },
        title: {text: variable_details.display_name, margin: 5, style: {"fontSize": "12px"}, align: "left", x: title_x_spacing},
        legend: {enabled: false},
        yAxis: {
            labels: {enabled: show_y_axis_labels},
            title: {text: null},
            gridLineColor: 'grey',
            plotBands: [{
                from: variable_details.dflt_normal_ranges[0],
                to: variable_details.dflt_normal_ranges[0],
                color: 'rgba(68, 170, 213, 0.4)'
            }]//,
            //min: variable_details.dflt_y_axis_ranges[0],
            //max: variable_details.dflt_y_axis_ranges[1]
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
                    from: displayed_max_t-86400000,
                    to: displayed_max_t,
                    color: '#fce1c9',
                    id: 'plot-line-1'
                }]
            }
        ],
        series: chart_data,
        plotOptions: {
            series: { point: { events: { click: function () { add_vertical_point(this.x); }}}}
        }, tooltip: {
            shared: false,
            positioner: function (labelWidth, labelHeight, point) {
                return {x: currChart.chartWidth / 2 - (labelWidth + 2), y: 0};

            },
            formatter: function () {
                if(this.series.name === 'numeric_values') {
                    return '<p style="font-size:12px">' + this.y + '</p>'
                }else{
                    return '<p style="font-size:12px">' + chart_data.discrete_nominal_to_yIndex[this.y] + '</p>'
                }
            },
            backgroundColor: "rgba(256,256,256,1)",
            padding: 4,
            crosshairs: [false, false]
        }
    });
    chartsContainers.push(currChart);
    chartrowids.push(chart_container_id);
}

// Creat med chart helper //
function add_medication_chart(obs_id, medication_details, med_details){
	/*
		medication_details is from observations.json
		med_details is from variable_details.json
	*/
	var chart_container_id = 'chart'+obs_id
	div_str = '<div class="medrow" id="row'+obs_id+'">' 
	div_str += '<div class="chartcol1 shower"> </div>'
	div_str += '<div class="chartcol3" id="'+chart_container_id+'"></div></div>'
	$('#'+med_details.med_route).append(div_str);		
	get_med_chart(chart_container_id, medication_details, med_details);
}

// Create med chart //
function get_med_chart(chart_container_id, medication_details, med_details) {
    var chart_height = 60 + 15*Math.floor(med_details.display_name.length/30);
	var chart_data = medication_details.med_data;
	
	// find most recent value that is < displayed_max_t //
	var most_recent_val = '';
	for (var i = chart_data[0].data.length - 1; i >= 0; i--) {
		if(chart_data[0].data[i][0] <= displayed_max_t){
			most_recent_val = chart_data[0].data[i][1];
			break;
		}
	}
	
    // Create chart
    var currChart = new Highcharts.Chart({
        chart: {
                renderTo: chart_container_id,
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
            text: '<p style="font-size:13px">' + most_recent_val + '</p>',
            //text: 'test',
            href: "",
            zIndex: 0,
            position: {align: "right",verticalAlign: "bottom",x: -8,y: -chart_height+14},
            style: {"fontSize": "14px", "color": "black", "cursor": "default"}
        },
        title: {text: med_details.display_name, margin: 5, style: {"fontSize": "12px"}, align: "left"},
        legend: {enabled: false},
        yAxis: {
            labels: {enabled: true},
            title: {text: null},
            gridLineColor: 'grey'//,
            //min: post_data[2][0],
            //max: post_data[2][1]
        },
        xAxis: [
            {
                tickLength: 0,
                labels: { enabled: false },
                min: selectedMin,
                max: selectedMax,
                lineWidth: 0,
                plotBands: [{
                    from: displayed_max_t-86400000,
                    to: displayed_max_t,
                    color: '#fce1c9',
                    id: 'plot-line-1'
                }]
            }
        ],
        series: chart_data,
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
            formatter: function() {return this.y},
            padding: 4,
            crosshairs: [false, false]
        }
    });
    chartsContainers.push(currChart);
    chartrowids.push(chart_container_id);
}

/*
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
                    from: displayed_max_t-86400000,
                    to: displayed_max_t,
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
*/

// Creates the time chart //
function getchartT(id) {
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
                {type: 'scatter',name:'min_max',data: [[displayed_min_t,0],[displayed_max_t,0]], visible: false,tooltip: {enabled: false}}
                ],
            tooltip:{enabled: false},
            title: {text: null},
            legend: { enabled: false},
            credits: { enabled:false},
            xAxis: {top: 2,
                labels: {format: '{value:%m/%d}', padding: 1},
                //tickPixelInterval: 25,
                min: displayed_min_t,
                max: displayed_max_t
            },
            yAxis:{ labels: { enabled:false }, title: { text: null}, top: 40} // top is what flips the navigator
		});
}

// Creates the time selector chart //
function getchartTS(id,case_details,time_step=0) {
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
                {type: 'scatter',name:'min_max',data: [[case_details[time_step].min_t,0],[case_details[time_step].max_t,0]], visible: false,tooltip: {enabled: false}}
                ],
            tooltip:{enabled: false},
            title: {text: null},
            legend: { enabled: false},
            credits: { enabled:false},
            xAxis: {top: -10,labels: {enabled: false}, min: case_details[time_step].min_t, max: case_details[time_step].max_t,
                events: {afterSetExtremes: function (e) {selectedMin = e.min;selectedMax = e.max;updateExtremes();}}},
            yAxis:{ labels: { enabled:false }, title: { text: null}} // top is what flips the navigator
    });
	displayed_min_t = case_details[time_step].min_t;
	displayed_max_t = case_details[time_step].max_t;
}

/*
// Creates post for sending data to server // 
function create_manual_input_post(new_link) {
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
}

// Gets cookie from webpage //
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

*/

/*
// Creates rounding report screen // 
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

// Creates complexity rating screen // 
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

// Creates selection screen // 
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
}

// Show all information for patient case //
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
*/
// fin //

