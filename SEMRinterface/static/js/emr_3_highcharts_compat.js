// Highcharts 8+ / current-stock compatibility for the restored research viewer.
// Latest Highstock dropped series.xData, so updateExtremes treated every row as empty and hid it.
(function (global) {
    function seriesXValues(series) {
        if (!series) {
            return [];
        }
        if (series.xData && series.xData.length) {
            return series.xData;
        }
        if (typeof series.getColumn === 'function') {
            var col = series.getColumn('x');
            if (col && col.length) {
                return Array.prototype.slice.call(col);
            }
        }
        if (series.points && series.points.length) {
            var fromPoints = [];
            for (var p = 0; p < series.points.length; p++) {
                if (series.points[p] && series.points[p].x != null) {
                    fromPoints.push(series.points[p].x);
                }
            }
            if (fromPoints.length) {
                return fromPoints;
            }
        }
        var data = (series.options && series.options.data) || [];
        var fromData = [];
        for (var d = 0; d < data.length; d++) {
            var pt = data[d];
            if (Object.prototype.toString.call(pt) === '[object Array]' && pt.length) {
                fromData.push(pt[0]);
            } else if (pt && typeof pt === 'object' && pt.x != null) {
                fromData.push(pt.x);
            }
        }
        return fromData;
    }

    global.updateExtremes = function () {
        if (selectedMin == null || selectedMax == null || isNaN(selectedMin) || isNaN(selectedMax)) {
            return;
        }
        $("#selectedTimes").text(get_formatted_date(selectedMin) + ' to ' + get_formatted_date(selectedMax));
        try {
            $("#lab-time1").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time2").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time3").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time4").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time5").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time6").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time11").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time12").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time13").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time14").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time15").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
            $("#lab-time16").highcharts().xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
        } catch (err) {}
        for (var i = 0; i < chartsContainers.length; i++) {
            var chart = chartsContainers[i];
            if (!chart || !chart.xAxis || !chart.xAxis[0]) {
                continue;
            }
            var notPoints = true;
            var currData = [];
            var seriesList = chart.xAxis[0].series || [];
            for (var q = 0; q < seriesList.length; q++) {
                currData = currData.concat(seriesXValues(seriesList[q]));
            }
            if (currData.length === 0) {
                try {
                    chart.xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
                    $("div[id='" + chartrowids[i] + "']").show();
                } catch (err) {}
                continue;
            }
            for (q = 0; q < currData.length; q++) {
                if (currData[q] >= selectedMin && currData[q] <= selectedMax) {
                    notPoints = false;
                    break;
                }
            }
            if (notPoints) {
                $("div[id='" + chartrowids[i] + "']").hide();
            } else {
                chart.xAxis[0].setExtremes(selectedMin, selectedMax, true, false);
                $("div[id='" + chartrowids[i] + "']").show();
            }
        }
    };

    var origGetchartTS = global.getchartTS;
    global.getchartTS = function (id, case_details, time_step) {
        time_step = time_step || 0;
        displayed_min_t = case_details[time_step].min_t;
        displayed_max_t = case_details[time_step].max_t;
        selectedMin = displayed_min_t;
        selectedMax = displayed_max_t;
        return origGetchartTS(id, case_details, time_step);
    };
}(this));
