/* Local fixture only. This script is never installed into Pi-hole. */
'use strict';
const select = document.querySelector('#theme');
const requested = new URLSearchParams(location.search).get('theme');
if (['kitty-christmas', 'kitty-easter', 'kitty-beach-summer', 'kitty-halloween-fall'].includes(requested)) select.value = requested;
const sheet = document.querySelector('#theme-css');
const charts = [];
function css(name) { return getComputedStyle(document.documentElement).getPropertyValue('--g-' + name).trim(); }
function render() {
  charts.splice(0).forEach(c => c.destroy());
  for (const [id, label, color] of [['queryOverTimeChart','Queries','green'],['clientsChart','Active clients','blue']]) {
    const values = Array.from({length:48},(_,i) => Math.round(75 + 35*Math.sin(i*.49) + 26*Math.cos(i*1.8) + (i>28&&i<36 ? 65 : 0)));
    charts.push(new Chart(document.getElementById(id), {type:'bar',data:{labels:values.map((_,i)=>`${String(Math.floor(i/2)).padStart(2,'0')}:${i%2?'30':'00'}`), datasets:[{label,data:values,backgroundColor:css(color),borderRadius:2}]},options:{responsive:true,maintainAspectRatio:false,animation:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:css('muted'),maxTicksLimit:12},grid:{display:false}},y:{ticks:{color:css('muted')},grid:{color:css('line')}}}}}));
  }
  for (const [id, legend, labels, values] of [['queryTypePieChart','query-types-legend',['A','AAAA','HTTPS','Other'],[57,28,12,3]],['forwardDestinationPieChart','forward-destinations-legend',['Cache','Local resolver','Blocked','Other'],[42,32,23,3]]]) {
    charts.push(new Chart(document.getElementById(id), {type:'doughnut',data:{labels,datasets:[{data:values,backgroundColor:['blue','green','amber','red'].map(css),borderWidth:0}]},options:{animation:false,cutout:'78%',plugins:{legend:{display:false}}}}));
    document.getElementById(legend).innerHTML = labels.map((s,i)=>`<div class="preview-key"><span>${s}</span><strong>${values[i]}%</strong></div>`).join('');
  }
}
function setTheme() {
  const path = `style/themes/${select.value}.css`;
  // A cached, already-selected stylesheet need not emit another load event.
  if (sheet.getAttribute('href') === path && sheet.sheet) render();
  else sheet.href = path;
}
sheet.addEventListener('load',render);select.addEventListener('change',setTheme);
if(requested) setTheme(); else render();
for (const [id,value] of Object.entries({dns_queries:'148,392',blocked_queries:'34,127',percent_blocked:'23.00%',gravity_size:'186,420',active_clients:'24'})) document.getElementById(id).textContent=value;
document.querySelectorAll('.overlay').forEach(e=>e.remove());
document.querySelectorAll('tbody').forEach((el,n)=>{el.innerHTML=Array.from({length:5},(_,i)=>`<tr><td>${n<2?['telemetry','metrics','assets','sync','media'][i]+'.example.test':'home-device-'+String(i+1).padStart(2,'0')}</td><td>${(2634-i*391).toLocaleString()}</td><td><div style="height:5px;background:var(--g-blue);width:${90-i*15}%"></div></td></tr>`).join('');});
document.querySelector('#layout-toggle').onclick=()=>document.body.classList.toggle('layout-boxed');
document.querySelector('#menu-toggle').onclick=(e)=>{ const mobile=innerWidth<768; document.body.classList.toggle(mobile?'sidebar-open':'sidebar-collapse');e.currentTarget.setAttribute('aria-expanded',String(mobile?document.body.classList.contains('sidebar-open'):!document.body.classList.contains('sidebar-collapse'))); };
document.querySelectorAll('a, .zoom-reset').forEach(el=>el.addEventListener('click',e=>{e.preventDefault();document.querySelector('#fixture-message').textContent='Preview only — this control requires the Pi-hole runtime.';}));
