<?php


class Message
{
    private $user;
    private $msg;
    private $time;

    public function __construct($user, $msg)
    {
        $this->user = $user;
        $this->msg  = $msg;
        $this->time = date('d.m.Y - H:i:s', time());
    }

    public function toString()
    {
        return $this->user . ' (' . $this->time . ') :' . $this->msg;
    }
}

?>
<html>
<head>
    <title>Welcome to ColinCC</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap-theme.min.css">
    <script src="js/bootstrap.min.js"></script>
</head>
<body>
<div class="page-header">
    <h1>ISE-Master - Oliver Colin Sauer</h1>
</div>
<div class="panel panel-default">
    <div class="panel-heading">
        <h3>
            <small>VVS - 2015</small>
        </h3>
    </div>
    <div class="panel-body">
        <form action="" method="post">
            <label>Name:</label><input type="text" class="form-control"/>
            <label>Message:</label>

            <div><textarea name="message" rows="5" cols="60"></textarea></div>
            <input type="submit" value="send ChatMessage" class="btn btn-primary"/>
        </form>
    </div>
    <div class="panel-footer">Current time is: <?= date('d.m.Y - H:i:s', time()) ?></div>
</div>
</body>
</html>


