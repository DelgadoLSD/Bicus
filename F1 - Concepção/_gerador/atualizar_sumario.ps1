# Abre o .docx no Microsoft Word (em segundo plano), preenche o sumario e salva.
# Uso: powershell -ExecutionPolicy Bypass -File atualizar_sumario.ps1
# O PDF deve ser gerado pelo proprio Word: Arquivo > Salvar como > PDF.
$raiz = Split-Path -Parent $PSScriptRoot
$docx = Get-ChildItem -LiteralPath $raiz -Filter "*.docx" | Where-Object { $_.Name -notlike "~$*" } | Select-Object -First 1

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0                  # wdAlertsNone
try {
    $doc = $word.Documents.Open($docx.FullName, $false, $false, $false)
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Save()
    $doc.Close($false)
    "Sumario atualizado: $($docx.Name)"
} finally {
    $word.Quit()
}
