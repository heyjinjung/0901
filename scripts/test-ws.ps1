# Usage:
#   .\scripts\test-ws.ps1 -UserId 1 -Topics "alpha,beta" -LastEventId 1
# Optional: -Host http://localhost:8000 (ws scheme will be derived)

param(
  [int]$UserId = 1,
  [string]$Topics = "",
  [int]$LastEventId = -1,
  [string]$Host = "http://localhost:8000"
)

$ErrorActionPreference = 'Stop'

function Get-WsUri([string]$host,[int]$uid,[string]$topics,[int]$lei){
  $wsHost = $host -replace '^http','ws'
  $qs = @()
  if($topics){ $qs += "topics=$topics" }
  if($lei -ge 0){ $qs += "lastEventId=$lei" }
  $q = if($qs.Count -gt 0){ '?' + ($qs -join '&') } else { '' }
  return "$wsHost/ws/notifications/$uid$q"
}

Add-Type -AssemblyName System.Net.WebSockets.Client
$c = New-Object System.Net.WebSockets.ClientWebSocket
$cts = New-Object System.Threading.CancellationTokenSource
$uri = [uri](Get-WsUri -host $Host -uid $UserId -topics $Topics -lei $LastEventId)
Write-Host "Connecting to $uri" -ForegroundColor Cyan
$c.ConnectAsync($uri,$cts.Token).GetAwaiter().GetResult() | Out-Null

function Send-Json([object]$obj){
  $json = ($obj | ConvertTo-Json -Depth 5 -Compress)
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
  $seg = [System.ArraySegment[byte]]::new($bytes)
  $c.SendAsync($seg,[System.Net.WebSockets.WebSocketMessageType]::Text,$true,$cts.Token).GetAwaiter().GetResult() | Out-Null
}

function Recv-Once(){
  $buffer = New-Object byte[] 8192
  $segment = [System.ArraySegment[byte]]::new($buffer)
  $ms = New-Object System.IO.MemoryStream
  do {
    $res = $c.ReceiveAsync($segment,$cts.Token).GetAwaiter().GetResult()
    $ms.Write($buffer,0,$res.Count)
  } while(-not $res.EndOfMessage)
  $txt = [System.Text.Encoding]::UTF8.GetString($ms.ToArray())
  $ms.Dispose()
  return $txt
}

# Demonstrate subscribe/unsubscribe flow
if($Topics){
  Write-Host "Subscribing to extra topic: gamma; unsubscribing from first topic if provided" -ForegroundColor Yellow
  Send-Json @{ type = 'subscribe'; topics = @('gamma') }
  Start-Sleep -Milliseconds 150
  $first = $Topics.Split(',')[0]
  if($first){ Send-Json @{ type = 'unsubscribe'; topics = @($first) } }
}

# Try to receive a couple of messages (best-effort)
$messages = @()
for($i=0;$i -lt 2;$i++){
  if($c.State -eq [System.Net.WebSockets.WebSocketState]::Open){
    try { $messages += (Recv-Once) } catch { break }
  }
}
$c.Dispose()

Write-Output ($messages -join "`n")
