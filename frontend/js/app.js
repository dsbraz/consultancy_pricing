import { renderProfessionals } from './views/professionals.js';
import { renderTemplates } from './views/templates.js';
import { renderProjects } from './views/projects.js';

const routes = {
    'professionals': { title: 'Profissionais', render: renderProfessionals },
    'templates': { title: 'Templates', render: renderTemplates },
    'projects': { title: 'Projetos', render: renderProjects }
};

function navigateTo(viewName) {
    const route = routes[viewName];
    if (route) {
        document.getElementById('page-title').textContent = route.title;
        const contentDiv = document.getElementById('app-content');
        contentDiv.innerHTML = ''; // Clear content
        route.render(contentDiv);

        // Update active link
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-view') === viewName) {
                link.classList.add('active');
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Setup navigation
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = link.getAttribute('data-view');
            navigateTo(view);
        });
    });

    // Initial load
    navigateTo('professionals');
});
