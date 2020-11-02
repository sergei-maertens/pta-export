<?php

define('ENDPOINT', 'https://pta-export.regex-it.nl/api/export');

define('TOKEN', getenv('TOKEN') ?: 'dummy-token');

function getExport($jaar, $klas)
{
    echo "Getting export for jaar $jaar and klas $klas\n";

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


$response = getExport('2019', '1');
// var_dump($response);

header('Content-Description: File Transfer');
header('Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document');
header('Content-Disposition: attachment; filename=export-2019-1.docx');
header('Content-Transfer-Encoding: binary');
header('Expires: 0');
header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
header('Pragma: public');
header('Content-Length: ' . strlen($response));
ob_clean();
flush();
echo $response;
flush();

?>
