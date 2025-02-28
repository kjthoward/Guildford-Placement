<!DOCTYPE html>
<html>
<head>
<title> Number of Artefacts by type </title>
<style>

table {
    align-self: center;
    border-collapse: collapse;
    border-style: none;

}
tr {
    border-bottom: solid;
    border-width: 1px;
    border-color: #b3b3b3;
}

/* Adds stripe effect to table */
tr:nth-child(even) {
  background-color: #f2f2f2;
}

th, td {
    text-align: center;
    padding: 8px;
}

th {
    background-color: #cce6ff;
}
</style>
</head>
<body>
  <p>
    OMI-DB is a dataset of mammogram images comprising of multiple datasets from multiple cases.
    Each dataset contains two views of each breast (medio-lateral oblique and cranio-caudal).
  </p>
  <p>
    Artefacts, objects that appear on a mammogram in addition to the breast tissue,
    can be problematic as they may show up as very bright areas (such as metal clips/implants)
    which could obscure areas of the tissue, or they may be misinterpreted as suspicious tissue causing unnecessary tests to
    be carried out.
  </p>
  <p>
    10,518 images from the OMI-BD dataset were classified into 13 categories, as an image may have more than one
    artefact a total of 10,542 classifications were applied.
  </p>
  <p>
    The table below summaries the number of images that have each type of artefact. Clicking on the name of an artefact
    will take you to a page with information about the images that have that artefact type.
  </p>
  <p>
    This data can also be viewed as graph <a href='/total_chart.php'>here</a>
  </p>
<?php

/*
this script reads all the image artefacts are on the artifact database
and present them in a table. It also shows the total amount of
cases for each classification
*/

/* check for any mistakes in the PHP script:*/

ini_set('display_errors',1);
error_reporting(E_ALL|E_STRICT);

/*
Connect to the database, using the host name(IP adress),
username, password and the name of the database:
*/

$hostname = "localhost";
$username = "khoward";
$password = "artifact123";
$databasename = "artifactdb";

// check the connections:

$dbconnection = @new mysqli($hostname, $username, $password, $databasename);

if ($dbconnection ->connect_error) {
    echo "MySQL connection FAILED <br><br>" . $dbconnection ->connect_error;
	die;
}

/* Gets the list of artefact names */

$sql = "SELECT name FROM artefact_types";
$result = $dbconnection -> query($sql) ;
// Set the name of the columns on the table
if (isset($result->num_rows) and ($result->num_rows>0)) {
    echo"<table border='1'><tr><th> Artefact Type</th>";
    echo"<th>Count</th></tr>";

    /*
    For each classification, read the total amount of images and print it to
    the correct cell
    */
    while($row = $result -> fetch_assoc()) {
        $artefact = $row["name"];
		//Links the artefact names to a second table that lists all images that have that artefact
		echo "<tr><td><a href='/list_images.php?artefact=$artefact'>".$artefact. "</a></td>";
        $sql4= " SELECT COUNT(*)
		             FROM image_artefacts
 		             JOIN artefact_types ON artefact_types.id=image_artefacts.artefact_id
		             WHERE artefact_types.name='$artefact'";
        $result4 = $dbconnection -> query($sql4);
        $echore = mysqli_fetch_assoc($result4);

        echo "<td>".$echore['COUNT(*)']."</td>";
      }
        echo "</tr>";



    echo "<td><b> Total </b></td>";

    // also print the total amount at the last row

    $sql4= " SELECT COUNT(*)
		         FROM image_artefacts
		         JOIN artefact_types ON artefact_types.id=image_artefacts.artefact_id
		         WHERE artefact_types.name is not NULL";
    $result4 = $dbconnection -> query($sql4);
    $echore = mysqli_fetch_assoc($result4);
    echo "<td><b>".implode(" ",$echore)."</b></td>";

	echo "</table>";

} else {
    echo "0 Results Found";

}
?>

</body>
</html>
