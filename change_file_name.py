import os

collection="C:\Users\Jhayne\OneDrive\Área de Trabalho\IA Reconhecimento Facial\Driver-Drowsiness-Detection\train\Closed"
collection1="C:\Users\Jhayne\OneDrive\Área de Trabalho\IA Reconhecimento Facial\Driver-Drowsiness-Detection\train\Open"

for file in os.listdir(collection):
    os.rename(collection+file,f'{collection}closed.{file}')

for file in os.listdir(collection1):
    os.rename(collection1+file,f'{collection1}open.{file}')