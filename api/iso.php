<?php

function render($data=[], $message='OK', $status_code=200) {
    header('Access-Control-Allow-Origin: '.'*');
    header('Content-Type: '.'application/json');
    http_response_code($status_code);

    $response = [
    	'message' => $message,
    	'data' => $data
    ];

    echo(json_encode($response));

    exit();
}

if ($_SERVER['REQUEST_METHOD'] == 'GET') {
	// Check if iso exists
	if (!array_key_exists('iso', $_GET)) {
		render([], 'Parameter "iso" is necessary - ISO code of country', 400);
	}

	// Open database
	$pdo = new PDO('sqlite:covid.db');

	// Get all data from coutry
	$stmt = $pdo->prepare('SELECT * FROM dataset WHERE (iso=?)');
	$stmt->execute([strtoupper($_GET['iso'])]);

	$result = [];

	// Create data
	while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
		$res = [];

		foreach ($row as $key => $value) {
			if (($key == 'name') || ($key == 'iso') || ($key == 'date') || ($value == '') || ($value == '0')) {
				continue;
			} else {
				$res[$key] = $value;
			}
		}

		$result[$row['date']] = $res;
	}

	if (count($result) == 0) {
		render([], 'ISO code of country not found', 400);
	}

	render($result);

} else {
	render([], 'Only GET method is allowed', 405);
}

