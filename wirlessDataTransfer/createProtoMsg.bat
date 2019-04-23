SET currDir=%cd%
SET teensyDir="C:\Users\Ahmad\Documents\Arduino\teensyClient"
SET nanoprotoc="C:\Users\Ahmad\Documents\Arduino\libraries\nanopb\generator-bin\protoc"
SET nsnopbdest="C:\Users\Ahmad\Documents\Arduino\libraries\pbimumsg"
ECHO %currDir%

protoc -I=%cd% --python_out=%cd%\release %cd%\imumsg.proto

%nanoprotoc% -I=%cd% --nanopb_out=%cd%\release %cd%\imumsg.proto
copy %cd%\release\imumsg.pb.c %nsnopbdest%
copy %cd%\release\imumsg.pb.h %nsnopbdest%
PAUSE							

rem C:\Users\Ahmad\Documents\Arduino\teensyClient\nanopb-0.3.9-windows-x86\nanopb-0.3.9-windows-x86\generator-bin