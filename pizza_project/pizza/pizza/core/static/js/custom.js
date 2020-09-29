$(document).ready(function(){
  $('.custom-checkbox').mousedown(function(){
      changeCheck($(this));
    });
  $('.custom-checkbox').each(function(){
      changeCheckStart($(this));
    });

  $('select').on('change', function(){ //attach event handler to select's change event.
                                      //use a more specific selector

      if ($(this).val() === ""){ //checking to see which option has been picked

          $(this).addClass('unselected');
      } else {                   // add or remove class accordingly
          $(this).removeClass('unselected');
      }

  });
});

function changeColor(dropdownList){
  dropdownList.style.color = 'black';
}
function changeCheck(el){
  var el=el, input=el.find('input').eq(0);
  if(!input.attr('checked')){
    $('.custom-checkbox').each(function(){
      cInput = $(this).find('input').eq(0);
      if(cInput.attr('name') == input.attr('name')){
        $(this).removeClass('active');
        cInput.attr("checked", false);
      }
    });
    el.addClass('active');
    input.attr("checked", true);
  }
  return true;
}
function changeCheckStart(el){
  var el=el,input=el.find('input').eq(0);
  if(input.attr('checked')){
    el.addClass('active');
  }
  return true;
}
