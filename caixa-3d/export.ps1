# export.ps1 — Compila corpo + tampa → STL via OpenSCAD headless
# Uso: .\caixa-3d\export.ps1

$ErrorActionPreference = "Continue"
$root = $PSScriptRoot
$outDir = Join-Path $root "stl"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$openscad = $null
$cmd = Get-Command openscad -ErrorAction SilentlyContinue
if ($cmd) { $openscad = $cmd.Source }
else {
  foreach ($c in @(
    "C:\Program Files\OpenSCAD\openscad.exe",
    "C:\Program Files (x86)\OpenSCAD\openscad.exe"
  )) {
    if (Test-Path $c) { $openscad = $c; break }
  }
}
if (-not $openscad) {
  Write-Host "ERRO: OpenSCAD nao encontrado. winget install OpenSCAD.OpenSCAD" -ForegroundColor Red
  exit 1
}

Write-Host "OpenSCAD: $openscad"
$parts = @("box_body", "box_lid")
foreach ($name in $parts) {
  $scad = Join-Path $root "$name.scad"
  $stl  = Join-Path $outDir "${name}_base.stl"
  if (Test-Path $stl) { Remove-Item $stl -Force }
  Write-Host "Compilando $name.scad ..." -NoNewline
  $p = Start-Process -FilePath $openscad -ArgumentList @("-o", $stl, $scad) -Wait -PassThru -NoNewWindow
  if ((Test-Path $stl) -and ((Get-Item $stl).Length -gt 1000)) {
    $kb = [math]::Round((Get-Item $stl).Length / 1KB, 1)
    Write-Host " OK ($kb KB)"
  } else {
    Write-Host " FALHOU (exit=$($p.ExitCode))"
    exit 1
  }
}

Write-Host "Aplicando relevo tribal (trimesh/manifold)..."
python (Join-Path $root "assemble_embossed.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$validate = Join-Path $root "validate_stl.py"
if (Test-Path $validate) {
  Write-Host "Validando malhas finais..."
  python $validate
}

Write-Host "Pronto: $outDir"
