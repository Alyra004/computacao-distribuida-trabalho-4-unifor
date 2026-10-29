<?php
$api_endpoint = getenv("API_ENDPOINT") ?: "http://api:5000/api/";
$url = isset($_GET["url"]) ? trim($_GET["url"]) : "";
$links = null;
$error = null;

if (!empty($url)) {
    $api_url = rtrim($api_endpoint, "/") . "/" . $url;
    $context = stream_context_create([
        "http" => [
            "timeout" => 15,
            "header" => "Accept: application/json\r\n"
        ]
    ]);
    $response = @file_get_contents($api_url, false, $context);
    if ($response === false) {
        $error = "Não foi possível extrair links da URL fornecida através da API.";
    } else {
        $links = json_decode($response, true);
    }
}
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Extractor</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; background-color: #f7fafc; color: #2d3748; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { margin-top: 0; color: #2b6cb0; }
        form { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="url"] { flex: 1; padding: 10px; border: 1px solid #cbd5e0; border-radius: 4px; font-size: 16px; }
        button { padding: 10px 20px; background-color: #3182ce; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #2b6cb0; }
        .error { background-color: #fed7d7; color: #c53030; padding: 12px; border-radius: 4px; margin-bottom: 20px; }
        .summary { background-color: #edf2f7; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #e2e8f0; }
        th { background-color: #f7fafc; }
        a { color: #3182ce; text-decoration: none; word-break: break-all; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
<div class="container">
    <h1>Link Extractor</h1>
    <form method="GET" action="">
        <input type="url" name="url" placeholder="http://example.com" value="<?php echo htmlspecialchars($url); ?>" required>
        <button type="submit">Extrair Links</button>
    </form>

    <?php if ($error): ?>
        <div class="error"><?php echo htmlspecialchars($error); ?></div>
    <?php endif; ?>

    <?php if ($links !== null): ?>
        <div class="summary">
            <strong>Página consultada:</strong> <?php echo htmlspecialchars($url); ?><br>
            <strong>Total de links encontrados:</strong> <?php echo count($links); ?>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Texto Âncora</th>
                    <th>Hiperlink (Href)</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($links as $link): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($link["text"] ?? ""); ?></td>
                        <td><a href="<?php echo htmlspecialchars($link["href"] ?? ""); ?>" target="_blank" rel="noopener noreferrer"><?php echo htmlspecialchars($link["href"] ?? ""); ?></a></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    <?php endif; ?>
</div>
</body>
</html>
