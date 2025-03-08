document.addEventListener("DOMContentLoaded", function () {
    const tasks = document.querySelectorAll(".task");
    const categoryFilters = document.querySelectorAll(".category-filter");

    let activeCategory = localStorage.getItem("activeCategory");
    if (activeCategory === "null") {
        activeCategory = null;
    }

    function filterByCategory(category) {
        tasks.forEach(task => {
            const taskCategories = task.getAttribute("data-category-ids").split(",");
            const isInCategory = !category || taskCategories.includes(category);
            task.style.display = isInCategory ? "flex" : "none";
        });
    }

    function hideEmptyTaskGroups() {
        document.querySelectorAll(".task-group").forEach(group => {
            const allTasksHidden = [...group.querySelectorAll(".task")].every(task => task.style.display === "none");
            
            // Toggle visibility of the task group
            group.classList.toggle('d-none', allTasksHidden);
            group.classList.toggle('d-flex', !allTasksHidden);
        });
    }
    

    function applyCategoryFilter() {
        categoryFilters.forEach(btn => {
            btn.classList.remove("active-category");
            btn.style.backgroundColor = "";
        });

        if (activeCategory) {
            const selectedCategory = document.querySelector(`[data-category-id="${activeCategory}"]`);
            if (selectedCategory) {
                selectedCategory.classList.add("active-category");
                selectedCategory.style.backgroundColor = selectedCategory.getAttribute("data-category-color");
            }
        }
    }

    // On page load, apply the active category (if any)
    if (activeCategory) {
        filterByCategory(activeCategory);
        hideEmptyTaskGroups();
        applyCategoryFilter();
    } else {
        tasks.forEach(task => task.style.display = "flex");
    }

    categoryFilters.forEach(category => {
        category.addEventListener("click", function () {
            const selectedCategory = this.getAttribute("data-category-id");

            // Toggle filtering (if clicking the same category, reset)
            activeCategory = (activeCategory === selectedCategory) ? null : selectedCategory;

            // Save the active category to localStorage
            localStorage.setItem("activeCategory", activeCategory);

            applyCategoryFilter();
            filterByCategory(activeCategory);
            hideEmptyTaskGroups();
        });
    });
});
