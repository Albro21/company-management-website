const tasks = document.querySelectorAll(".task-item");
const categoryFilters = document.querySelectorAll(".category-filter");
const highPriorityFilter = document.querySelector("#high-priority-filter");

// Retrieve the activeCategory and isHighPriority from localStorage to apply them on page load
let activeCategory = localStorage.getItem("activeCategory") === "null" ? null : localStorage.getItem("activeCategory");
let isHighPriority = localStorage.getItem("isHighPriority")?.toLowerCase() === "true";


function filterByCategory(categoryId, categoryColor) {
    const selectedCategory = categoryId

    // Toggle filtering (if clicking the same category, reset)
    activeCategory = (activeCategory === selectedCategory) ? null : selectedCategory;

    // Save the active category to localStorage
    localStorage.setItem("activeCategory", activeCategory);

    applyCategoryFilter(categoryColor);
    filterTasks(); // Apply both category and high priority filters together
    hideEmptyTaskGroups();
}

function FilterByHighPriority() {
    applyHighPriorityFilter();
    filterTasks(); // Apply both category and high priority filters together
    hideEmptyTaskGroups();
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

// Filters tasks based on both active category and high priority status
function filterTasks() {
    tasks.forEach(task => {
        const taskCategories = task.dataset.categoryIds.split(",");
        const taskPriority = task.dataset.isHighPriority;

        const isCategoryMatch = !activeCategory|| taskCategories.includes(String(activeCategory));
        const isPriorityMatch = !isHighPriority || taskPriority === "True";

        // Only display the task if both filters match
        task.style.display = isCategoryMatch && isPriorityMatch ? "flex" : "none";
    });
}

// Changes styles of category filters and set the activeCategory variable
function applyCategoryFilter(categoryColor) {
    categoryFilters.forEach(btn => {
        btn.classList.remove("active-category");
        btn.style.backgroundColor = "#26242a";
    });

    if (activeCategory) {
        const selectedCategory = document.getElementById(`category-filter-${activeCategory}`);
        if (selectedCategory) {
            selectedCategory.classList.add("active-category");
            selectedCategory.style.backgroundColor = categoryColor;
        }
    }
}

function hideEmptyTaskGroups() {
    const taskGroups = document.querySelectorAll(".task-group");
    taskGroups.forEach(group => {
        const tasks = group.querySelectorAll(".task-item");
        const isEmpty = tasks.length === 0 || [...tasks].every(task => task.style.display === "none");
        group.classList.replace(isEmpty ? "d-flex" : "d-none", isEmpty ? "d-none" : "d-flex");
    });
}

document.addEventListener("DOMContentLoaded", function () {
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
});
