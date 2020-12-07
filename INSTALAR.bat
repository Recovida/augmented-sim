@echo off
python -m pip install -r requirements.txt
python setup.py install
cls
echo "O programa foi instalado. Pressione qualquer tecla para fechar." 
pause >NUL