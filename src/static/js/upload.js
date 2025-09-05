// ARQV30 Enhanced v2.0 - Upload System
console.log('📁 Sistema de Upload carregado');

// Função global para manipular arquivos
window.handleFiles = function(files) {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    const preview = document.getElementById('preview');
    
    if (preview) {
        preview.innerHTML = `
            <div class="file-preview">
                <i class="fas fa-file-text"></i>
                <span>${file.name}</span>
                <small>(${(file.size / 1024).toFixed(1)} KB)</small>
            </div>
        `;
    }
    
    console.log('📎 Arquivo selecionado:', file.name);
};

// Função handleFiles que estava ausente
function handleFiles(files) {
    const fileList = document.getElementById('fileList');
    const uploadStatus = document.getElementById('uploadStatus');

    if (!fileList || !uploadStatus) {
        console.warn('Elementos de upload não encontrados');
        return;
    }

    // Limpa lista anterior
    fileList.innerHTML = '';

    // Processa cada arquivo
    Array.from(files).forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <strong>${file.name}</strong>
                <span class="file-size">(${formatFileSize(file.size)})</span>
            </div>
            <div class="file-status" id="status-${index}">Pronto para upload</div>
        `;
        fileList.appendChild(fileItem);
    });

    uploadStatus.textContent = `${files.length} arquivo(s) selecionado(s)`;
}

// Função auxiliar para formatar tamanho do arquivo
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}


// Função para lidar com uploads de arquivos
// function handleFiles(files) {
//     console.log('📁 Processando', files.length, 'arquivos');

//     const fileList = document.getElementById('fileList');
//     if (!fileList) {
//         console.error('❌ Elemento fileList não encontrado');
//         return;
//     }

//     Array.from(files).forEach(file => {
//         const fileItem = document.createElement('div');
//         fileItem.className = 'file-item';
//         fileItem.innerHTML = `
//             <span class="file-name">${file.name}</span>
//             <span class="file-size">${(file.size / 1024).toFixed(1)} KB</span>
//         `;
//         fileList.appendChild(fileItem);
//     });
// }

// Função para upload de arquivo individual
// function uploadFile(file) {
//     const formData = new FormData();
//     formData.append('file', file);

//     return fetch('/api/upload', {
//         method: 'POST',
//         body: formData
//     }).then(response => response.json());
// }

// Função para manipular múltiplos arquivos
// function handleFiles(files) {
//     if (files && files.length > 0) {
//         Array.from(files).forEach(file => {
//             uploadFile(file).then(result => {
//                 console.log('Arquivo enviado:', result);
//             }).catch(error => {
//                 console.error('Erro no upload:', error);
//             });
//         });
//     }
// }

// Função para upload de arquivo
function handleFileUpload() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (!file) {
        showNotification('Por favor, selecione um arquivo.', 'warning');
        return;
    }

    uploadFile(file);
}

// Função uploadFile que estava ausente
function uploadFile(file) {
    console.log('📤 Enviando arquivo:', file.name);

    const formData = new FormData();
    formData.append('file', file);

    return fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Arquivo enviado:', data);
        return data;
    })
    .catch(error => {
        console.error('❌ Erro no upload:', error);
        throw error;
    });
}

// // Função handleFiles que estava ausente
// function handleFiles(files) {
//     console.log('📁 Processando arquivos:', files.length);

//     for (let i = 0; i < files.length; i++) {
//         const file = files[i];
//         if (file.size > 10 * 1024 * 1024) { // 10MB limit
//             alert(`Arquivo ${file.name} é muito grande (máximo 10MB)`);
//             continue;
//         }

//         uploadFile(file).then(result => {
//             console.log(`✅ ${file.name} enviado com sucesso`);
//         }).catch(error => {
//             console.error(`❌ Erro ao enviar ${file.name}:`, error);
//         });
//     }
// }

