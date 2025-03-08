document.addEventListener("DOMContentLoaded", function () {
    const tasks = document.querySelectorAll(".task");
    const categoryFilters = document.querySelectorAll(".category-filter");
    const highPriorityFilter = document.querySelector("#high-priority-filter");

    // Retrieve the activeCategory and isHighPriority from localStorage to apply them on page load
    let activeCategory = localStorage.getItem("activeCategory") === "null" ? null : localStorage.getItem("activeCategory");
    let isHighPriority = localStorage.getItem("isHighPriority")?.toLowerCase() === "true";

    // On page load, apply both filters if they're set
    if (activeCategory) {
        filterTasks();
        hideEmptyTaskGroups();
        applyCategoryFilter();
    }

    if (isHighPriority) {
        filterTasks();
        hideEmptyTaskGroups();
        highPriorityFilter.classList.replace("bi-flag", "bi-flag-fill");
    }

    // Hides empty task groups if all tasks in the group are hidden
    function hideEmptyTaskGroups() {
        document.querySelectorAll(".task-group").forEach(group => {
            const allTasksHidden = [...group.querySelectorAll(".task")].every(task => task.style.display === "none");

            // Toggle visibility of the task group
            group.classList.toggle('d-none', allTasksHidden);
            group.classList.toggle('d-flex', !allTasksHidden);
        });
    }

    // Filters tasks based on both active category and high priority status
    function filterTasks() {
        tasks.forEach(task => {
            const taskCategories = task.getAttribute("data-category-ids").split(",");
            const taskPriority = task.getAttribute("data-is-high-priority");

            const isCategoryMatch = !activeCategory || taskCategories.includes(activeCategory);
            const isPriorityMatch = !isHighPriority || taskPriority === "True";

            // Only display the task if both filters match
            task.style.display = isCategoryMatch && isPriorityMatch ? "flex" : "none";
        });
    }

    // Changes styles of category filters and set the activeCategory variable
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

    // Changes styles of high priority filter and set the isHighPriority variable
    function applyHighPriorityFilter() {
        if (isHighPriority) {
            isHighPriority = false;
            highPriorityFilter.classList.replace("bi-flag-fill", "bi-flag");
        } else {
            isHighPriority = true;
            highPriorityFilter.classList.replace("bi-flag", "bi-flag-fill");
        }
        localStorage.setItem("isHighPriority", isHighPriority);
    }

    // Event listeners for category filters
    categoryFilters.forEach(categoryFilter => {
        categoryFilter.addEventListener("click", function () {
            const selectedCategory = this.getAttribute("data-category-id");

            // Toggle filtering (if clicking the same category, reset)
            activeCategory = (activeCategory === selectedCategory) ? null : selectedCategory;

            // Save the active category to localStorage
            localStorage.setItem("activeCategory", activeCategory);

            applyCategoryFilter();
            filterTasks(); // Apply both category and high priority filters together
            hideEmptyTaskGroups();
        });
    });

    // Event listener for high priority filter
    highPriorityFilter.addEventListener("click", function () {
        applyHighPriorityFilter();
        filterTasks(); // Apply both category and high priority filters together
        hideEmptyTaskGroups();
    });
});
