@echo off
REM ARQV30 Enhanced v3.0 ULTRA-ROBUSTO - Script de Execução Windows
REM Execute este arquivo para iniciar V70V1 + Módulo Viral

echo ========================================
echo ARQV30 Enhanced v3.0 ULTRA-ROBUSTO
echo Análise Ultra-Detalhada de Mercado + Módulo Viral
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado!
    echo Por favor, execute install.bat primeiro.
    pause
    exit /b 1
)

REM Verifica se está no diretório correto
if not exist "src\run.py" (
    echo ❌ ERRO: Arquivo run.py não encontrado!
    echo Certifique-se de estar no diretório correto do projeto.
    pause
    exit /b 1
)

REM Ativa ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo 🔄 Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ AVISO: Ambiente virtual não encontrado.
    echo Recomendamos executar install.bat primeiro.
    echo.
)

REM Verifica se arquivo .env existe
if not exist ".env" (
    echo ⚠️ AVISO: Arquivo .env não encontrado!
    echo Copie o arquivo .env.example para .env e configure suas chaves de API.
    echo.
) else (
    echo ✅ Arquivo .env encontrado - APIs configuradas
)

REM Navega para o diretório src
cd src

REM Verifica dependências críticas
echo 🧪 Verificando dependências críticas...
python -c "import flask, requests, google.generativeai, supabase" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Dependências faltando! Execute install.bat
    pause
    exit /b 1
)

REM === INICIALIZAÇÃO DO MÓDULO VIRAL ===
echo.
echo ========================================
echo 🔥 INICIANDO MÓDULO VIRAL
echo ========================================
echo.

REM Verifica se Node.js está disponível
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ AVISO: Node.js não encontrado - Módulo viral desabilitado
    echo O sistema funcionará com fallback automático.
    echo.
    set VIRAL_AVAILABLE=false
    goto START_V70V1
) else (
    echo ✅ Node.js encontrado:
    node --version
    set VIRAL_AVAILABLE=true
)

REM Verifica se diretório viral existe
if not exist "..\viral" (
    echo ⚠️ AVISO: Diretório viral não encontrado - Módulo viral desabilitado
    echo.
    set VIRAL_AVAILABLE=false
    goto START_V70V1
)

REM Inicia o módulo viral em background
echo 🔄 Iniciando módulo viral em background...
cd ..\viral

REM Verifica se node_modules existe, se não, instala dependências
if not exist "node_modules" (
    echo 📦 Instalando dependências do viral...
    npm install >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ AVISO: Falha na instalação das dependências do viral
        set VIRAL_AVAILABLE=false
        cd ..\src
        goto START_V70V1
    )
)

start /B cmd /c "npm run dev > viral.log 2>&1"
if errorlevel 1 (
    echo ⚠️ AVISO: Falha ao iniciar módulo viral - usando fallback
    set VIRAL_AVAILABLE=false
) else (
    echo ✅ Módulo viral iniciado em http://localhost:8787
    set VIRAL_AVAILABLE=true
)
cd ..\src

REM Aguarda alguns segundos para o viral inicializar
echo 🔄 Aguardando inicialização do módulo viral...
timeout /t 5 /nobreak >nul

:START_V70V1
REM === INICIALIZAÇÃO DO V70V1 ===
echo.
echo ========================================
echo 🚀 INICIANDO V70V1 PRINCIPAL
echo ========================================
echo.

echo 🌐 Servidor Principal: http://localhost:5000
echo 📊 Interface: Análise Ultra-Detalhada de Mercado
echo 🤖 IA: Google Gemini Pro + HuggingFace
echo 🔍 Pesquisa: WebSailor + Google Search + Jina AI
echo 💾 Banco: Supabase PostgreSQL

if "%VIRAL_AVAILABLE%"=="true" (
    echo 🔥 Módulo Viral: http://localhost:8787 ✅ ATIVO
) else (
    echo 🔥 Módulo Viral: ⚠️ FALLBACK AUTOMÁTICO
)

echo.
echo ⚡ RECURSOS ATIVADOS:
echo - Análise com múltiplas IAs
echo - Pesquisa web profunda
echo - Processamento de anexos inteligente
echo - Geração de relatórios PDF
echo - Avatar ultra-detalhado
echo - Drivers mentais customizados
echo - Análise de concorrência profunda
echo - 🔥 Coleta de conteúdo viral das redes sociais
echo.

REM Abre o navegador automaticamente
echo 🌐 Abrindo navegador automaticamente...
timeout /t 2 /nobreak >nul
start http://localhost:5000

echo.
echo ========================================
echo ✅ SISTEMA COMPLETO INICIADO!
echo ========================================
echo.
echo 💡 INSTRUÇÕES:
echo - V70V1: http://localhost:5000 (já aberto no navegador)
if "%VIRAL_AVAILABLE%"=="true" (
    echo - Módulo Viral: http://localhost:8787 (rodando em background)
)
echo - Pressione Ctrl+C para parar ambos os servidores
echo.

python run.py

REM Volta para o diretório raiz
cd ..

REM === LIMPEZA E ENCERRAMENTO ===
echo.
echo ========================================
echo 🛑 ENCERRANDO SISTEMA COMPLETO
echo ========================================
echo.

REM Tenta encerrar processos do viral se estiverem rodando
echo 🔄 Encerrando módulo viral...
taskkill /F /IM node.exe >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Nenhum processo Node.js encontrado
) else (
    echo ✅ Módulo viral encerrado
)

echo.
echo ========================================
echo ✅ SISTEMA ULTRA-ROBUSTO ENCERRADO
echo ========================================
echo.
echo 💡 Para reiniciar: execute run.bat novamente
echo 🔧 Para reconfigurar: execute install.bat
echo 📊 Logs do viral: viral/viral.log (se disponível)
echo.
pause