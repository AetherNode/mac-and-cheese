(function(){
var RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function vt(fn){if(document.startViewTransition&&!RM)document.startViewTransition(fn);else fn();}
/* clocks */
var C=[['Tokyo','Asia/Tokyo',540,930],['London','Europe/London',480,990],['New York','America/New_York',570,960]];
var ck=document.getElementById('ck');
var clocks=C.map(function(c){var d=document.createElement('div');d.className='cl';d.innerHTML='<span class="tm"></span><span class="cn">'+c[0]+'</span><span class="cs"><i></i><b></b></span>';ck.appendChild(d);
return{c:c,d:d,t:d.querySelector('.tm'),s:d.querySelector('.cs b'),f:new Intl.DateTimeFormat('en-GB',{timeZone:c[1],hour:'2-digit',minute:'2-digit',second:'2-digit',weekday:'short',hour12:false})};});
var age=document.getElementById('age'),iso=new Date(age.dataset.iso);
function tick(){var now=new Date();clocks.forEach(function(k){var o={};k.f.formatToParts(now).forEach(function(p){o[p.type]=p.value});var H=+o.hour%24,M=+o.minute,m=H*60+M;
var op=o.weekday!=='Sat'&&o.weekday!=='Sun'&&m>=k.c[2]&&m<k.c[3];k.d.classList.toggle('open',op);k.t.innerHTML=(H%12||12)+':'+o.minute+'<small>'+(H<12?'AM':'PM')+'</small>';k.s.textContent=op?'Open':'Closed';});
var mins=Math.max(0,Math.round((now-iso)/60000)),txt=mins<1?'just now':mins<60?mins+' min ago':mins<1440?Math.floor(mins/60)+'h '+(mins%60)+'m ago':Math.floor(mins/1440)+'d ago';
age.textContent=txt;age.classList.toggle('old',mins>180);}
tick();setInterval(tick,1000);
/* news */
var ns=document.getElementById('ns'),cards=ns.querySelectorAll('.nc'),nn=document.getElementById('nn'),bar=document.getElementById('npb'),ni=0,DUR=RM?9000:6500,left=DUR,lastT=performance.now(),paused=false;
var nw=ns.closest('.nw');nw.addEventListener('mouseenter',function(){paused=true});nw.addEventListener('mouseleave',function(){paused=false});nw.addEventListener('focusin',function(){paused=true});nw.addEventListener('focusout',function(){paused=false});
function runBar(){bar.classList.remove('run');void bar.offsetWidth;bar.style.setProperty('--dur',DUR+'ms');bar.classList.add('run');}
function show(i){cards[ni].classList.remove('on');ni=(i+cards.length)%cards.length;cards[ni].classList.add('on');nn.textContent=(ni+1)+' / '+cards.length;left=DUR;runBar();}
runBar();
(function loop(t){var dt=t-lastT;lastT=t;if(!paused&&!document.hidden){left-=dt;if(left<=0)show(ni+1);}requestAnimationFrame(loop);})(performance.now());
/* filters, sort, view */
var tiles=document.getElementById('tiles'),list=document.getElementById('list'),rows=document.getElementById('rows'),em=document.getElementById('em');
var st={f:'all',s:'g',v:'cards'};
function key(el){var m=+el.dataset.m,c=+el.dataset.c;return st.s==='g'?+el.dataset.g:st.s==='x'?-(Math.abs(m+c)*100+Math.abs(m)):st.s==='m'?-(Math.abs(m)*100+Math.abs(c)):-(Math.abs(c)*100+Math.abs(m));}
function apply(){[tiles,rows].forEach(function(box){var els=[].slice.call(box.children);els.sort(function(a,b){return key(a)-key(b)});els.forEach(function(el){el.hidden=!(st.f==='all'||el.dataset.f===st.f);box.appendChild(el);});});
tiles.hidden=st.v!=='cards';list.hidden=st.v!=='table';em.hidden=!!tiles.querySelector('.tile:not([hidden])');}
function setOn(sel,el){document.querySelectorAll(sel).forEach(function(b){b.classList.toggle('on',b===el)});}
function toAssets(){var fb=document.getElementById('fb'),y=document.getElementById('assets').getBoundingClientRect().top+scrollY;if(scrollY<y-40||scrollY>y+400)scrollTo({top:y,behavior:RM?'auto':'smooth'});}
document.querySelectorAll('.f').forEach(function(b){b.addEventListener('click',function(){st.f=b.dataset.f;vt(function(){setOn('.f',b);apply();});toAssets();});});
document.querySelectorAll('[data-s]').forEach(function(b){b.addEventListener('click',function(){st.s=b.dataset.s;vt(function(){setOn('[data-s]',b);apply();});});});
document.querySelectorAll('[data-v]').forEach(function(b){b.addEventListener('click',function(){st.v=b.dataset.v;vt(function(){setOn('[data-v]',b);apply();});});});
/* spotlight */
tiles.addEventListener('pointermove',function(ev){var t=ev.target.closest('.tile');if(!t)return;var r=t.getBoundingClientRect();t.style.setProperty('--mx',(ev.clientX-r.left)+'px');t.style.setProperty('--my',(ev.clientY-r.top)+'px');});
/* count-up and scale reveal */
function count(el){var n=+el.dataset.n,s=performance.now(),d=900;function f(t){var p=Math.min(1,(t-s)/d),e=1-Math.pow(1-p,3),v=Math.round(n*e);el.textContent=v>0?'+'+v:v<0?'−'+(-v):'0';if(p<1)requestAnimationFrame(f);}requestAnimationFrame(f);}
if(!RM&&'IntersectionObserver'in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(!x.isIntersecting)return;var t=x.target;io.unobserve(t);requestAnimationFrame(function(){t.classList.remove('pre')});t.querySelectorAll('.v[data-n]').forEach(count);});},{threshold:.25});
document.querySelectorAll('.tile').forEach(function(t,i){t.classList.add('pre');io.observe(t);});}
/* drawer */
var ov=document.getElementById('ov'),sh=document.getElementById('sheet'),cur=null,last=null,toast=document.getElementById('toast');
function order(){var box=st.v==='cards'?tiles:rows;return[].slice.call(box.children).filter(function(e){return!e.hidden}).map(function(e){return e.dataset.k});}
function open(k,from){var tp=document.getElementById('d-'+k);if(!tp)return;cur=k;if(from)last=from;sh.className='sheet '+tp.dataset.c;sh.innerHTML='';sh.appendChild(tp.content.cloneNode(true));sh.scrollTop=0;
ov.classList.add('on');document.body.style.overflow='hidden';
sh.querySelector('.x').onclick=close;sh.querySelector('.pv').onclick=function(){step(-1)};sh.querySelector('.nx').onclick=function(){step(1)};
sh.querySelector('.share').onclick=function(){shareOpen(tp,sh)};sh.querySelector('.x').focus({preventScroll:true});}
function step(d){var o=order(),i=o.indexOf(cur);if(i<0)o=[].slice.call(tiles.children).map(function(e){return e.dataset.k}),i=o.indexOf(cur);open(o[(i+d+o.length)%o.length]);}
function close(){ov.classList.remove('on');document.body.style.overflow='';cur=null;if(last)last.focus({preventScroll:true});}
function say(t){toast.textContent=t;toast.classList.add('on');clearTimeout(say.t);say.t=setTimeout(function(){toast.classList.remove('on')},2200);}
var SITE='https://aethernode.github.io/mac-and-cheese/',ASOF=(document.querySelector('.asof')||{}).firstChild;ASOF=ASOF?ASOF.textContent.trim():'';
function col(v){return v<0?'#FF6A3D':v>0?'#4EE3AE':'#F4F1E6'}
function sn(v){return v>0?'+'+v:v<0?'−'+(-v):'0'}
function rr(c,x,y,w,h,r){c.beginPath();c.moveTo(x+r,y);c.arcTo(x+w,y,x+w,y+h,r);c.arcTo(x+w,y+h,x,y+h,r);c.arcTo(x,y+h,x,y,r);c.arcTo(x,y,x+w,y,r);c.closePath()}
function card(d){var W=1080,H=1350,cv=document.createElement('canvas');cv.width=W;cv.height=H;var c=cv.getContext('2d'),F='Fraunces, Georgia, serif',m=+d.mac,k=+d.cheese,acc=d.c.indexOf('y')>0?'#FFD23F':col(m||k);
function ls(v){if('letterSpacing'in c)c.letterSpacing=v+'px'}
c.fillStyle='#000';c.fillRect(0,0,W,H);var g=c.createRadialGradient(0,0,0,0,0,900);g.addColorStop(0,acc+'40');g.addColorStop(1,acc+'00');c.fillStyle=g;c.fillRect(0,0,W,H);
c.save();c.translate(80,80);rr(c,0,0,104,104,26);c.fillStyle='#000';c.fill();c.lineWidth=4;c.strokeStyle='#FFD23F';c.stroke();c.translate(12,24);c.scale(1.33,1.33);c.beginPath();c.moveTo(4,42);c.lineTo(18,31);c.lineTo(27,35);c.lineTo(40,20);c.lineTo(48,25);c.lineTo(60,8);c.lineTo(60,42);c.closePath();c.fillStyle='#FFD23F';c.fill();c.fillStyle='#000';[[46,34,4],[30,39,2.6],[53,22,2.4]].forEach(function(p){c.beginPath();c.arc(p[0],p[1],p[2],0,7);c.fill()});c.restore();
ls(0);c.textBaseline='alphabetic';c.font='600 64px '+F;c.fillStyle='#F4F1E6';var x=212;c.fillText('Mac ',x,155);x+=c.measureText('Mac ').width;c.font='italic 500 64px '+F;c.fillStyle='#FFD23F';c.fillText('&',x,155);x+=c.measureText('&').width;c.font='600 64px '+F;c.fillStyle='#F4F1E6';c.fillText(' Cheese',x,155);
ls(6);c.font='700 26px '+F;c.fillStyle='#FFD23F';c.fillText(d.group.toUpperCase(),80,330);
ls(4);c.font='700 112px '+F;c.fillStyle='#F4F1E6';c.fillText(d.name.toUpperCase(),74,450);
ls(1);c.font='500 32px '+F;c.fillStyle='rgba(244,241,230,.6)';c.fillText(d.px+'  ·  '+d.d5+'% in 5 days',80,505);
[[80,'MAC',m],[580,'CHEESE',k]].forEach(function(p){var X=p[0];ls(6);c.font='700 28px '+F;c.fillStyle='#F4F1E6';c.fillText(p[1],X,640);ls(-6);c.font='500 250px '+F;c.fillStyle=col(p[2]);c.fillText(sn(p[2]).replace('\u2212','\u2013'),X-10,870);ls(0);
var w=420,y=920;c.fillStyle='rgba(244,241,230,.25)';rr(c,X,y-2,w,4,2);c.fill();c.fillRect(X+w/2-1,y-12,2,24);c.fillStyle=col(p[2]);rr(c,X+(p[2]+10)/20*w-5,y-16,10,32,5);c.fill();c.font='600 24px '+F;c.fillStyle='rgba(244,241,230,.55)';c.fillText('−10',X,y+50);c.textAlign='center';c.fillText('0',X+w/2,y+50);c.textAlign='right';c.fillText('+10',X+w,y+50);c.textAlign='left';});
ls(5);c.font='700 30px '+F;c.fillStyle=acc;c.fillText(d.state.toUpperCase(),80,1080);
ls(0);c.font='500 46px '+F;c.fillStyle='#F4F1E6';c.fillText(d.name+' is a '+sn(m)+' on Mac & Cheese.',80,1160);
c.fillStyle='rgba(244,241,230,.18)';c.fillRect(80,1205,920,2);ls(2);c.font='600 24px '+F;c.fillStyle='rgba(244,241,230,.6)';c.fillText(ASOF.toUpperCase(),80,1255);ls(1);c.font='600 28px '+F;c.fillStyle='#FFD23F';c.fillText(SITE.replace('https://','').replace(/\/$/,''),80,1300);
return new Promise(function(r){cv.toBlob(r,'image/png')});}
function dl(blob,name){var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},1500)}
function shareOpen(tp,sh){var box=sh.querySelector('.shm');if(!box.hidden){box.hidden=true;return}box.hidden=false;var d={name:tp.dataset.name,group:tp.dataset.group,mac:tp.dataset.mac,cheese:tp.dataset.cheese,state:tp.dataset.state,px:tp.dataset.px,d5:tp.dataset.d5,c:tp.dataset.c},txt=tp.dataset.share,fn='mac-and-cheese-'+d.name.toLowerCase().replace(/[^a-z0-9]+/g,'-')+'.png',file=null,blob=null;
var ready=(document.fonts?document.fonts.load('600 100px Fraunces'):Promise.resolve()).then(function(){return card(d)}).then(function(b){blob=b;file=new File([b],fn,{type:'image/png'});box.querySelector('img').src=URL.createObjectURL(b);});
box.scrollIntoView({behavior:RM?'auto':'smooth',block:'nearest'});
function native(){return navigator.canShare&&file&&navigator.canShare({files:[file]})}
function win(u){window.open(u,'_blank','noopener,width=640,height=640')}
box.querySelectorAll('[data-to]').forEach(function(b){b.onclick=function(){ready.then(function(){var to=b.dataset.to,full=txt+' '+SITE;
if(to==='instagram'||to==='snapchat'){if(native()){navigator.share({files:[file],text:full}).catch(function(){});return}dl(blob,fn);if(to==='snapchat'){win('https://www.snapchat.com/scan?attachmentUrl='+encodeURIComponent(SITE))}say('Image saved. Post it to '+(to==='instagram'?'Instagram':'Snapchat')+' from your photos.');}
else if(to==='facebook')win('https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(SITE));
else if(to==='x')win('https://twitter.com/intent/tweet?text='+encodeURIComponent(txt)+'&url='+encodeURIComponent(SITE));
else if(to==='whatsapp')win('https://wa.me/?text='+encodeURIComponent(full));
else if(to==='save'){dl(blob,fn);say('Image saved.')}
else if(to==='copy'){(navigator.clipboard?navigator.clipboard.writeText(full):Promise.reject()).then(function(){say('Link copied.')},function(){say(full)})}})}});}
document.addEventListener('click',function(ev){var t=ev.target.closest('.tile,.lr');if(t)open(t.dataset.k,t);var p=ev.target.closest('.pt');if(p)open(p.dataset.ks.split(',')[0],p);});
document.querySelectorAll('.pt').forEach(function(p){p.addEventListener('keydown',function(ev){if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();open(p.dataset.ks.split(',')[0],p);}});});
ov.addEventListener('click',function(ev){if(ev.target===ov)close();});
var y0=null;sh.addEventListener('touchstart',function(ev){y0=sh.scrollTop<=0?ev.touches[0].clientY:null},{passive:true});
sh.addEventListener('touchend',function(ev){if(y0!==null&&ev.changedTouches[0].clientY-y0>110&&innerWidth<1000)close();y0=null;});
document.addEventListener('keydown',function(ev){if(ev.target.matches('input,textarea'))return;
if(ov.classList.contains('on')){if(ev.key==='Escape')close();else if(ev.key==='ArrowRight')step(1);else if(ev.key==='ArrowLeft')step(-1);return;}
var n='1234'.indexOf(ev.key);if(n>=0&&!ev.metaKey&&!ev.ctrlKey){document.querySelectorAll('.f')[n].click();}});
})();
