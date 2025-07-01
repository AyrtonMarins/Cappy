document.addEventListener('DOMContentLoaded', () => {
    // --- INICIALIZAÇÃO ---
    const appContainer = document.querySelector('.container');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatBox = document.getElementById('chat-box');
    const tabs = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const projectListContainer = document.getElementById('project-list-container');
    const scheduleContainer = document.getElementById('schedule-container');
    const dashboardContainer = document.getElementById('dashboard-container');

    // --- MEMÓRIA DE SESSÃO: CARREGA A ÚLTIMA ABA ---
    const lastTabId = localStorage.getItem('cappy_last_tab') || 'dashboard-view';
    document.querySelector(`.tab-button[data-tab="${lastTabId}"]`)?.click();
    
    // Mostra o app após o carregamento inicial para evitar piscar
    appContainer.style.opacity = 1;

    // --- LÓGICA DE ABAS (com salvamento) ---
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tabId).classList.add('active');
            
            // Salva a aba clicada no localStorage
            localStorage.setItem('cappy_last_tab', tabId);

            // Carrega os dados da aba correspondente
            if (tabId === 'projects-view') window.electron.sendMessage('get_all_projects');
            else if (tabId === 'schedule-view') window.electron.sendMessage('get_daily_schedule');
            else if (tabId === 'dashboard-view') window.electron.sendMessage('get_dashboard_data');
        });
    });

    // --- ENVIO DE MENSAGEM (CHAT) ---
    messageForm.addEventListener('submit', (e) => { e.preventDefault(); const msg = messageInput.value.trim(); if (msg) { window.electron.sendMessage(msg); addMessageToChat(msg, 'user'); messageInput.value = ''; } });

    // --- RECEPTOR PRINCIPAL DE MENSAGENS ---
    window.electron.receiveMessage((json) => {
        try {
            const res = JSON.parse(json);
            if (res.message) addMessageToChat(res.message, 'cappy');

            const activeTabId = localStorage.getItem('cappy_last_tab') || 'dashboard-view';
            switch (res.data_type) {
                case 'project_created': case 'task_created': case 'project_deleted':
                case 'task_deleted': case 'project_updated': case 'task_updated':
                case 'activity_created': case 'activity_updated': case 'activity_deleted':
                    // Sempre recarrega a aba ativa se ela for o painel ou projetos
                    if (activeTabId === 'dashboard-view') window.electron.sendMessage('get_dashboard_data');
                    if (activeTabId === 'projects-view') window.electron.sendMessage('get_all_projects');
                    break;
                case 'project_list': renderProjects(res.data); break;
                case 'daily_schedule_data': renderSchedule(res.data); break;
                case 'dashboard_data': renderDashboard(res.data); break;
            }
        } catch (err) { console.error('Erro no frontend:', err, 'JSON:', json); }
    });

    // --- DELEGAÇÃO DE EVENTOS ---
    [projectListContainer, scheduleContainer, dashboardContainer].forEach(container => {
        container.addEventListener('click', (event) => {
            const target = event.target;
            // Ações de clique (deleção, edição, etc.)
            if (target.classList.contains('delete-task-btn')) { if (confirm('Tem certeza?')) window.electron.sendMessage(`delete_task:${target.dataset.taskId}`); }
            else if (target.classList.contains('delete-project-btn')) { if (confirm('Excluir projeto e tarefas?')) window.electron.sendMessage(`delete_project:${target.dataset.projectId}`); }
            else if (target.classList.contains('delete-activity-btn')) { if (confirm('Tem certeza?')) window.electron.sendMessage(`delete_activity:${target.dataset.activityId}`); }
            else if (target.classList.contains('editable')) { makeNameEditable(target); }
            else if (target.classList.contains('due-date') || target.classList.contains('add-due-date')) { makeDueDateEditable(target); }
            else if (target.id === 'add-project-btn') { showInputForNewItem(projectListContainer, 'project'); }
            else if (target.classList.contains('add-task-btn')) { const taskList = target.closest('.project-item').querySelector('.task-list'); showInputForNewItem(taskList, 'task', target.dataset.projectId, target.dataset.projectName); }
        });

        container.addEventListener('change', (event) => {
            const target = event.target;
            // Ações de mudança (checkboxes)
            if (target.matches('.task-checkbox, .activity-checkbox')) {
                const listItem = target.closest('li');
                if (listItem) {
                    listItem.classList.add('fading-out'); // Adiciona a classe para a animação
                    listItem.addEventListener('transitionend', () => {
                        if (target.classList.contains('task-checkbox')) {
                            window.electron.sendMessage(`update_task_status:${target.dataset.taskId}:${target.checked ? 'Feita' : 'A Fazer'}`);
                        } else if (target.classList.contains('activity-checkbox')) {
                            window.electron.sendMessage(`update_activity_status:${target.dataset.activityId}:${target.checked ? 'Feita' : 'A Fazer'}`);
                        }
                    }, { once: true }); // O evento só dispara uma vez
                }
            }
        });
        // Adição Rápida de Atividade no Painel
        container.addEventListener('keydown', (event) => {
            if (event.target.id === 'new-activity-input' && event.key === 'Enter') {
                const input = event.target;
                const activityName = input.value.trim();
                if (activityName) {
                    window.electron.sendMessage(activityName); // Envia como um comando de fallback
                    input.value = '';
                }
            }
        });
    });

    // --- FUNÇÕES DE EDIÇÃO E CRIAÇÃO (sem alterações) ---
    function makeNameEditable(el){const o=el.textContent;const i=document.createElement('input');i.type='text';i.value=o;i.classList.add('edit-input');el.replaceWith(i);i.focus();const s=()=>{const n=i.value.trim();if(n&&n!==o){const{id,type}=el.dataset;window.electron.sendMessage(`edit_${type}:${id}:${n}`);}else{i.replaceWith(el);}};i.addEventListener('blur',s);i.addEventListener('keydown',e=>{if(e.key==='Enter')i.blur();if(e.key==='Escape')i.replaceWith(el);});}
    function makeDueDateEditable(el){const{id,type}=el.dataset;const i=document.createElement('input');i.type='date';i.value=el.textContent;el.replaceWith(i);i.focus();const s=()=>{const n=i.value?i.value:'null';window.electron.sendMessage(`edit_${type}_due_date:${id}:${n}`);};i.addEventListener('blur',()=>i.replaceWith(el));i.addEventListener('change',s);}
    function showInputForNewItem(c,t,pId=null,pName=null){const i=document.createElement('input');i.type='text';i.placeholder=`Novo ${t==='project'?'projeto':'tarefa'}...`;i.classList.add('new-item-input');c.appendChild(i);i.focus();const create=()=>{const n=i.value.trim();if(n){let cmd='';if(t==='project')cmd=`crie um projeto: ${n}`;else if(t==='task'&&pId)cmd=`crie uma tarefa: ${n} para o projeto: ${pName}`;if(cmd)window.electron.sendMessage(cmd);}i.remove();};i.addEventListener('blur',create);i.addEventListener('keydown',e=>{if(e.key==='Enter')i.blur();});}

    // --- FUNÇÕES DE RENDERIZAÇÃO ---
    function createDueDateBadge(d,id,t){if(d){const D=new Date(d+'T00:00:00'),T=new Date();T.setHours(0,0,0,0);let c='due-date-future';if(D<T)c='due-date-overdue';else if(D.getTime()===T.getTime())c='due-date-today';return`<span class="due-date ${c}" data-id="${id}" data-type="${t}">${d}</span>`;}else{return`<span class="add-due-date" data-id="${id}" data-type="${t}">[+data]</span>`;}}
    function addMessageToChat(text,sender){const el=document.createElement('div');el.classList.add('chat-message',`${sender}-message`);el.textContent=text;chatBox.appendChild(el);chatBox.scrollTop=chatBox.scrollHeight;}
    function renderProjects(projects){projectListContainer.innerHTML='<button id="add-project-btn" class="add-button">Novo Projeto</button>';if(!projects||projects.length===0){projectListContainer.innerHTML+='<p class="empty-message">Nenhum projeto encontrado.</p>';return;}projects.forEach(p=>{const el=document.createElement('div');el.classList.add('project-item');const b=createDueDateBadge(p.due_date,p.id,'project');let tasksHtml='<ul class="task-list">';if(p.tasks&&p.tasks.length>0){p.tasks.forEach(t=>{const done=t.status==='Feita';const tb=createDueDateBadge(t.due_date,t.id,'task');tasksHtml+=`<li class="task-item ${done?'completed':''}"><div class="task-content"><input type="checkbox" class="task-checkbox" data-task-id="${t.id}" ${done?'checked':''}><label class="editable" data-id="${t.id}" data-type="task">${t.name}</label>${tb}</div><span class="delete-task-btn" data-task-id="${t.id}">[x]</span></li>`;});}tasksHtml+=`</ul><div class="task-actions"><span class="add-task-btn" data-project-id="${p.id}" data-project-name="${p.name}">[+ Tarefa]</span></div>`;el.innerHTML=`<div class="project-header"><div class="project-title-wrapper"><span class="editable" data-id="${p.id}" data-type="project">${p.name}</span>${b}</div><span class="delete-project-btn" data-project-id="${p.id}">[x]</span></div>${tasksHtml}`;projectListContainer.appendChild(el);});}
    function renderSchedule(activities){scheduleContainer.innerHTML='';if(!activities||activities.length===0){scheduleContainer.innerHTML='<p class="empty-message">Nenhuma atividade para hoje.</p>';return;}let html='<ul class="schedule-list">';activities.forEach(act=>{const done=act.status==='Feita';html+=`<li class="schedule-item ${done?'completed':''}"><div class="item-content"><input type="checkbox" class="activity-checkbox" data-activity-id="${act.id}" ${done?'checked':''}><label>${act.name}</label></div><span class="delete-activity-btn" data-activity-id="${act.id}">[x]</span></li>`;});scheduleContainer.innerHTML=html+'</ul>';}

    function renderDashboard(data) {
        dashboardContainer.innerHTML = '';
        const { tasks, activities } = data;
        let html = `<h1>Olá, Ayrton!</h1><p class="subtitle">Este é o seu resumo de hoje.</p>`;

        if (tasks.overdue?.length > 0) {
            html += '<div class="dashboard-section"><h2><span class="section-icon overdue-icon">!</span>Tarefas Atrasadas</h2><ul class="dashboard-list">';
            tasks.overdue.forEach(t => { html += `<li class="task-item"><div class="task-content"><input type="checkbox" class="task-checkbox" data-task-id="${t.id}"><label>${t.name}</label><span class="task-project-tag">${t.project_name}</span></div></li>`; });
            html += '</ul></div>';
        }
        if (tasks.due_today?.length > 0) {
            html += '<div class="dashboard-section"><h2><span class="section-icon today-icon">→</span>Para Hoje</h2><ul class="dashboard-list">';
            tasks.due_today.forEach(t => { html += `<li class="task-item"><div class="task-content"><input type="checkbox" class="task-checkbox" data-task-id="${t.id}"><label>${t.name}</label><span class="task-project-tag">${t.project_name}</span></div></li>`; });
            html += '</ul></div>';
        }
        
        // Seção de Atividades do Dia com campo de adição
        html += '<div class="dashboard-section"><h2><span class="section-icon activity-icon">⚡</span>Atividades do Dia</h2><ul class="dashboard-list">';
        if (activities?.length > 0) {
            activities.forEach(act => { const done = act.status === 'Feita'; html += `<li class="schedule-item ${done ? 'completed' : ''}"><div class="item-content"><input type="checkbox" class="activity-checkbox" data-activity-id="${act.id}" ${done ? 'checked' : ''}><label>${act.name}</label></div></li>`; });
        }
        html += '</ul><input type="text" id="new-activity-input" class="new-item-input" placeholder="Adicionar nova atividade e pressionar Enter..."></div>';
        
        dashboardContainer.innerHTML = html;
    }
});