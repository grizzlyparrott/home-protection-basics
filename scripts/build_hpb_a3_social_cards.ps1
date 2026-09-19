$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$root = Split-Path -Parent $PSScriptRoot
$output = Join-Path $root 'assets\hpb-a3\social'
New-Item -ItemType Directory -Force -Path $output | Out-Null

$cards = @(
    [pscustomobject]@{ Slug='smoke-alarm-placement'; Title='Smoke alarm placement'; Subtitle='General home guidance; local rules and manufacturer instructions control.'; Kind='house' }
    [pscustomobject]@{ Slug='smoke-alarm-types'; Title='Photoelectric vs. ionization'; Subtitle='Compare alarm technologies without treating either as a universal answer.'; Kind='compare' }
    [pscustomobject]@{ Slug='replace-smoke-alarms'; Title='When to replace a smoke alarm'; Subtitle='A practical replacement flow that keeps the manufacturer in charge.'; Kind='flow' }
    [pscustomobject]@{ Slug='hardwired-vs-battery'; Title='Hardwired vs. battery alarms'; Subtitle='Compare power approaches and know when qualified electrical work is needed.'; Kind='compare' }
    [pscustomobject]@{ Slug='smoke-alarm-chirp'; Title='Why smoke alarms chirp'; Subtitle='Troubleshoot safely, then follow the product manual or get help.'; Kind='flow' }
    [pscustomobject]@{ Slug='security-system-layers'; Title='Home security systems'; Subtitle='A layered view of deterrence, detection, response, and safe habits.'; Kind='layers' }
    [pscustomobject]@{ Slug='window-lock-balance'; Title='Window lock types'; Subtitle='Match the lock to the window, escape needs, and manufacturer limits.'; Kind='layers' }
    [pscustomobject]@{ Slug='diy-vs-professional'; Title='DIY vs. professional security'; Subtitle='Compare support, monitoring, installation, and your own responsibilities.'; Kind='compare' }
    [pscustomobject]@{ Slug='power-outage-safety'; Title='Power outage basics'; Subtitle='A safety-first flow for food, generators, and household readiness.'; Kind='flow' }
    [pscustomobject]@{ Slug='power-outage-checklist'; Title='Power outage readiness checklist'; Subtitle='A practical family checklist for before, during, and after an outage.'; Kind='checklist' }
)

function Color([string]$hex) { [System.Drawing.ColorTranslator]::FromHtml($hex) }

function Draw-Text([System.Drawing.Graphics]$g, [string]$text, [System.Drawing.Font]$font, [System.Drawing.Brush]$brush, [float]$x, [float]$y, [float]$width, [float]$height) {
    $format = New-Object System.Drawing.StringFormat
    $format.Trimming = [System.Drawing.StringTrimming]::EllipsisWord
    $g.DrawString($text, $font, $brush, (New-Object System.Drawing.RectangleF($x, $y, $width, $height)), $format)
    $format.Dispose()
}

