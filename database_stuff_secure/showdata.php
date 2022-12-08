<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  
  <meta http-equiv='refresh' content='60';url='showdata.php'> <!-- Refreshes page every 60 seconds -->
  <META NAME="description" CONTENT="Mushroom Container">

  <META NAME="keywords" CONTENT="Intelligent Bat Detector random forest classification deep learning raspberry pi jetson nano 4g LTE">

  <link REL="SHORTCUT ICON" HREF="http://www.goatindustries.co.uk/goat.ico">
  <title>Mushroom Container</title>


</html>

<?php

$host="localhost"; // Host name 
$username="###############"; // Mysql username 
$password="###############"; // Mysql password 
$db_name="###############"; // Database name 
$tbl_name="###############"; // Table name

// Connect to server and select database.
mysql_connect("$host", "$username", "$password")or die("cannot connect"); 
mysql_select_db("$db_name")or die("cannot select DB");


$query12="SELECT * FROM mushrooms ORDER BY id DESC LIMIT 1";
$result12=mysql_query($query12);
while($row12=mysql_fetch_array($result12))
   {  
   $id = $row12['ID'];
   $time_stamp = $row12['TIME'];
   $temp = $row12['temp'];
   $hum = $row12['hum'];
   $cotwo = $row12['cotwo'];
   $pma = $row12['pma'];
   $pmb = $row12['pmb'];
   $pmc = $row12['pmc'];
   }
   
// Time stuff:
$localTime = time();
//echo(date("M-d h:i:s",$localTime));
$timestamp2 = strtotime($time_stamp);
$timeDifference = $localTime - $timestamp2;
// echo $timeDifference;

// Retrieve data from database 
$sql2="SELECT * FROM mushrooms  ORDER BY id DESC LIMIT 100";
$result2=mysql_query($sql2);


?>

<style type="text/css">
<!--
.style1 {font-size: 10px}  <!-- Data font size -->
-->
</style>

<style type="text/css">
<!--
.style2 {font-size: 10px}  <!-- Readings font size -->
-->
</style>

<style type="text/css">
<!--
.style3 {font-size: 14px; text-decoration: underline; font-weight: bold; opacity: 0.7}  <!-- Heading -->
-->
</style>

<style type="text/css">
.blink_me {
  color: green;
  font-size: 14px
  font-weight: bold;
  animation: blinker 1s linear infinite;
}

@keyframes blinker {
  50% {
    opacity: 0;
  }
}
</style>

<body>
	
<table width="580">
  <tr><span class="style2">
    <td><div align="center"><span class="style3">Mushroom Container Data</td>
  </tr>
</table>

<table width="580">
  <tr><span class="style2">
    <td><span class="style2">Last update: <?php echo(date("M-d H:i:s",$timestamp2)); ?></td>
    <td><span class="style2">UTC (GMT) time: <?php echo(date("M-d H:i:s",$localTime)); ?></td>
	<?php

	if ($timeDifference < "1200")
	{
		?> <td><div align="center"><div class="blink_me">NOW LIVE !</div></td> <?php
	} else {
		?> <td><div align="right"><span class="style2">NOT LIVE</td><td><span class="style2">... Please check later.</td> <?php
	}
	?>
    
  </tr>
  <tr>
	<td><span class="style2">Humidity: <?php echo $hum; ?> %</td>
    <td><span class="style2">Temp: <?php echo $temp; ?> ℃</td>
    <td><span class="style2"><div align="left"></div>CO2: <?php echo $cotwo; ?> ppm/10</td>
    <td><div align="right"></div><span class="style2">PMA: <?php echo $pma; ?></td>
  </tr>
</table>


<table width="580" border="1" cellspacing="0" cellpadding="0">
	<tr>
		<td width="6%"><span class="style1"><div align="center">Id </div></td>
		<td width="12%"><span class="style1"><div align="center">Time Stamp </div></td>
		<td width="9%"><span class="style1"><div align="center">Temp </div></td>
		<td width="8%"><span class="style1"><div align="center">Humidity </div></td>
		<td width="7%"><span class="style1"><div align="center">CO2/10 </div></td>
		<td width="7%"><span class="style1"><div align="center">PMA </div></td>
		<td width="7%"><span class="style1"><div align="center">PMB </div></td>
		<td width="7%"><span class="style1"><div align="center">PMC </div></td>  
	</tr>
</table>
<table width="580" border="1" cellspacing="0" cellpadding="0"> 
 
<?php

// Start looping rows in mysql database.
while($rows=mysql_fetch_array($result2))
{

?>

 <tr>
 <td bgcolor="#cce2ff" width="6%"><div align="center"><span class="style1"><? echo $rows['ID']; ?></span></td>
 <td bgcolor="#FFFFCC" width="12%"><div align="center"><span class="style1"><? echo $rows['TIME']; ?></span></td>
 <td bgcolor="#ccffcd" width="9%"><div align="center"><span class="style1"><? echo $rows['temp']; ?></span></td>
 <td bgcolor="#ffccd9" width="8%"><div align="center"><span class="style1"><? echo $rows['hum']; ?></span></td>
 <td bgcolor="#cce2ff" width="7%"><div align="center"><span class="style1"><? echo $rows['cotwo']; ?></span></td>
 <td bgcolor="#FFFFCC" width="7%"><div align="center"><span class="style1"><? echo $rows['pma']; ?></span></td>
 <td bgcolor="#FFFFCC" width="7%"><div align="center"><span class="style1"><? echo $rows['pmb']; ?></span></td>
 <td bgcolor="#FFFFCC" width="7%"><div align="center"><span class="style1"><? echo $rows['pmc']; ?></span></td>
 </tr>

<?php
// close while loop 
}

?>
</table>
</body>
</html>

<?php
// close MySQL connection 
mysql_close();
 ?>
