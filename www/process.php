<?php 

$param = $_POST["text"];

$command = escapeshellcmd('python3 ../src/CustomSearch.py "'.$param.'"');
$output = shell_exec($command);
echo $output;

?>