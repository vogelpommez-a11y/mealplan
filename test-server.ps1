# Kleiner lokaler Test-Server für Paddy's Mealplan
# Startet http://localhost:8000/ und liefert die Dateien aus diesem Ordner aus.
# Stoppen: dieses Fenster schließen oder Strg+C.

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$port = 8000
$prefix = "http://localhost:$port/"

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
try {
  $listener.Start()
} catch {
  Write-Host "Konnte Server nicht starten: $($_.Exception.Message)" -ForegroundColor Red
  Write-Host "Vermutlich ist Port $port belegt. Schließe andere Server oder starte neu."
  exit 1
}

Write-Host ""
Write-Host "  Test-Server läuft:  $prefix" -ForegroundColor Green
Write-Host "  Ordner:             $root"
Write-Host "  Zum Beenden dieses Fenster schließen (oder Strg+C)."
Write-Host ""

$mime = @{
  ".html" = "text/html; charset=utf-8"
  ".js"   = "application/javascript; charset=utf-8"
  ".css"  = "text/css; charset=utf-8"
  ".json" = "application/json; charset=utf-8"
  ".png"  = "image/png"
  ".jpg"  = "image/jpeg"
  ".jpeg" = "image/jpeg"
  ".svg"  = "image/svg+xml"
  ".ico"  = "image/x-icon"
}

while ($listener.IsListening) {
  try {
    $context = $listener.GetContext()
    $req = $context.Request
    $res = $context.Response

    $rel = [System.Uri]::UnescapeDataString($req.Url.AbsolutePath.TrimStart('/'))
    if ([string]::IsNullOrWhiteSpace($rel)) { $rel = "index.html" }
    $path = Join-Path $root $rel

    if (Test-Path $path -PathType Leaf) {
      $ext = [System.IO.Path]::GetExtension($path).ToLower()
      if ($mime.ContainsKey($ext)) { $res.ContentType = $mime[$ext] }
      $bytes = [System.IO.File]::ReadAllBytes($path)
      $res.ContentLength64 = $bytes.Length
      $res.OutputStream.Write($bytes, 0, $bytes.Length)
      Write-Host ("200  " + $rel)
    } else {
      $res.StatusCode = 404
      $msg = [System.Text.Encoding]::UTF8.GetBytes("404 - nicht gefunden: $rel")
      $res.OutputStream.Write($msg, 0, $msg.Length)
      Write-Host ("404  " + $rel) -ForegroundColor Yellow
    }
    $res.OutputStream.Close()
  } catch {
    # Einzelne fehlerhafte Anfrage ignorieren, Server weiterlaufen lassen
  }
}
