document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Show loading spinner
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const jobListings = document.getElementById('jobListings');
    
    loading.classList.remove('d-none');
    results.classList.add('d-none');
    jobListings.innerHTML = '';
    
    // Get form data
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display job listings
            data.jobs.forEach(job => {
                const jobCard = document.createElement('div');
                jobCard.className = 'card job-card mb-3';
                jobCard.innerHTML = `
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div>
                                <h5 class="card-title job-title">${job.title}</h5>
                                <h6 class="card-subtitle company-name">
                                    <i class="fas fa-building me-2"></i>${job.company || 'Company not specified'}
                                </h6>
                            </div>
                            ${job.job_link ? `
                                <a href="${job.job_link}" class="card-link" target="_blank">
                                    <i class="fas fa-external-link-alt me-1"></i>View Job
                                </a>` : ''
                            }
                        </div>
                        
                        <p class="card-text location">
                            <i class="fas fa-map-marker-alt me-2"></i>${job.location || 'Location not specified'}
                        </p>
                        
                        <p class="card-text summary">
                            <i class="fas fa-info-circle me-2"></i>${job.summary || 'No description available'}
                        </p>
                        
                        ${job.RecommendedCertifications ? `
                            <div class="mt-4">
                                <h6 class="text-primary">
                                    <i class="fas fa-certificate me-2"></i>Recommended Certifications
                                </h6>
                                <div class="certifications">
                                    ${job.RecommendedCertifications}
                                </div>
                            </div>` : ''
                        }
                        
                        ${job.RoadMap ? `
                            <div class="mt-4">
                                <h6 class="text-primary">
                                    <i class="fas fa-road me-2"></i>Career Roadmap
                                </h6>
                                <div class="roadmap">
                                    ${job.RoadMap}
                                </div>
                            </div>` : ''
                        }
                    </div>
                `;
                jobListings.appendChild(jobCard);
            });
            
            results.classList.remove('d-none');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('An error occurred while processing your request.');
        console.error(error);
    } finally {
        loading.classList.add('d-none');
    }
});
