const blogList = document.getElementById('blog-list');
const paginationContainer = document.getElementById('pagination-container');
const filterButtons = document.querySelectorAll('.filter-btn');
const API_URL = 'https://buddyskincare.pythonanywhere.com/blog/';

let currentPage = 1;
let currentTag = 'all';

const formatDate = (dateString) => {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
    return new Date(dateString).toLocaleDateString('vi-VN', options);
};

const getTagName = (tag) => {
    switch (tag.toLowerCase()) {
        case 'mld':
            return 'Mẹo làm đẹp';
        case 'ud':
            return 'Ưu đãi';
        case 'hd':
            return 'Hướng dẫn';
        default:
            return tag;
    }
};

const getTagClass = (tag) => {
    switch (tag.toLowerCase()) {
        case 'mld':
            return 'blog-tag-mld';
        case 'ud':
            return 'blog-tag-ud';
        case 'hd':
            return 'blog-tag-hd';
        default:
            return 'blog-tag';
    }
};

const createBlogCard = (blog) => {
    const blogCard = document.createElement('div');
    blogCard.className = 'blog-card';
    const tagName = getTagName(blog.tag);
    const tagClass = getTagClass(blog.tag);

    blogCard.innerHTML = `
        <a href="/blog/${blog.id}" class="blog-card-link">
            <img src="${blog.img_thumbnail}" alt="${blog.title}" class="blog-image">
            <div class="blog-content">
                <span class="blog-tag ${tagClass}">${tagName}</span>
                <h2 class="blog-title">${blog.title}</h2>
                <p class="blog-description">${blog.short_description}</p>
                <div class="blog-meta">
                    <div class="date-views">
                        <span><i class="fas fa-calendar-alt"></i> ${formatDate(blog.post_date)}</span>
                        <span><i class="fas fa-eye"></i> ${blog.views} lượt xem</span>
                    </div>
                </div>
            </div>
        </a>
    `;
    blogList.appendChild(blogCard);
};

const renderPagination = (numPages) => {
    paginationContainer.innerHTML = '';

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '<<';
    prevBtn.className = 'pagination-btn';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', () => {
        currentPage--;
        fetchBlogs(currentPage, currentTag);
    });
    paginationContainer.appendChild(prevBtn);

    // Number buttons
    for (let i = 1; i <= numPages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = 'pagination-btn';
        if (i === currentPage) {
            pageBtn.classList.add('active');
        }
        pageBtn.addEventListener('click', () => {
            currentPage = i;
            fetchBlogs(currentPage, currentTag);
        });
        paginationContainer.appendChild(pageBtn);
    }

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '>>';
    nextBtn.className = 'pagination-btn';
    nextBtn.disabled = currentPage === numPages;
    nextBtn.addEventListener('click', () => {
        currentPage++;
        fetchBlogs(currentPage, currentTag);
    });
    paginationContainer.appendChild(nextBtn);
};

const updateActiveButton = (selectedTag) => {
    filterButtons.forEach(btn => {
        if (btn.dataset.tag === selectedTag) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
};

const fetchBlogs = async (page, tag) => {
    try {
        let apiUrl = `${API_URL}?page=${page}`;
        if (tag !== 'all') {
            apiUrl += `&tag=${tag}`;
        }

        const response = await fetch(apiUrl);
        const data = await response.json();

        // Clear existing blogs before adding new ones
        blogList.innerHTML = '';

        // Loop through the results and create a card for each blog
        if (data.results && data.results.length > 0) {
            data.results.forEach(blog => {
                createBlogCard(blog);
            });
        } else {
            blogList.innerHTML = '<p class="no-blogs-message">Không tìm thấy bài viết nào.</p>';
        }

        // Render pagination based on num_pages
        renderPagination(data.num_pages);
        // Update active filter button
        updateActiveButton(tag);
    } catch (error) {
        console.error('Lỗi khi fetch API:', error);
        alert('Không thể tải dữ liệu blog. Vui lòng thử lại sau.');
    }
};

// Add event listeners to filter buttons
filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        currentTag = button.dataset.tag;
        currentPage = 1;
        fetchBlogs(currentPage, currentTag);
    });
});

// Initial call to fetch the first page of blogs
fetchBlogs(currentPage, currentTag);