<!DOCTYPE html>
<html>
<head>
<style>
<!--
Moved HMTL section to top as for large tables (e.g No Artefatc) the table loads and populates before the CSS
gets applied as the table tables a while to generate, looks odd. Having CSS first means table is always styled
even when it it loading
-->
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

<script>

	function sortTable(table, col, reverse) {
	    var tb = table.tBodies[0], // use `<tbody>` to ignore `<thead>` and `<tfoot>` rows
	        tr = Array.prototype.slice.call(tb.rows, 0), // put rows into array
	        i;
	    reverse = -((+reverse) || -1);
	    tr = tr.sort(function (a, b) { // sort rows
	        return reverse // `-1 *` if want opposite order
	            * (a.cells[col].textContent.trim() // using `.textContent.trim()` for test
	                .localeCompare(b.cells[col].textContent.trim())
	               );
	    });
	    for(i = 0; i < tr.length; ++i) tb.appendChild(tr[i]); // append each row in order
	}

	function makeSortable(table) {
	    var th = table.tHead;
	    th && (th = th.rows[0]) && (th = th.cells);
	    if (th) i = th.length;
	    else console.log("NO"); // if no `<thead>`
	    while (--i >= 0) (function (i) {
	        var dir = 1;
	        th[i].addEventListener('click', function () {sortTable(table, i, (dir = 1 - dir))});
          //if a table header is selected immediately runs a function that returns false
          //other solutions disabled select/copy globally, but might want to copy image_uid etc...
          th[i].onselectstart= new Function ("return false");

	    }(i));
	}

	window.onload = function () {makeSortable(document.getElementById('ArtefactTable'));};
</script>




<?php

/*
this script lists all the images of a particular artefact and presents
them in a table with information such as the study UID and patient number etc...
*/

/* check for any mistakes in the PHP script:*/

ini_set('display_errors',1);
error_reporting(E_ALL|E_STRICT);


/*checks that the argument (artefact type to show) is set
and if it is, saves it as a variable, if not shows an error
*/
if (isset($_GET['artefact'])){
	$artefact = $_GET['artefact'];
}
else{
	echo "ARTEFACT TYPE INCORRECTLY SET!";
	echo "<p><a href='/total_table.php'> CLICK HERE TO GO BACK TO THE TABLE</a></p>";
	echo "<p> OR </p>";
	echo "<p><a href='/total_chart.php'> CLICK HERE TO GO BACK TO THE CHART</a></p>";
	die;
}

echo "<title> List of images with $artefact </title>";
/*
Connect to the database, using the host name(IP adress),
username, password and the name of the database:
*/

$hostname = "localhost";
$username = "khoward";
$password = "artifact123";
$databasename = "artifactdb";

$dbconnection = @new mysqli($hostname, $username, $password, $databasename);

// check the connection:
if ($dbconnection ->connect_error) {
    echo "MySQL connection FAILED <br><br>" . $dbconnection ->connect_error;
	die;
}

//Gets a list of all the images with $artefact

$sql = "SELECT image_artefacts.image_uid
		    FROM image_artefacts
		    JOIN artefact_types ON image_artefacts.artefact_id=artefact_types.id
		    WHERE artefact_types.name='$artefact'";
$result = $dbconnection -> query($sql) ;

//'Dictionary of artefact types - Description'

