// ==================================================================
// FUNÇÕES DE RENDERIZAÇÃO (Interface)
// ==================================================================

/**
 * Renderiza a lista de atividades na coluna da esquerda.
 * Adiciona um 'ouvinte' de clique a cada item.
 */
function renderActivities(activities) {
    const activityList = document.getElementById('activity-list');
    activityList.innerHTML = ''; // Limpa a lista antes de adicionar os novos itens

    if (!activities || activities.length === 0) {
        const noActivitiesMessage = document.createElement('li');
        noActivitiesMessage.textContent = 'Nenhuma atividade para hoje.';
        activityList.appendChild(noActivitiesMessage);
        return;
    }

    activities.forEach(activity => {
        const listItem = document.createElement('li');
        listItem.textContent = `${activity.name} (${activity.type})`;
        listItem.setAttribute('data-id', activity.id); // Guarda o ID para referência

        // Adiciona o evento de clique para mostrar os detalhes
        listItem.addEventListener('click', async () => {
            const activityId = listItem.getAttribute('data-id');
            const details = await window.api.getActivityDetails(activityId);
            if (details) {
                renderDetails(details);
            }
        });

        activityList.appendChild(listItem);
    });
}

/**
 * Renderiza os detalhes de uma atividade no painel da direita.
 */
function renderDetails(details) {
    const detailsContent = document.getElementById('details-content');
    const scheduledDate = new Date(details.scheduled_for).toLocaleString('pt-BR');
    const createdDate = new Date(details.created_at).toLocaleString('pt-BR');

    detailsContent.innerHTML = `
        <h2>${details.name}</h2>
        <p><strong>Tipo:</strong> ${details.type}</p>
        <p><strong>Status:</strong> ${details.status}</p>
        <hr>
        <p><strong>Agendado para:</strong> ${scheduledDate}</p>
        <p><strong>Criado em:</strong> ${createdDate}</p>
    `;
}

/**
 * Adiciona uma mensagem do USUÁRIO ao histórico do chat.
 */
function appendUserMessage(message) {
    const chatHistory = document.getElementById('chat-history');
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', 'user-message');
    messageElement.textContent = message;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight; // Rola para ver a mensagem
}

/**
 * Adiciona uma mensagem da IA ao histórico do chat.
 */
function appendAiMessage(message) {
    const chatHistory = document.getElementById('chat-history');
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', 'ai-message');
    messageElement.textContent = message;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

/**
 * Função principal para buscar dados do backend e iniciar a renderização.
 */
async function loadAndRenderActivities() {
    try {
        const activities = await window.api.getActivities();
        renderActivities(activities);
    } catch (error) {
        console.error("Erro ao carregar e renderizar atividades:", error);
    }
}


// ==================================================================
// PONTO DE ENTRADA PRINCIPAL (Executa quando a página carrega)
// ==================================================================

document.addEventListener('DOMContentLoaded', () => {

    // --- Carregamento Inicial ---
    loadAndRenderActivities();

    // --- Lógica do Modal de Adicionar Atividade ---
    const modal = document.getElementById('add-activity-modal');
    const addActivityBtn = document.getElementById('add-activity-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const addActivityForm = document.getElementById('add-activity-form');

    function openModal() { modal.classList.add('visible'); }
    function closeModal() {
        modal.classList.remove('visible');
        addActivityForm.reset();
    }

    addActivityBtn.addEventListener('click', openModal);
    closeModalBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (event) => { if (event.target === modal) closeModal(); });

    addActivityForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const name = document.getElementById('activity-name').value;
        const type = document.getElementById('activity-type').value;
        if (!name) return;

        const result = await window.api.addActivity({ name, type });
        if (result.success) {
            closeModal();
            loadAndRenderActivities(); // Atualiza a lista
        } else {
            alert(`Erro ao salvar: ${result.message}`);
        }
    });

    // --- Lógica do Chat ---
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    async function handleSendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            appendUserMessage(message); // Mostra a mensagem do usuário
            chatInput.value = '';       // Limpa o campo

            // Envia para a IA e aguarda a resposta
            const aiResponse = await window.api.processChatMessage(message);
            
            // Mostra a resposta da IA
            appendAiMessage(aiResponse.response_text);

            // Se a IA confirmou a adição, atualiza a lista de atividades
            if (aiResponse.response_text.includes("Adicionei a tarefa")) {
                loadAndRenderActivities();
            }
        }
    }

    sendBtn.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            handleSendMessage();
        }
    });
});