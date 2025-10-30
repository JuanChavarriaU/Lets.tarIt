import streamlit as st
import tarfile
import tempfile
import os
import zipfile
from pathlib import Path
import shutil
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="TAR Compressor/Decompressor",
    page_icon="📦",
    layout="wide"
)

st.title("📦 TAR Compressor/Decompressor")
st.markdown("---")

# Crear dos columnas principales
col1, col2 = st.columns(2)

with col1:
    st.header("🗜️ Comprimir archivos a TAR")
    
    # Subir múltiples archivos
    uploaded_files = st.file_uploader(
        "Selecciona los archivos que deseas comprimir:",
        accept_multiple_files=True,
        key="compress_files"
    )
    
    if uploaded_files:
        st.success(f"Se han seleccionado {len(uploaded_files)} archivos:")
        
        # Mostrar lista de archivos
        for file in uploaded_files:
            st.write(f"• {file.name} ({file.size} bytes)")
        
        # Nombre del archivo TAR
        tar_name = st.text_input(
            "Nombre del archivo TAR (sin extensión):",
            value="archivo_comprimido",
            key="tar_name"
        )
        
        # Tipo de compresión
        compression_type = st.selectbox(
            "Tipo de compresión:",
            ["Ninguna (.tar)", "GZIP (.tar.gz)", "BZIP2 (.tar.bz2)"],
            key="compression"
        )
        
        if st.button("🗜️ Crear archivo TAR", key="compress_btn"):
            try:
                # Determinar modo y extensión
                if compression_type == "GZIP (.tar.gz)":
                    mode = "w:gz"
                    extension = ".tar.gz"
                elif compression_type == "BZIP2 (.tar.bz2)":
                    mode = "w:bz2"
                    extension = ".tar.bz2"
                else:
                    mode = "w"
                    extension = ".tar"
                
                # Crear archivo TAR en memoria
                tar_buffer = BytesIO()
                
                with tarfile.open(fileobj=tar_buffer, mode=mode) as tar:
                    for uploaded_file in uploaded_files:
                        # Crear info del archivo
                        tarinfo = tarfile.TarInfo(name=uploaded_file.name)
                        tarinfo.size = uploaded_file.size
                        
                        # Resetear puntero del archivo
                        uploaded_file.seek(0)
                        
                        # Añadir archivo al TAR
                        tar.addfile(tarinfo, uploaded_file)
                
                # Preparar descarga
                tar_buffer.seek(0)
                final_name = f"{tar_name}{extension}"
                
                st.download_button(
                    label=f"⬇️ Descargar {final_name}",
                    data=tar_buffer.getvalue(),
                    file_name=final_name,
                    mime="application/x-tar"
                )
                
                st.success(f"✅ Archivo TAR creado exitosamente: {final_name}")
                
            except Exception as e:
                st.error(f"❌ Error al crear el archivo TAR: {str(e)}")

with col2:
    st.header("📂 Descomprimir archivo TAR")
    
    # Subir archivo TAR
    uploaded_tar = st.file_uploader(
        "Selecciona el archivo TAR que deseas descomprimir:",
        type=['tar', 'gz', 'bz2'],
        key="decompress_file"
    )
    
    if uploaded_tar:
        st.success(f"Archivo seleccionado: {uploaded_tar.name}")
        
        if st.button("📂 Descomprimir archivo TAR", key="decompress_btn"):
            try:
                # Determinar modo de lectura
                uploaded_tar.seek(0)
                
                # Intentar abrir el archivo TAR
                try:
                    tar = tarfile.open(fileobj=uploaded_tar, mode='r:*')
                except tarfile.ReadError:
                    st.error("❌ El archivo no es un TAR válido o está corrupto")
                    st.stop()
                
                # Obtener lista de archivos
                members = tar.getmembers()
                
                if not members:
                    st.warning("⚠️ El archivo TAR está vacío")
                    tar.close()
                    st.stop()
                
                st.success(f"✅ Archivo TAR válido con {len(members)} elementos:")
                
                # Crear expander para mostrar contenido
                with st.expander("Ver contenido del archivo TAR"):
                    for member in members:
                        if member.isfile():
                            st.write(f"📄 {member.name} ({member.size} bytes)")
                        elif member.isdir():
                            st.write(f"📁 {member.name}/")
                        else:
                            st.write(f"🔗 {member.name} (enlace)")
                
                # Crear ZIP con los archivos descomprimidos para descarga
                zip_buffer = BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for member in members:
                        if member.isfile():
                            # Extraer archivo
                            file_obj = tar.extractfile(member)
                            if file_obj:
                                # Añadir al ZIP
                                zip_file.writestr(member.name, file_obj.read())
                
                tar.close()
                
                # Preparar descarga del ZIP
                zip_buffer.seek(0)
                zip_name = f"{Path(uploaded_tar.name).stem}_extraido.zip"
                
                st.download_button(
                    label=f"⬇️ Descargar archivos extraídos ({zip_name})",
                    data=zip_buffer.getvalue(),
                    file_name=zip_name,
                    mime="application/zip"
                )
                
                st.info("ℹ️ Los archivos se han empaquetado en un ZIP para facilitar la descarga")
                
            except Exception as e:
                st.error(f"❌ Error al descomprimir el archivo TAR: {str(e)}")

# Información adicional
st.markdown("---")
st.markdown("### ℹ️ Información")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.markdown("""
    **Formatos soportados para compresión:**
    - `.tar` - Sin compresión
    - `.tar.gz` - Compresión GZIP
    - `.tar.bz2` - Compresión BZIP2
    """)

with info_col2:
    st.markdown("""
    **Formatos soportados para descompresión:**
    - `.tar`, `.tar.gz`, `.tar.bz2`
    - Los archivos extraídos se descargan como ZIP
    """)

st.markdown("---")
st.markdown("**Nota:** Esta aplicación funciona completamente en el navegador y no requiere instalaciones adicionales.")

# Instrucciones de uso
with st.expander("📖 Instrucciones de uso"):
    st.markdown("""
    ### Para comprimir archivos:
    1. Selecciona uno o varios archivos usando el botón "Browse files"
    2. Escribe el nombre que deseas para tu archivo TAR
    3. Selecciona el tipo de compresión
    4. Haz clic en "Crear archivo TAR"
    5. Descarga el archivo resultante
    
    ### Para descomprimir archivos:
    1. Selecciona un archivo TAR (.tar, .tar.gz, o .tar.bz2)
    2. Haz clic en "Descomprimir archivo TAR"
    3. Revisa el contenido en la sección expandible
    4. Descarga los archivos extraídos como ZIP
    
    ### Limitaciones:
    - El tamaño máximo de archivo depende de la configuración del servidor
    - Los archivos grandes pueden tardar más en procesarse
    - La extracción se proporciona como ZIP para facilitar la descarga múltiple
    """)

# Footer
st.markdown("---")
st.markdown("*Desarrollado por J4 - TAR Compressor/Decompressor v1.0*")
