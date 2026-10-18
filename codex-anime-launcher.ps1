Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$imagePath = 'C:\Users\周驰宇\.codex\generated_images\01a12f4f-0c30-7c31-b314-84ba3a7f9870\exec-01650acf-74c1-48f1-8a7c-0cbf88021088.png'
$form = New-Object Windows.Forms.Form
$form.FormBorderStyle = 'None'; $form.StartPosition = 'CenterScreen'; $form.TopMost = $true; $form.ShowInTaskbar = $false; $form.Width = 900; $form.Height = 506
$img = [Drawing.Image]::FromFile($imagePath); $form.BackgroundImage = $img; $form.BackgroundImageLayout = 'Stretch'; $form.Show(); [Windows.Forms.Application]::DoEvents(); Start-Sleep -Milliseconds 2200; $form.Close(); $img.Dispose(); Start-Process 'explorer.exe' 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'
