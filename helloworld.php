<?php

$timeNow = time();
$html = '<html>'
		.'<head>'
		.'<title>Welcome to ColinCC</title>'
		.'</head>'
		.'<body>'
		.'<h1>Welcome to ColinCC</h1>'
		.''
		.'Current time is: '.date('d.m.Y - H:i:s',$timeNow)
		.'</body>'
		.'</html>';
  

  echo $html;

