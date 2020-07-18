<?php

function get_SEweging($type,$wg4,$wg5) {
    if ($wg4 == 0) {
        $t1 = 0;
        $n1 = 1;
    }
    elseif ($wg4 >= 1 && $wg4 <= 100) {
        $t1 = $wg4;
        $n1 = 100;
    }
    elseif ($wg4 > 100) {
        $tmp = $wg4 - 100;
        $tmp = explode("/",$listbreuk[$tmp]);
        $t1 = $tmp[0];
        $n1 = $tmp[1];
    }

    if ($wg5 == 0) {
        $t2 = 0;
        $n2 = 1;
    }
    elseif ($wg5 >= 1 && $wg5 <= 100) {
        $t2 = $wg5;
        $n2 = 100;
    }
    elseif ($wg5 > 100) {
        $tmp = $wg5 - 100;
        $tmp = explode("/", $listbreuk[$tmp]);
        $t2 = $tmp[0]; $n2 = $tmp[1];
    }

    $noemer = $n1 * $n2;
    $teller4 = $n2 * $t1;
    if ($type == "H") {
        $teller5 = $noemer - $teller4;
        $ggd = gcd($teller4,$teller5);
    }
    elseif ($type == "V") {
        $teller5 = $n1 * $t2;
        $teller6 = $noemer - $teller4 - $teller5;
        $ggd = gcd(gcd($teller4,$teller5),$teller6);
    }

    $noemer /= $ggd;
    $teller4 /= $ggd;
    $teller5 /= $ggd;
    if ($type == "V") {
        $teller6 /= $ggd;
    }
    else {
        $teller6 = 0;
    }

    return $noemer."/".$teller4."/".$teller5."/".$teller6;
}

?>
