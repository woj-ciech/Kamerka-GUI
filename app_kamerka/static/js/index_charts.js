function drawcharts(ics_len,coordinates_search_len, ports, countries){
//console.log(ports)
    /* reportrange */
    if($("#reportrange").length > 0){   
        $("#reportrange").daterangepicker({                    
            ranges: {
               'Today': [moment(), moment()],
               'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
               'Last 7 Days': [moment().subtract(6, 'days'), moment()],
               'Last 30 Days': [moment().subtract(29, 'days'), moment()],
               'This Month': [moment().startOf('month'), moment().endOf('month')],
               'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            },
            opens: 'left',
            buttonClasses: ['btn btn-default'],
            applyClass: 'btn-small btn-primary',
            cancelClass: 'btn-small',
            format: 'MM.DD.YYYY',
            separator: ' to ',
            startDate: moment().subtract('days', 29),
            endDate: moment()            
          },function(start, end) {
              $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        });
        
        $("#reportrange span").html(moment().subtract('days', 29).format('MMMM D, YYYY') + ' - ' + moment().format('MMMM D, YYYY'));
    }
    /* end reportrange */
    
    /* Rickshaw dashboard chart */
    // var seriesData = [ [], [] ];
    // var random = new Rickshaw.Fixtures.RandomData(1000);

    // for(var i = 0; i < 100; i++) {
        // random.addData(seriesData);
    // }

    // var rdc = new Rickshaw.Graph( {
            // element: document.getElementById("dashboard-chart"),
            // renderer: 'area',
            // width: $("#dashboard-chart").width(),
            // height: 250,
            // series: [{color: "#33414E",data: seriesData[0],name: 'New'}, 
                     // {color: "#1caf9a",data: seriesData[1],name: 'Returned'}]
    // } );

    // rdc.render();

    // var legend = new Rickshaw.Graph.Legend({graph: rdc, element: document.getElementById('dashboard-legend')});
    // var shelving = new Rickshaw.Graph.Behavior.Series.Toggle({graph: rdc,legend: legend});
    // var order = new Rickshaw.Graph.Behavior.Series.Order({graph: rdc,legend: legend});
    // var highlight = new Rickshaw.Graph.Behavior.Series.Highlight( {graph: rdc,legend: legend} );        

    // var rdc_resize = function() {                
            // rdc.configure({
                    // width: $("#dashboard-area-1").width(),
                    // height: $("#dashboard-area-1").height()
            // });
            // rdc.render();
    // }

    // var hoverDetail = new Rickshaw.Graph.HoverDetail({graph: rdc});

    // window.addEventListener('resize', rdc_resize);        

    // rdc_resize();
    /* END Rickshaw dashboard chart */
    
    /* Donut dashboard chart */
    Morris.Donut({
        element: 'dashboard-donut-1',
        data: [
            {label: "ICS", value: ics_len},
            {label: "Coordinates", value: coordinates_search_len},
        ],
        colors: ['#33414E', '#1caf9a', '#FEA223'],
        resize: true
    });
    /* END Donut dashboard chart */
	console.log(ports);
	console.log(ports);
    /* Bar dashboard chart */
    Morris.Bar({
        element: 'dashboard-bar-1',
        data: ports,
        xkey: 'port',
        ykeys: [ 'c'],
        labels: ['Total results'],
        barColors: ['#1caf9a'],
        gridTextSize: '10px',
        xLabelMargin: 10,
        xLabelAngle: 60,
        hideHover: true,
        resize: true,
        gridLineColor: '#E5E5E5'
    });
    /* END Bar dashboard chart */
    
//    /* Line dashboard chart */
//    Morris.Line({
//      element: 'dashboard-line-1',
//      data: [
//        { y: '2014-10-10', a: 2,b: 4},
//        { y: '2014-10-11', a: 4,b: 6},
//        { y: '2014-10-12', a: 7,b: 10},
//        { y: '2014-10-13', a: 5,b: 7},
//        { y: '2014-10-14', a: 6,b: 9},
//        { y: '2014-10-15', a: 9,b: 12},
//        { y: '2014-10-16', a: 18,b: 20}
//      ],
//      xkey: 'y',
//      ykeys: ['a','b'],
//      labels: ['Sales','Event'],
//      resize: true,
//      hideHover: true,
//      xLabels: 'day',
//      gridTextSize: '10px',
//      lineColors: ['#1caf9a','#33414E'],
//      gridLineColor: '#E5E5E5'
//    });
    /* EMD Line dashboard chart */
    /* Moris Area Chart */
//      Morris.Area({
//      element: 'dashboard-area-1',
//      data: [
//        { y: '2014-10-10', a: 17,b: 19},
//        { y: '2014-10-11', a: 19,b: 21},
//        { y: '2014-10-12', a: 22,b: 25},
//        { y: '2014-10-13', a: 20,b: 22},
//        { y: '2014-10-14', a: 21,b: 24},
//        { y: '2014-10-15', a: 34,b: 37},
//        { y: '2014-10-16', a: 43,b: 45}
//      ],
//      xkey: 'y',
//      ykeys: ['a','b'],
//      labels: ['Sales','Event'],
//      resize: true,
//      hideHover: true,
//      xLabels: 'day',
//      gridTextSize: '10px',
//      lineColors: ['#1caf9a','#33414E'],
//      gridLineColor: '#E5E5E5'
//    });
//    /* End Moris Area Chart */
    /* Vector Map */
    var mapData = countries;
        var colorScale = ['#f0f0f0', '#C8EEFF', '#0071A4', '#FFA500', '#ff0000'];

    var jvm_wm = new jvm.WorldMap({container: $('#dashboard-map-seles'),
                                    map: 'world_mill_en', 
                                    backgroundColor: '#FFFFFF',                                      
                                    regionsSelectable: true,
                                    regionStyle: {selected: {fill: '#B64645'},
                                                    initial: {fill: '#33414E'}},
                                    markerStyle: {initial: {fill: '#1caf9a',
                                                   stroke: '#1caf9a'}},
//                                    markers: [{latLng: [50.27, 30.31], name: pies},
//                                              {latLng: [52.52, 13.40], name: 'Berlin - 2'},
//                                              {latLng: [48.85, 2.35], name: 'Paris - 1'},
//                                              {latLng: [51.51, -0.13], name: 'London - 3'},
//                                              {latLng: [40.71, -74.00], name: 'New York - 5'},
//                                              {latLng: [35.38, 139.69], name: 'Tokyo - 12'},
//                                              {latLng: [37.78, -122.41], name: 'San Francisco - 8'},
//                                              {latLng: [28.61, 77.20], name: 'New Delhi - 4'},
//                                              {latLng: [39.91, 116.39], name: 'Beijing - 3'}],
                                    series: {
                                        regions: [
                                            {
                                            scale: ["#0071A4"],
                                            attribute: 'fill',
                                            normalizeFunction: 'polynomial',
                                            values: mapData}]
        },
                                });    
    /* END Vector Map */

    
    $(".x-navigation-minimize").on("click",function(){
        setTimeout(function(){
            rdc_resize();
        },200);    
    });
    
    
};

