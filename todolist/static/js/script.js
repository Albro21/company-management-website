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



const textarea = document.querySelectorAll(".edit-ico-textarea textarea");

[].forEach.call(textarea, function(el){
  el.addEventListener('keyup', e =>{
    let scHeight = e.target.scrollHeight;
    console.log(scHeight);
    el.style.height = `${scHeight}px`; 
  });
});

// Date calculator (days left/overdue) //

function daysBetween(startDate, endDate) {
  if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
    throw new Error('Применяйте корректные объекты Date.');
  }
  
  const diffTime = (Date.UTC(endDate.getFullYear(), endDate.getMonth(), endDate.getDate()) -Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()));
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
  
  console.log(diffDays)
  return diffDays;
}

const startDate = new Date();
const endDate = document.querySelectorAll('div.endDateLabel');

endDate.forEach((item) => {
  if (daysBetween(startDate, new Date('20'+item.textContent)) == 1) {
    item.textContent = 'Do it today'
  } else if (daysBetween(startDate, new Date('20'+item.textContent)) > 0) {
      item.textContent = daysBetween(startDate, new Date('20'+item.textContent)) + ' days left';
  } else {
    item.textContent = 'overdue '+ -daysBetween(startDate, new Date('20'+item.textContent)) + ' days';
    item.style.textDecorationLine = 'line-through';
  }
  
})

//console.log(daysBetween(startDate, endDate));

//endDate.forEach.call(daysBetween())