foreach ($card in $cards) {
    $bitmap = New-Object System.Drawing.Bitmap 1200, 675
    $g = [System.Drawing.Graphics]::FromImage($bitmap)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear((Color '#0f1520'))
    $g.FillRectangle((New-Object System.Drawing.SolidBrush (Color '#13253a')), 0, 0, 1200, 124)

    $white = New-Object System.Drawing.SolidBrush (Color '#ffffff')
    $muted = New-Object System.Drawing.SolidBrush (Color '#c8d8ea')
    $blue = New-Object System.Drawing.SolidBrush (Color '#8bc5ff')
    $mint = New-Object System.Drawing.SolidBrush (Color '#85d6b6')
    $gold = New-Object System.Drawing.SolidBrush (Color '#f5b971')
    $line = New-Object System.Drawing.Pen (Color '#365575'), 2
    $titleFont = New-Object System.Drawing.Font 'Arial', 39, ([System.Drawing.FontStyle]::Bold)
    $subFont = New-Object System.Drawing.Font 'Arial', 23, ([System.Drawing.FontStyle]::Regular)
    $labelFont = New-Object System.Drawing.Font 'Arial', 18, ([System.Drawing.FontStyle]::Bold)
    $smallFont = New-Object System.Drawing.Font 'Arial', 16, ([System.Drawing.FontStyle]::Regular)

    $g.DrawString('HOME PROTECTION BASICS', $labelFont, $blue, 56, 42)
    $g.DrawString('FACTUAL GUIDE', $labelFont, $mint, 930, 42)
    Draw-Text $g $card.Title $titleFont $white 56 165 700 140
    Draw-Text $g $card.Subtitle $subFont $muted 60 300 645 130

    $g.DrawLine($line, 56, 510, 1144, 510)
    $g.DrawString('General guidance - verify product instructions, local requirements, and emergency advice.', $smallFont, $muted, 56, 550)

    switch ($card.Kind) {
        'house' {
            $house = New-Object System.Drawing.SolidBrush (Color '#17324d')
            $roofPen = New-Object System.Drawing.Pen (Color '#8bc5ff'), 5
            $points = [System.Drawing.Point[]]@((New-Object System.Drawing.Point 790, 440), (New-Object System.Drawing.Point 790, 302), (New-Object System.Drawing.Point 955, 200), (New-Object System.Drawing.Point 1110, 302), (New-Object System.Drawing.Point 1110, 440))
            $g.FillPolygon($house, $points); $g.DrawLines($roofPen, $points)
            foreach ($p in @(@(858,345), @(1025,345), @(952,392))) { $g.FillEllipse($gold, $p[0], $p[1], 38, 38); $g.FillEllipse((New-Object System.Drawing.SolidBrush (Color '#0f1520')), $p[0]+13, $p[1]+13, 12, 12) }
            $house.Dispose(); $roofPen.Dispose()
        }
        'compare' {
            foreach ($x in @(780, 967)) { $g.FillRectangle((New-Object System.Drawing.SolidBrush (Color '#17324d')), $x, 234, 155, 180); $g.DrawRectangle($line, $x, 234, 155, 180) }
            $g.DrawString('COMPARE', $labelFont, $blue, 816, 276); $g.DrawString('OPTIONS', $labelFont, $gold, 1003, 276)
            $g.DrawLine((New-Object System.Drawing.Pen (Color '#85d6b6'), 5), 936, 324, 966, 324)
        }
        'flow' {
            foreach ($x in @(770, 918, 1066)) { $g.FillEllipse((New-Object System.Drawing.SolidBrush (Color '#17324d')), $x, 287, 92, 92); $g.DrawEllipse((New-Object System.Drawing.Pen (Color '#8bc5ff'), 4), $x, 287, 92, 92) }
            $g.DrawString('1', $titleFont, $blue, 800, 299); $g.DrawString('2', $titleFont, $gold, 948, 299); $g.DrawString('3', $titleFont, $mint, 1096, 299)
            $g.DrawLine((New-Object System.Drawing.Pen (Color '#85d6b6'), 5), 865, 333, 913, 333); $g.DrawLine((New-Object System.Drawing.Pen (Color '#85d6b6'), 5), 1013, 333, 1061, 333)
        }
        'layers' {
            foreach ($r in @(142, 100, 58)) { $g.DrawEllipse((New-Object System.Drawing.Pen (Color '#8bc5ff'), 4), 941-$r, 332-$r, 2*$r, 2*$r) }
            $g.FillRectangle($gold, 919, 337, 44, 54); $g.FillPolygon($gold, [System.Drawing.Point[]]@((New-Object System.Drawing.Point 909,337),(New-Object System.Drawing.Point 941,309),(New-Object System.Drawing.Point 973,337)))
        }
        'checklist' {
            for ($i = 0; $i -lt 4; $i++) { $y = 222 + ($i * 52); $g.DrawRectangle((New-Object System.Drawing.Pen (Color '#85d6b6'), 4), 792, $y, 25, 25); $g.DrawLine((New-Object System.Drawing.Pen (Color '#f5b971'), 4), 833, $y+13, 1082, $y+13) }
        }
    }

    $path = Join-Path $output ($card.Slug + '.png')
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bitmap.Dispose(); $white.Dispose(); $muted.Dispose(); $blue.Dispose(); $mint.Dispose(); $gold.Dispose(); $line.Dispose(); $titleFont.Dispose(); $subFont.Dispose(); $labelFont.Dispose(); $smallFont.Dispose()
    Write-Output $path
}
