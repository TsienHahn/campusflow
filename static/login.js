'use strict';
const form = document.querySelector('#loginForm');
const password = document.querySelector('#password');
const error = document.querySelector('#error');
const submit = document.querySelector('#submit');
document.querySelector('#togglePassword').addEventListener('click',e=>{
    const show=password.type==='password';
    password.type=show?'text':'password';
    e.target.textContent=show?'Hide':'Show';
    e.target.setAttribute('aria-label',show?'Hide password':'Show password');
    e.target.setAttribute('aria-pressed',String(show));
});
document.querySelector('#fillDemo').addEventListener('click',()=>{
    form.elements.username.value='alex.morgan';
    password.value='CampusFlow2026!';
    error.textContent='';
    submit.focus();
});
form.addEventListener('submit',async e=>{
    e.preventDefault();error.textContent='';submit.disabled=true;
    try{
        const response=await fetch('/api/login',{
            method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({username:form.elements.username.value,password:password.value})
        });
        const result=await response.json();
        if(!response.ok)throw new Error(result.error||'Sign in failed.');
        window.location.replace('/');
    }catch(e){error.textContent=e.message||'Could not connect. Please try again.'}
    finally{submit.disabled=false}
});
