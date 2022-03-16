@echo off
if "%1" == "h" goto begin
start mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin
start D:\ZhuanYe_SoftWare\neo4j-community-3.5.22\bin\neo4j.bat console