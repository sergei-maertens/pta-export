<?php

define('ENDPOINT', 'https://pta-export.regex-it.nl/api/export');

define('TOKEN', getenv('TOKEN') ?: 'dummy-token');

function getExport($jaar, $klas, $outfile)
{
    echo "Getting export for jaar $jaar and klas $klas\n";

    // $fp = fopen($outfile, "wb");

    $params = array(
        'jaar' => $jaar,
        'klas' => $klas,
    );
    $headers = array(
        'Authorization: Token ' . TOKEN,
    );

    $ch = curl_init(ENDPOINT);
    // curl_setopt($ch, CURLOPT_FILE, $fp);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $params);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER , true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 60 * 5);

    $response = curl_exec($ch);
    if(curl_error($ch)) {
        // fwrite($fp, curl_error($ch));
        echo curl_error($ch);
        echo "\n";
    }
    curl_close($ch);
    // fclose($fp);
    return $response;
}


$response = getExport('2019', '1', '/tmp/ignored.docx');
var_dump($response);

// TODO: example on how to output this to the browser

?>
