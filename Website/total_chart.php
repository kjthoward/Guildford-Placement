<?php

ini_set('display_errors',1);
error_reporting(E_ALL|E_STRICT);


$hostname = "10.161.128.46";
$username = "khoward";
$password = "artifact123";
$databasename = "artifactdb";

$dbconnection = @new mysqli($hostname, $username, $password, $databasename);

if ($dbconnection ->connect_error) {
    echo "MySQL connection FAILED <br /><br />" . $dbconnection ->connect_error;
	die;
}
//gets list of artefact types
$sql = "SELECT name FROM artefact_types";
$result = $dbconnection -> query($sql) ;

if (isset($result->num_rows) and ($result->num_rows>0)) {
  $artefacts = array();
  while($row = $result -> fetch_assoc()) {
    $artefacts[] = $row["name"];
  }
}
else {
  echo "0 Results Found";
}


?>

<html>
<head>
    <title> Bar Chart for Artefact Totals</title>
    <!--Load the AJAX API-->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
        // Load the Visualization API and the corechart package.
        google.charts.load('current', {'packages': ['corechart']});
        // Set a callback to run when the Google Visualization API is loaded.
        google.charts.setOnLoadCallback(drawChart);
        function drawChart() {
            // Create the data table.
            var data = google.visualization.arrayToDataTable([
              ['Type of Artefact','Number of Images', {role: 'annotation'}],
              <?php
                foreach($artefacts as $artefact) {
			               $sql1= " SELECT COUNT(*)
						                  FROM image_artefacts
						                  JOIN artefact_types ON artefact_types.id=image_artefacts.artefact_id
						                  WHERE artefact_types.name='$artefact'";

			               $result1 = $dbconnection -> query($sql1);
			               $echore1 = mysqli_fetch_array($result1);

				  //added count as annotation as for very low frequencies you can't see the
				  //bar to hover over it to get the number
				  if($echore1['COUNT(*)']>100) {
				  	  $annotation = NULL;}

				  else {
					  $annotation=$echore1['COUNT(*)'];}

          echo "['$artefact', ".$echore1['COUNT(*)'].", '$annotation'],";

              }

              ?>
            ]);

            // Set chart options
            var options = {
              title: 'Number of Different Artefact Types' ,
              titleTextStyle: {
                color: 'Black',
                fontSize: '30',

              },
              vAxis:{
                title: 'Count',
                titleTextStyle: {
                  Color: 'Black',
                  fontSize: 22,
                  italic: false,
                },
              },
              hAxis: {
                title: 'Artefact Type',
                titleTextStyle: {
                  Color: 'Black',
                  fontSize: 22,
                  italic: false,
                },
              },
              colors: ['#0000ff'],
              height: 500,
              legend: 'none',
              isStacked: false,
             };

            function resizeChart () {
               chart.draw(data, options);
            };
            if (document.addEventListener) {
              window.addEventListener('resize', resizeChart);
            }
            else if (document.attachEvent) {
              window.attachEvent('onresize', resizeChart);
            }
            else {
              window.resize = resizeChart;
            };

            // Instantiate and draw our chart, passing in some options.
            var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));

			/*Makes the labels for the chart 'hyperlinks' (can't make them true hyperlinks but can add
			 an on click event listener which effectively acts as a hyper link)*/
			google.visualization.events.addListener(chart, 'click', function (e) {
			    // match the id of the axis label
			    var match = e.targetID.match(/hAxis#0#label#(\d+)/);
			    if (match && match.length) {
			        var row = parseInt(match[1]);
			        // get's the 0th row from the data table, row is X Axis label:
			        var label = data.getValue(row, 0);
			        // Constructs URL
			        var url = '/list_images.php?artefact=' + label;
			        window.location = url;
			    }
			});

            chart.draw(data, options);
        }
    </script>
</head>

<body>
    <!--Div that will hold the chart-->
    <div id="chart_div" style="width: 100%;"></div>
</body>

</html>