// Configurações de upload
const UPLOAD_CONFIG = {
    maxFileSize: 50 * 1024 * 1024, // 50MB
    allowedTypes: [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'text/plain',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image/jpeg',
        'image/png',
        'image/gif'
    ],
    allowedExtensions: ['.pdf', '.docx', '.doc', '.txt', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif']
};

// Sistema de upload de arquivos
function initializeUploadSystem() {
    const uploadAreas = document.querySelectorAll('.upload-area, .file-upload-area');

    uploadAreas.forEach(area => {
        // Drag and drop
        area.addEventListener('dragover', handleDragOver);
        area.addEventListener('dragleave', handleDragLeave);
        area.addEventListener('drop', handleDrop);

        // Click to upload
        area.addEventListener('click', () => {
            const input = area.querySelector('input[type="file"]') || createFileInput();
            input.click();
        });
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('drag-over');

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
}

function createFileInput() {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.style.display = 'none';
    input.accept = UPLOAD_CONFIG.allowedExtensions.join(',');

    input.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });

    document.body.appendChild(input);
    return input;
}

function validateFile(file) {
    // Verifica tamanho
    if (file.size > UPLOAD_CONFIG.maxFileSize) {
        showAlert(`Arquivo "${file.name}" é muito grande. Máximo: 50MB`, 'error');
        return false;
    }

    // Verifica tipo
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    if (!UPLOAD_CONFIG.allowedExtensions.includes(extension)) {
        showAlert(`Tipo de arquivo "${extension}" não permitido`, 'error');
        return false;
    }

    return true;
}

function showUploadProgress(fileName, progress) {
    let progressContainer = document.getElementById('uploadProgress');

    if (!progressContainer) {
        progressContainer = document.createElement('div');
        progressContainer.id = 'uploadProgress';
        progressContainer.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 20px;
            min-width: 300px;
            z-index: 9999;
        `;
        document.body.appendChild(progressContainer);
    }

    let fileProgress = document.getElementById(`progress-${fileName}`);

    if (!fileProgress) {
        fileProgress = document.createElement('div');
        fileProgress.id = `progress-${fileName}`;
        fileProgress.innerHTML = `
            <div style="margin-bottom: 10px;">
                <div style="font-size: 14px; margin-bottom: 5px;">${fileName}</div>
                <div style="background: #f0f0f0; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div class="progress-bar" style="background: #2196F3; height: 100%; width: ${progress}%; transition: width 0.3s;"></div>
                </div>
                <div style="font-size: 12px; color: #666; margin-top: 2px;">${progress}%</div>
            </div>
        `;
        progressContainer.appendChild(fileProgress);
    } else {
        const progressBar = fileProgress.querySelector('.progress-bar');
        const progressText = fileProgress.querySelector('div:last-child');
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;
    }

    if (progress >= 100) {
        setTimeout(() => {
            removeUploadProgress(fileName);
        }, 2000);
    }
}

function removeUploadProgress(fileName) {
    const fileProgress = document.getElementById(`progress-${fileName}`);
    if (fileProgress) {
        fileProgress.remove();
    }

    const progressContainer = document.getElementById('uploadProgress');
    if (progressContainer && progressContainer.children.length === 0) {
        progressContainer.remove();
    }
}

function addFileToList(fileData) {
    const filesList = document.getElementById('uploadedFiles') || createFilesList();

    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        margin-bottom: 8px;
        background: #f9f9f9;
    `;

    fileItem.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-file" style="color: #2196F3;"></i>
            <div>
                <div style="font-weight: 500;">${fileData.file_name}</div>
                <div style="font-size: 12px; color: #666;">${formatFileSize(fileData.file_size)}</div>
            </div>
        </div>
        <button onclick="removeFile('${fileData.file_id}')" style="background: none; border: none; color: #f44336; cursor: pointer;">
            <i class="fas fa-trash"></i>
        </button>
    `;

    filesList.appendChild(fileItem);
}

function createFilesList() {
    const container = document.querySelector('.files-container') || document.body;

    const filesList = document.createElement('div');
    filesList.id = 'uploadedFiles';
    filesList.innerHTML = '<h4>Arquivos Enviados</h4>';

    container.appendChild(filesList);
    return filesList;
}

// function formatFileSize(bytes) {
//     if (bytes === 0) return '0 Bytes';

//     const k = 1024;
//     const sizes = ['Bytes', 'KB', 'MB', 'GB'];
//     const i = Math.floor(Math.log(bytes) / Math.log(k));

//     return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
// }

function getSessionId() {
    let sessionId = sessionStorage.getItem('arqv30_session_id');

    if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        sessionStorage.setItem('arqv30_session_id', sessionId);
    }

    return sessionId;
}

async function removeFile(fileId) {
    try {
        const response = await fetch(`/api/remove_attachment/${fileId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            const fileItem = document.querySelector(`[onclick="removeFile('${fileId}')"]`).parentNode;
            fileItem.remove();
            showAlert('Arquivo removido com sucesso!', 'success');
        } else {
            throw new Error(result.error || 'Erro ao remover arquivo');
        }

    } catch (error) {
        console.error('Erro ao remover arquivo:', error);
        showAlert(`Erro ao remover arquivo: ${error.message}`, 'error');
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('📁 Inicializando sistema de upload');
    initializeUploadSystem();
});

// Exposição de funções globais
window.uploadFile = uploadFile;
window.removeFile = removeFile;
window.handleFiles = handleFiles;