$descriptions = [
    "No Artefact" => "These classification was applied to images which had no artefact present.",
    "Collimator Misaligned" => "The Collimator is a series of plates that are used to shape and control the x-ray beam. If the Collimator is misaligned a white bar can be seen next to the chest wall.",
    "Other" => "These images have something present in them that does not fit into one of the other 12 categories.",
    "MagView" => "Magnification Views (MagViews) are images that use a small magnification table to brins the breast closer to the x-ray source and further away from the film plate. This allows the acquisition of 'zoomed in' images of the region of interest. Magnification views provide a clearer assessment of the borders and the tissue structures of a suspicious area or a mass.",
    "Thin Breast Artefact" => "During a mammogram the breast is compressed to even out the thickness so all the tissue can be visualised, spread out the tissue so small abnormalities aren’t hidden by overlying tissue. If the breast compresses to less than 2cm in thickness the compression paddle edges may be seen in the image, showing up as bright white corners.",
    "Not Acceptable for Testing" => "This is a broad category of images which do not have a clearly defined full breast or have other objects in view, such as biopsy needles.",
    "Silicone Implant" => "These images have a silicone breast implant present, which shows up as a large, bright, white object.",
    "Medical Port" => "These images contain a medical port, such as a central line port.",
    "Face (or Glasses)" => "These images contain part of the face or the frame of glasses. This can occur if the subject isn't positioned correctly and their hand rests between the x-ray source and the detector. Depending on in the obstruction covers any area of the breast, these images may not need to be repeated.",,
    "Finger (or Hand)" => "These images contain a finger or part of the hand. This can occur if the subject isn't positioned correctly and their hand rests between the x-ray source and the detector. Depending on in the obstruction covers any area of the breast, these images may not need to be repeated.",
    "Metal Clip" => "If an area within the breast is hard to find/biopsy sometimes small metal clips will be inserted into the tissue to help that area be relocated in future. As these are made from titanium, which is non magnetic and body safe, they are often left in after the scan/biopsy as removing them carries more risk than leaving them in.",
    "Saline Implant" => "These images have a saline breast implant present, which shows up as a large, bright grey object. Sometimes the port used for adjusting the volume of saline can also be seen.",
    "Other Type of Implant" => "These images contain another type of implanted deviced, not for breast augmentation, but is larger than the small metal clips used for marking areas.",
];

// Set the name of the columns on the table
// <thead> is used to locate the headers for the 'makesortable' function to find the headers
if (isset($result->num_rows) and ($result->num_rows>0)) {
	echo "<h2> Table of all images with Artefact Type: $artefact</h2>";
	echo "<h4> Click the headers to sort by that column</h4>";
  echo "<p> OMI-DB is a dataset of mammogram images comprising of multiple datasets from multiple cases. Each dataset contains two views of each breast (medio-lateral oblique and cranio-caudal). </p>";
  echo "<p> Artefacts, objects that appear on a mammogram in addition to the breast tissue, can be problematic as they may show up as very bright areas (such as metal clips/implants) which could obscure areas of the tissue, or they may be misinterpreted as suspicious tissue causing unnecessary tests to be carried out. </p>";
  echo "<p> This table lists all of the images that have the artefact type of: $artefact - $descriptions[$artefact] </p>";
  echo "<p><a href='/total_table.php'> Click here to return to the summary table </a></p>";
	echo "<p><a href='/total_chart.php'> Click here to return to the summary chart </a></p>";
  echo"<table id='ArtefactTable' border='1'><thead><tr><th> Image Name</th>";
	echo"<th>Patient Name</th>";
	echo"<th>Study UID</th>";
	echo"<th>Image Laterality</th>";
	echo"<th>Image Positon</th></tr></thead>";
	echo"<tbody>";
    //Gets all the information about each image
    while($row = $result -> fetch_assoc()) {
        $image = $row['image_uid'];
        $info_sql= " SELECT images.image_uid, patients.name, studies.study_uid,
                            laterality.direction, positions.position
				             FROM images
				             JOIN studies ON images.study_id=studies.id
				             JOIN patients ON studies.patient_id=patients.id
				             JOIN laterality ON images.laterality_id=laterality.id
				             JOIN positions ON images.position_id=positions.id
				             WHERE images.image_uid='$image'";
        $info_result = $dbconnection -> query($info_sql);
        $infos = mysqli_fetch_assoc($info_result);
    echo "<tr>";
		//Goes through each value from the SQL result and puts it into a cell
		foreach($infos as $info){
			echo "<td>$info</td>";
		}
        // echo "</tr>";


    }
	echo "</tbody>";
	echo "</table>";

}
//if 0 results artefact type is likely wrong so shows error
else {
	echo "ARTEFACT TYPE INCORRECTLY SET OR 0 RESULTS ARE AVAILIBLE";
	echo "<p><a href='/total_table.php'> CLICK HERE TO GO BACK TO THE TABLE</a></p>";
	echo "<p> OR </p>";
	echo "<p><a href='/total_chart.php'> CLICK HERE TO GO BACK TO THE CHART</a></p>";
	die;

}
?>


</head>
</html>
