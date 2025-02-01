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



// calculate start width of note title after page render
const inputTitles = document.querySelectorAll("textarea.input-title")
inputTitles.forEach((title) => {

  let span = document.createElement('span');
  span.style.cssText = `font: Montserrat; visibility: hidden; whit-space: nowrap; font-size: 18px`;
  span.textContent = title.textContent;
  document.body.appendChild(span);
  let width = span.offsetWidth + title.textContent.length;
  document.body.removeChild(span)
  
  title.style.width = width + 'px';

})

// textarea auto height (when user write smth)
const textarea = document.querySelectorAll(".edit-ico-textarea textarea");

[].forEach.call(textarea, function(el){
  el.addEventListener('keyup', e =>{
    let scHeight = e.target.scrollHeight;
    console.log(scHeight);
    el.style.height = `${scHeight}px`; 
  });
});

// Date calculator (days left/overdue)

function daysBetween(startDate, endDate) {
  if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
    throw new Error('Применяйте корректные объекты Date.');
  }
  
  const diffTime = (Date.UTC(endDate.getFullYear(), endDate.getMonth(), endDate.getDate()) -Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()));
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
  

  return diffDays;
}

const startDate = new Date(); // today user's date
const endDate = document.querySelectorAll('div.endDateLabel');

endDate.forEach((item) => {
  if (daysBetween(startDate, new Date('20'+item.textContent)) == 1) {
    item.textContent = 'Do it today'
  } else if (daysBetween(startDate, new Date('20'+item.textContent)) > 0) {
      item.textContent = daysBetween(startDate, new Date('20'+item.textContent)) + ' days left';
  } else if (daysBetween(startDate, new Date('20'+item.textContent)) <= 0 && daysBetween(startDate, new Date('20'+item.textContent)) >= -1){
    item.textContent = 'overdue yesterday';
    item.style.textDecorationLine = 'line-through';
  } else {
    item.textContent = 'overdue '+ -daysBetween(startDate, new Date('20'+item.textContent)) + ' days';
    item.style.textDecorationLine = 'line-through';
  }
  
})

//add category form

let plusCategory = document.querySelectorAll('.plus-inner')

plusCategory.forEach((item) => {
  item.addEventListener('click', (e) => {
    let form = item.querySelector('form')
    
    console.log(form.style.visibility)

    

    if (form.style.visibility == 'visible') {
      form.style.height = '0';
      setTimeout(function(){
        form.style.visibility = 'hidden';
        form.style.width = '0';
      }, 400); 
    } else {
      form.style.visibility = 'visible';
      form.style.height = '100%';
      form.style.width = '100%';
    }
  });
});

//switch flag

let flags = document.querySelectorAll('.bi')

flags.forEach((item) => {
  item.addEventListener('click', (e) => {
    if (item.getAttribute('class') == 'bi bi-flag-fill') {
      item.setAttribute('class', 'bi bi-flag')
    } else {
      item.setAttribute('class', 'bi bi-flag-fill')
    }
  });
});