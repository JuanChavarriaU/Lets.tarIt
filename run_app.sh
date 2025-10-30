echo "Iniciando TAR Compressor/Decompressor..."
echo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python no está instalado en este sistema."
        echo "Por favor, instala Python desde https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        echo "ERROR: pip no está disponible."
        echo "Por favor, instala pip o reinstala Python con pip incluido."
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi

echo "Instalando dependencias..."
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias."
    exit 1
fi

echo
echo "Iniciando la aplicación..."
echo "La aplicación se abrirá en tu navegador web en unos segundos..."
echo "Para cerrar la aplicación, presiona Ctrl+C en esta terminal."
echo

$PYTHON_CMD -m streamlit run app.py