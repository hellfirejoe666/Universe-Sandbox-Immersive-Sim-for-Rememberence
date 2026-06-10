# Hybrid Router PowerShell Wrapper
# Usage: .\router.ps1 "<query>" [--force fast|smart|cloud] [--learn pattern response] [--stats]

param(
    [Parameter(Position=0)]
    [string]$Query,
    
    [string]$Force,
    
    [switch]$Learn,
    
    [switch]$Stats,
    
    [switch]$Interactive
)

$RouterScript = "D:\Ollama\OpenClaw\workspace\hybrid-router\router.py"
$PythonExe = "python"

# Build command
$Args = @($RouterScript)

if ($Stats) {
    $Args += "--stats"
} elseif ($Learn -and $Query) {
    # Learn mode: Query contains pattern, second param is response
    $Args += "--learn"
    $Args += $Query
    $Args += $Force  # In learn mode, Force parameter holds the response
} elseif ($Force) {
    $Args += $Query
    $Args += "--force"
    $Args += $Force
} elseif ($Query) {
    $Args += $Query
} elseif ($Interactive) {
    $Args += "--interactive"
}

# Run with UTF-8 output
& $PythonExe $Args 2>&1 | Out-String
