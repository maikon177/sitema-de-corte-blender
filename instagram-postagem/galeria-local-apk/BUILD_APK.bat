@echo off
setlocal
set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
set "GRADLE_BIN=%USERPROFILE%\.gradle\wrapper\dists\gradle-8.14.3-all\10utluxaxniiv4wxiphsi49nj\gradle-8.14.3\bin\gradle.bat"
cd /d "D:\intagram postagem\galeria-local-apk"
"%GRADLE_BIN%" assembleDebug
endlocal
