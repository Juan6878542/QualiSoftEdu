// Simple client-side validation (optional)
document.addEventListener('DOMContentLoaded', function(){ 
  const form = document.querySelector('form');
  if(!form) return;
  form.addEventListener('submit', function(e){
    const nums = form.querySelectorAll('input[type=number]');
    for(const n of nums){
      const v = parseFloat(n.value || 0);
      if(isNaN(v) || v < parseFloat(n.min || 0) || v > parseFloat(n.max || 5)){
        alert('Por favor verifique los valores numéricos (0-5).');
        e.preventDefault();
        return;
      }
    }
  });
});
