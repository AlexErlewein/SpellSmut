# PowerShell script to fix AutoScaleMode in all Designer.cs files
# Run this script from the spellforce_data_editor directory

$designerFiles = Get-ChildItem -Path "." -Filter "*.Designer.cs" -Recurse

foreach ($file in $designerFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    $originalContent = $content

    # Replace AutoScaleMode.Font with AutoScaleMode.None
    $content = $content -replace 'AutoScaleMode = System\.Windows\.Forms\.AutoScaleMode\.Font;', 'AutoScaleMode = System.Windows.Forms.AutoScaleMode.None;'

    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        Write-Host "Fixed: $($file.FullName)"
    }
}

Write-Host "Done!"
