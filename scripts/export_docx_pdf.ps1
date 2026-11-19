param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Pdf,
    [Parameter(Mandatory = $true)][int]$ExpectedPages,
    [Parameter(Mandatory = $true)][string]$RequiredPairsJson,
    [switch]$AllowOverflowPreview
)

$ErrorActionPreference = 'Stop'
$word = $null
$document = $null

function Find-ParagraphPage([object]$Document, [string]$Marker) {
    foreach ($paragraph in $Document.Paragraphs) {
        if ($paragraph.Range.Text.Contains($Marker, [StringComparison]::OrdinalIgnoreCase)) {
            return $paragraph.Range.Information(3)
        }
    }
    throw "Required layout marker not found: $Marker"
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($Source, $false, $true, $false)
    $pageCount = $document.ComputeStatistics(2)
    if ($pageCount -ne $ExpectedPages) {
        $message = "Text does not fit the fixed template: expected $ExpectedPages pages, got $pageCount."
        if ($AllowOverflowPreview) { Write-Warning $message } else { throw "$message No PDF was exported." }
    }
    foreach ($paragraph in $document.Paragraphs) {
        if (-not $paragraph.Range.Text.Trim()) { continue }
        $content = $document.Range($paragraph.Range.Start, [Math]::Max($paragraph.Range.Start, $paragraph.Range.End - 1))
        $content.Collapse(0)
        if ($paragraph.Range.Information(3) -ne $content.Information(3)) {
            $message = "A paragraph crosses a page boundary: $($paragraph.Range.Text.Trim())"
            if ($AllowOverflowPreview) { Write-Warning $message } else { throw "$message No PDF was exported." }
        }
    }
    foreach ($pair in (ConvertFrom-Json -InputObject $RequiredPairsJson)) {
        $markers = $pair.Split('|', 2)
        if ($markers.Count -ne 2) { throw "Invalid page-pair check: $pair" }
        $companyPage = Find-ParagraphPage $document $markers[0]
        $bulletPage = Find-ParagraphPage $document $markers[1]
        if ($companyPage -ne $bulletPage) {
            $message = "Layout overflow: '$($markers[0])' and its first bullet moved to different pages."
            if ($AllowOverflowPreview) { Write-Warning $message } else { throw "$message No PDF was exported." }
        }
    }
    $document.ExportAsFixedFormat($Pdf, 17)
    Write-Output "Exported $Pdf ($pageCount pages)"
}
catch {
    Write-Error $_
    exit 1
}
finally {
    if ($document -ne $null) {
        $document.Close(0)
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }
    if ($word -ne $null) {
        $word.Quit()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
}
