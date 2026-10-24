'use strict';
const form=document.querySelector('#registerForm');
const error=document.querySelector('#error');
const submit=document.querySelector('#submit');
document.querySelector('#togglePassword').addEventListener('click',e=>{
 const show=form.elements.password.type==='password';
 form.elements.password.type=show?'text':'password';
 form.elements.confirm_password.type=show?'text':'password';
 e.target.textContent=show?'Hide':'Show';
 e.target.setAttribute('aria-label',show?'Hide passwords':'Show passwords');
 e.target.setAttribute('aria-pressed',String(show));
});
form.addEventListener('submit',async e=>{
 e.preventDefault();error.textContent='';
 const payload=Object.fromEntries(new FormData(form));
 if(payload.password!==payload.confirm_password){error.textContent='Passwords do not match.';return}
 submit.disabled=true;
 try{
  const response=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const result=await response.json();
  if(!response.ok)throw Error(result.error||'Could not create account.');
  window.location.replace('/login?registered=1');
 }catch(e){error.textContent=e.message||'Could not connect. Please try again.'}
 finally{submit.disabled=false}
});
