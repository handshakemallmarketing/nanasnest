const form=document.getElementById('care-inquiry');
if(form){
 form.hidden=false;
 form.addEventListener('submit',async e=>{
  e.preventDefault();
  const button=form.querySelector('button'), status=document.getElementById('inquiry-status');
  button.disabled=true; status.textContent='Submitting…';
  try{
   const response=await fetch('/api/inquiry',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(form)))});
   const result=await response.json(); status.textContent=result.message;
   if(response.ok) form.reset();
  }catch(e){status.textContent='Please contact us directly by phone or email.';}
  finally{button.disabled=false;}
 });
}
