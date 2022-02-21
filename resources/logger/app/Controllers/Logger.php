<?php

namespace App\Controllers;

class Logger extends BaseController
{

    static $log_file = "./actions.log";

    public function index()
    {
        echo "<pre>".file_get_contents(self::$log_file)."</pre>";

    }

    public function log($story, $user, $msg)
    {        
        $txt = sprintf("%s\t%s\t%s\t%s\n", date("Y-m-d:h:i:s"), $story, $user, $msg);
        $fout = fopen(self::$log_file, "a");
        fwrite($fout,$txt);
        fclose($fout);
        echo "WROTE ".$txt;   
    }
}