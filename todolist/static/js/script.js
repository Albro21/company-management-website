window.csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

function showWindow(){
    let el = document.getElementById("content_window");
    el.style.display = 'block';
  }

  function showWindowProject(){
    let el = document.getElementById("content_window project-window");
    el.style.display = 'block';
  }

  function showWindowCategory(){
    let el = document.getElementById("content_window category-window");
    el.style.display = 'block';
  }

function closeWindow(){
    let el = document.getElementById("content_window");
    el.style.display = 'none';
  }

function closeWindowProject(){
    let el = document.getElementById("content_window project-window");
    el.style.display = 'none';
  }  
function closeWindowCategory(){
    let el = document.getElementById("content_window category-window");
    el.style.display = 'none';
  }

async function completeNote(button) {
    const taskId = button.getAttribute('data-task-id');
    const url = `/${taskId}/complete/`;
    const method = 'POST';

    const success = await sendRequest(url, method);

    if (success) {
        button.closest('a').remove();
    } else {
        console.error('Failed to complete task');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const badges = document.querySelectorAll('.badge');

    badges.forEach(function(badge) {
        const backgroundColor = window.getComputedStyle(badge).backgroundColor;
        
        const rgb = backgroundColor.match(/\d+/g);
        const r = parseInt(rgb[0]);
        const g = parseInt(rgb[1]);
        const b = parseInt(rgb[2]);

        const brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b;

        if (brightness > 128) {
            badge.style.color = 'black';
        } else {
            badge.style.color = 'white';
        }
    });
});






/*
function showCategoryForm(){
  let el = document.getElementById("content_window_category");
    el.style.display = 'block';

}
function closeWindowCategory(){
  let el = document.getElementById("content_window_category");
  el.style.display = 'none';
}

function showProjectForm(){
  let el = document.getElementById("content-project");
    el.style.display = 'block';
}

function closeWindowProject(){
  let el = document.getElementById("content-project");
  el.style.display = 'none';
}

*/



/* визуальное изменение цвета в settings
let colorPicker;
const defaultColor = "#ff9100";
  
window.addEventListener("load", startup, false);

function startup() {
    colorPicker = document.getElementById("#color-picker");
    colorPicker.value = defaultColor;
    colorPicker.addEventListener("input", updateFirst, false);
    colorPicker.addEventListener("change", updateAll, false);
    colorPicker.select();
    console.log(colorPicker)
  }

function updateFirst(event) {
    const p = document.querySelector("category_case");
    const bg = "background-color"
    if (p) {
      p.style.bg = event.target.value;
    }
  }

*/










/* проверка на возвращаемую дату
function WriteDate() {
  let dateControl = document.querySelector('input[type="date"]');
  dateControl;
  console.log(dateControl.value);
  console.log(dateControl.valueAsNumber);
}
*/




  