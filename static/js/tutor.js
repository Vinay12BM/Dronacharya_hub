// ── AI CHAT (chat page) ──────────────────────────────────────────
async function sendChatMessage(){
  const input=document.getElementById('chat-input');
  if(!input) return;
  const msg=input.value.trim();
  if(!msg) return;
  appendChatBubble(msg,'user');
  input.value='';
  showTypingIndicator();
  try{
    const res=await fetch('/tutor/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    const data=await res.json();
    hideTypingIndicator();
    appendChatBubble(data.reply||data.message||'Error.','bot');
  } catch(e){ hideTypingIndicator(); appendChatBubble('Network error.','bot'); }
}

function appendChatBubble(text, role){
  const box=document.getElementById('chat-messages');
  if(!box) return;
  const div=document.createElement('div');
  div.className=role==='user'?'flex justify-end mb-3':'flex justify-start mb-3';
  const bubble=document.createElement('div');
  bubble.className=role==='user'?'bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-br-sm max-w-xs text-sm':'bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-sm max-w-sm text-sm text-gray-800';
  if(role==='bot') bubble.innerHTML=marked.parse(text);
  else bubble.textContent=text;
  div.appendChild(bubble);
  box.appendChild(div);
  box.scrollTop=box.scrollHeight;
}

function showTypingIndicator(){
  const box=document.getElementById('chat-messages');
  if(box) {
    box.innerHTML+='<div id="typing" class="flex justify-start mb-4"><div class="bg-white border px-4 py-4 rounded-2xl text-sm shadow-sm"><span class="typing-dots">● ● ●</span></div></div>';
    box.scrollTop=box.scrollHeight;
  }
}
function hideTypingIndicator(){ document.getElementById('typing')?.remove(); }

// ── QUIZ PAGE ────────────────────────────────────────────────────
let quiz=[], selectedAnswers={}, currentQuestion=0, timerInterval;

async function generateQuiz(){
  const topic=document.getElementById('quiz-topic').value.trim();
  if(!topic){ alert('Enter a topic.'); return; }
  document.getElementById('quiz-loading').classList.remove('hidden');
  document.getElementById('quiz-input-area').classList.add('hidden');
  try{
    const res=await fetch('/tutor/api/generate-quiz',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic})});
    const data=await res.json();
    if(data.success){ quiz=data.questions; currentQuestion=0; selectedAnswers={}; showQuestion(); }
    else showQuizError(data.message);
  } catch(e){ showQuizError('Network error.'); }
  finally{ document.getElementById('quiz-loading').classList.add('hidden'); }
}

function showQuestion(){
  const q=quiz[currentQuestion];
  document.getElementById('quiz-display').classList.remove('hidden');
  document.getElementById('q-number').textContent=`Question ${currentQuestion+1} of ${quiz.length}`;
  document.getElementById('q-text').textContent=q.question;
  document.getElementById('q-progress').style.width=`${((currentQuestion+1)/quiz.length)*100}%`;
  const opts=document.getElementById('q-options');
  opts.innerHTML='';
  Object.entries(q.options).forEach(([k,v])=>{
    const btn=document.createElement('button');
    btn.className='w-full text-left px-4 py-3 border-2 border-gray-200 rounded-xl hover:border-blue-400 transition text-sm font-medium bg-white';
    btn.textContent=`${k}. ${v}`;
    btn.onclick=()=>selectOption(k, btn, q);
    opts.appendChild(btn);
  });
  startTimer();
}

function selectOption(key, btn, q){
  clearInterval(timerInterval);
  document.querySelectorAll('#q-options button').forEach(b=>b.disabled=true);
  selectedAnswers[currentQuestion]=key;
  const correct=q.answer;
  if(key===correct) btn.className=btn.className.replace('border-gray-200','border-green-500 bg-green-50');
  else{
    btn.className=btn.className.replace('border-gray-200','border-red-400 bg-red-50');
    document.querySelectorAll('#q-options button').forEach(b=>{ if(b.textContent.startsWith(correct)) b.className=b.className.replace('border-gray-200','border-green-500 bg-green-50'); });
  }
  setTimeout(()=>{ if(currentQuestion<quiz.length-1){ currentQuestion++; showQuestion(); } else showResults(); },1500);
}

function startTimer(){
  let t=30;
  const timerEl = document.getElementById('timer');
  if(timerEl) timerEl.textContent=t;
  clearInterval(timerInterval);
  timerInterval=setInterval(()=>{ t--; if(timerEl) timerEl.textContent=t; if(t<=0){ clearInterval(timerInterval); if(currentQuestion<quiz.length-1){currentQuestion++;showQuestion();}else showResults(); }},1000);
}

function showResults(){
  document.getElementById('quiz-display').classList.add('hidden');
  const correct=Object.entries(selectedAnswers).filter(([i,a])=>quiz[i].answer===a).length;
  const pct=Math.round((correct/quiz.length)*100);
  document.getElementById('results-display').classList.remove('hidden');
  document.getElementById('final-score').textContent=`${correct}/${quiz.length}`;
  document.getElementById('final-pct').textContent=`${pct}%`;
  // Save results
  fetch('/tutor/api/save-quiz',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic:document.getElementById('quiz-topic').value,score:correct,total:quiz.length,percentage:pct,details:quiz.map((q,i)=>({question:q.question,user_answer:selectedAnswers[i]||'Skipped',correct_answer:q.answer,is_correct:selectedAnswers[i]===q.answer}))})});
}

function showQuizError(msg){
  alert(msg);
  document.getElementById('quiz-input-area').classList.remove('hidden');
}

// ── NOTES GENERATOR (dashboard) ──────────────────────────────────
async function generateAndDownloadNotes(){
  const topicInput = document.getElementById('notes-topic-input');
  if(!topicInput) return;
  const topic=topicInput.value.trim();
  if(!topic){ alert('Enter a topic.'); return; }
  const btn=document.querySelector('[onclick="generateAndDownloadNotes()"]');
  if(btn){ btn.disabled=true; btn.textContent='Generating...'; }
  try{
    const res=await fetch('/tutor/api/generate-notes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic,format:'docx'})});
    const data=await res.json();
    if(data.success&&data.download_url){ 
        window.location.href=data.download_url; 
    } else alert(data.message||'Error generating notes.');
  } catch(e){ alert('Network error.'); }
  finally{ if(btn){ btn.disabled=false; btn.textContent='Generate & Download'; } }
}

// ── ENTER KEY SUPPORT ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('chat-input')?.addEventListener('keydown',e=>{ if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendChatMessage();} });
  document.getElementById('quiz-topic')?.addEventListener('keydown',e=>{ if(e.key==='Enter') generateQuiz(); });
  document.getElementById('topic-input')?.addEventListener('keydown',e=>{ if(e.ctrlKey&&e.key==='Enter') generatePaper(); });
});
