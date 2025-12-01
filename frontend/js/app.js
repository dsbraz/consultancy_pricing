import { api } from './api.js';
import { renderProfessionals } from './views/professionals.js';
import { renderOffers } from './views/offers.js';
import { renderProjects } from './views/projects.js';

const routes = {
    'professionals': { title: 'Profissionais', render: renderProfessionals },
    'offers': { title: 'Ofertas', render: renderOffers },
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

document.addEventListener('DOMContentLoaded', async () => {
    // Verify authentication
    try {
        await api.get('/auth/me');
    } catch (e) {
        // API handles redirect for 401
        return;
    }

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
