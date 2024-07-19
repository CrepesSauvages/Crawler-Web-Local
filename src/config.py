import os

# Logs 

Logs_Directory = "logs"
Logs_FileName = "Crawer.log"
Log_Path = os.path.join(os.getcwd(), Logs_Directory, Logs_FileName)
Log_To_File = True
Log_To_Console = True

# Procces

Max_Webpages = 1000
Save_Interval = 100
Timeout = 10