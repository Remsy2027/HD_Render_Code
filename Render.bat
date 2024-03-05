@echo off
setlocal

set email=%~1

REM Extract the username from the email address
for /F "tokens=1 delims=@" %%G in ("%email%") do set "username=%%G"

set script_path="Render.py"
set output_path="C:\Users\Remsy\PycharmProjects\BlenderCycles\Assets\Render_Images\%username%_Render_Image.png"

REM Run Blender to render the image
"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe" -b -P "%script_path%" -- "%email%"

REM Send the rendered image via email
python "send_email.py" "%email%" "%output_path%"

endlocal

