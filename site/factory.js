(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const stages = [
    {tool:'PERSONA + FACTORY', maturity:'Visión del flujo', title:'Todo empieza por una necesidad.', copy:'“Quiero guardar notas y que ninguna tenga el título vacío.” La persona trae el problema; Factory reúne el contexto y abre un cambio que se puede seguir.', input:'Una idea y su contexto', output:'Un pedido con responsable', decision:'Primero, entender el problema.', why:'Todavía no se escribe código. Acordar para quién construimos evita producir algo que nadie necesita.', tracker:'Pedido recibido'},
    {tool:'OPENSPEC + PERSONA', maturity:'Formato integrado', title:'La idea se convierte en un acuerdo.', copy:'Una especificación es una lista clara de lo que la app debe hacer. Por ejemplo: si el título está vacío, no guardar la nota y explicar cómo corregirlo. OpenSpec organiza ese acuerdo.', input:'El pedido y las dudas resueltas', output:'Comportamientos y ejemplos aceptados', decision:'¿Esto es lo que necesitás?', why:'Leé el comportamiento esperado. Podés aceptar la propuesta o volver a definir el pedido antes de que se escriba código.', tracker:'Esperando acuerdo de alcance', gate:true},
    {tool:'ORACLE + PERSONA', maturity:'Medidas en el prototipo', title:'Acordamos cómo comprobarlo.', copy:'Elegimos qué observar: intentar guardar una nota sin título y registrar si se rechazó. Una medida es la regla que evalúa ese hecho. La persona decide si esa evidencia alcanza.', input:'El acuerdo sobre la app', output:'Reglas de comprobación y sus límites', decision:'¿Qué evidencia te daría confianza?', why:'La prueba puede mostrar que el dato se rechaza. Saber si el mensaje resulta claro para una persona requiere además mirarlo y probarlo con ella.', tracker:'Esperando criterio de medición', gate:true},
    {tool:'AGENTES DE CÓDIGO', maturity:'Orquestación prevista', title:'Los agentes construyen la app.', copy:'Con el acuerdo como guía, los agentes escriben el código: la pantalla, el guardado de notas y la validación del título. Factory coordinará el trabajo y conservará el vínculo con el pedido.', input:'Un acuerdo y un plan de trabajo', output:'Código de la app y sus pruebas', decision:'La intención acompaña al código.', why:'En la POC actual, la implementación se hace fuera de la CLI. La visión de Factory es coordinar también a los agentes que la realizan.', tracker:'Construyendo el cambio'},
    {tool:'PRUEBAS + OBSERVACIONES', maturity:'Ejecución externa hoy', title:'Probamos lo que se construyó.', copy:'Las pruebas son comprobaciones repetibles. Intentamos guardar una nota válida, una vacía y una con espacios. Registramos lo ocurrido para que la revisión y Oracle puedan evaluarlo.', input:'Una versión de la app', output:'Resultados de pruebas y hechos observados', decision:'Probar también lo que podría fallar.', why:'Que una prueba pase solo habla de lo que comprobó. Necesitamos revisar los casos que elegimos y los que quedaron afuera.', tracker:'Reuniendo resultados'},
    {tool:'ORACLE CLUE + PERSONA', maturity:'Análisis IA pendiente', title:'Otra mirada busca problemas.', copy:'Clue revisará los cambios de código y señalará posibles defectos con evidencia. En nuestro ejemplo detecta que un título hecho solo de espacios se acepta. La persona decide cómo resolverlo.', input:'Los cambios y el acuerdo original', output:'Hallazgos con una decisión documentada', decision:'Hay un caso que debemos corregir.', why:'“   ” parece un título vacío, pero el código lo permite. Pedí la corrección y seguí el cambio de vuelta por código y pruebas.', tracker:'Esperando resolver un hallazgo', gate:true},
    {tool:'ORACLE', maturity:'Integrado en la POC', title:'Contrastamos lo prometido con lo observado.', copy:'Oracle compara los hechos con las reglas acordadas. Si falta evidencia o algo no se cumple, queda visible. El resultado se refiere a las propiedades medidas, con sus límites.', input:'Hechos observados y reglas acordadas', output:'Un veredicto sobre cada requisito medido', decision:'El resultado tiene una explicación.', why:'La regla “rechazar un título vacío” se evalúa con hechos. Oracle no deduce que toda la app es perfecta por comprobar ese caso.', tracker:'Evaluando evidencia'},
    {tool:'PERSONA + FACTORY', maturity:'Cierre humano en la POC', title:'La entrega vuelve a tus manos.', copy:'La persona ve la app construida, las pruebas, los hallazgos resueltos y el veredicto. Decide si acepta el cambio o necesita otra vuelta. El trabajo queda registrado para poder retomarlo.', input:'Software, revisión y evidencia', output:'Una entrega aceptada y trazable', decision:'¿Está listo para entregar?', why:'Aceptar la entrega es una decisión humana. La demo reúne el recorrido; una entrega real exige revisar los artefactos del producto.', tracker:'Esperando decisión de entrega', gate:true}
  ];
  let current = 0, playing = false, timer = null, frame = null, elapsed = 0, lastTime = null;
  let fixed = false, delivered = false;
  const accepted = new Set();
  const stageButtons = [...document.querySelectorAll('[data-stage]')];
  const canvas = $('factory-scene'), ctx = canvas.getContext('2d');
  const palette = {sky:'#132421', wall:'#334e3c', line:'#4d6a4d', ink:'#c5d9a9', light:'#c0ec96', gold:'#e4be73', blue:'#83c2bd'};
  function gatePending() { return !!stages[current].gate && !accepted.has(current); }
  function artifactReady() { return [1,2,5].every(n => accepted.has(n)); }
  function stop() {
    playing = false; clearTimeout(timer); cancelAnimationFrame(frame); timer = frame = null; lastTime = null;
    updateControls(); draw(elapsed);
  }
  function updateControls() {
    const gate = gatePending();
    $('play').disabled = reduced.matches || gate || current === 7;
    $('play').setAttribute('aria-pressed', String(playing));
    $('play-icon').textContent = playing ? 'Ⅱ' : '▶';
    $('play-label').textContent = playing ? 'Pausar' : 'Reproducir';
    $('previous').disabled = current === 0;
    $('next').disabled = gate || current === 7;
    $('counter').textContent = `${String(current + 1).padStart(2,'0')} / 08`;
    $('motion-status').textContent = delivered ? 'Entrega aceptada en la demostración.' : gate ? 'Pausa: esta etapa necesita una decisión humana.' : reduced.matches ? 'Movimiento reducido: avanzá con los controles.' : playing ? 'Recorriendo el flujo. Se detendrá en cada decisión humana.' : 'Avanzá a tu ritmo o reproducí el recorrido.';
  }
  function action(text, handler) {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = text;
    button.addEventListener('click', handler); $('decision-actions').append(button);
  }
  function focusStage() { $('stage-title').tabIndex=-1; $('stage-title').focus({preventScroll:true}); }
  function show(n, fromUser = false) {
    stop(); current = Math.max(0, Math.min(7,n)); const s = stages[current];
    $('stage-tool').textContent=s.tool; $('stage-maturity').textContent=s.maturity; $('stage-title').textContent=s.title;
    $('stage-copy').textContent=s.copy; $('stage-input').textContent=s.input; $('stage-output').textContent=s.output;
    $('decision-label').textContent=s.gate ? '◆ TU DECISIÓN HACE AVANZAR EL TRABAJO' : 'LO QUE IMPORTA ACÁ';
    $('decision-title').textContent=s.decision; $('decision-copy').textContent=s.why;
    $('decision-panel').classList.toggle('gate',!!s.gate); $('decision-actions').replaceChildren(); $('decision-feedback').textContent='';
    $('tracker-status').textContent=s.tracker;
    for (const b of stageButtons) { if (+b.dataset.stage===current) b.setAttribute('aria-current','step'); else b.removeAttribute('aria-current'); }
    if (current===1) {
      action('Aceptar el alcance',()=>{accepted.add(1); show(2,true);});
      action('Reformular el pedido',()=>{accepted.clear();fixed=false;delivered=false;show(0,true);});
    }
    if (current===2) {
      action('Acordar estas medidas',()=>{accepted.add(2);show(3,true);});
      action('Revisar el alcance',()=>{accepted.clear();fixed=false;delivered=false;show(1,true);});
    }
    if (current===3 && fixed) {
      $('stage-copy').textContent='Los agentes ajustan la validación para rechazar también títulos que solo contienen espacios. Se agrega una prueba para ese caso y el cambio vuelve a recorrer los controles.';
      $('tracker-status').textContent='Corrigiendo el caso encontrado';
    }
    if (current===4 && fixed) $('decision-copy').textContent='Ahora comprobamos también el caso señalado en la revisión. La corrección vuelve a pasar por pruebas; no saltea el resto del recorrido.';
    if (current===5) {
      if (fixed) {
        $('decision-title').textContent='La corrección tiene una nueva revisión.';
        $('decision-copy').textContent='El título formado por espacios ahora se rechaza y tiene una prueba. En la demo no quedan hallazgos abiertos. La persona decide aceptar la revisión.';
        $('stage-copy').textContent='La revisión vuelve sobre el cambio corregido. Los hallazgos se relacionan con la versión revisada; si el código cambia, la revisión anterior necesita renovarse.';
        action('Aceptar la revisión',()=>{accepted.add(5);show(6,true);});
      }
      action(fixed ? 'Pedir otro ajuste' : 'Pedir la corrección',()=>{accepted.delete(5);accepted.delete(7);delivered=false;fixed=true;show(3,true);});
    }
    if (current===6) {
      $('decision-title').textContent=artifactReady() ? 'Lo medido se cumple en este ejemplo.' : 'Todavía faltan decisiones del recorrido.';
      if (!artifactReady()) $('decision-copy').textContent='Podés explorar cualquier estación. Para completar esta demostración, acordá el alcance, las medidas y la resolución del hallazgo. Visitar una etapa no equivale a aprobarla.';
    }
    if (current===7) {
      if (delivered) {
        $('decision-title').textContent='Una entrega con historia.';
        $('decision-copy').textContent='El pedido, las decisiones y la evidencia quedan unidos. Un cambio futuro puede empezar desde lo que ya sabemos.';
        $('tracker-status').textContent='Entrega aceptada en la demo';
        action('Volver a recorrer',reset);
      } else if (artifactReady()) {
        action('Aceptar la entrega',()=>{accepted.add(7);delivered=true;show(7,true);});
        action('Pedir un cambio',()=>{accepted.delete(5);fixed=true;show(3,true);});
      } else {
        $('decision-title').textContent='Primero completá el recorrido.';
        $('decision-copy').textContent='La entrega necesita los acuerdos y la revisión previos. Explorar una etapa sirve para entenderla; no reemplaza esas decisiones.';
        action('Volver al acuerdo',()=>show(1,true));
      }
    }
    if (accepted.has(current) && current!==7) $('decision-feedback').textContent='Esta decisión ya se tomó en el recorrido actual.';
    updateControls(); draw(elapsed);
    if(fromUser) focusStage();
  }
  function reset(){accepted.clear();fixed=false;delivered=false;show(0,true);}
  function animate(now) {
    if (!playing || reduced.matches) return;
    if(lastTime!==null) elapsed += Math.min(now-lastTime,80);
    lastTime=now; draw(elapsed); frame=requestAnimationFrame(animate);
  }
  function start() {
    if(reduced.matches || gatePending() || current===7) return;
    playing=true; updateControls(); frame=requestAnimationFrame(animate);
    timer=setTimeout(()=>{const next=current+1;show(next);if(!gatePending() && next<7) start();},5200);
  }
  $('play').addEventListener('click',()=>playing ? stop() : start());
  $('next').addEventListener('click',()=>{if(!gatePending())show(current+1,true);});
  $('previous').addEventListener('click',()=>show(current-1,true));
  $('restart').addEventListener('click',reset);
  stageButtons.forEach(b=>b.addEventListener('click',()=>show(+b.dataset.stage)));
  reduced.addEventListener('change',()=>{stop();updateControls();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});

  // Pixel-art escena original. Dibujo local, sin imágenes o fuentes externas.
  function rect(x,y,w,h,color){ctx.fillStyle=color;ctx.fillRect(Math.round(x),Math.round(y),w,h);}
  function line(x,y,w,color){rect(x,y,w,2,color);}
  function text(label,x,y,color,size=10,align='left'){ctx.fillStyle=color;ctx.font=`${size}px monospace`;ctx.textAlign=align;ctx.fillText(label,x,y);}
  function sprite(pattern,x,y,colors,scale=2){pattern.forEach((row,dy)=>[...row].forEach((p,dx)=>{if(colors[p])rect(x+dx*scale,y+dy*scale,scale,scale,colors[p]);}));}
  function person(x,y,walk=false){sprite(['...hhh...','..hhhhh..','..sssss..','...sss...','..jjjjj..','.sjjjjjs.','.sjjjjjs.','..jjjjj..','..pp.pp..','..pp.pp..',walk?'..bb..bb.':'.bbb.bbb.'],x,y,{h:'#6d5241',s:'#e8b480',j:'#e9c776',p:'#889776',b:'#142821'},2);}
  function bot(x,y,t){sprite(['..aaaa..','.agggga.','.agbgba.','.agggga.','..aaaa..','.cccccc.','acgccgca','.cccccc.','..a..a..',t%2?'.aa..aa.':'..aa.aa.'],x,y,{a:'#9bba96',g:'#bddbaf',b:'#244b3d',c:'#477861'},2);}
  function paper(x,y,color='#c5d4a2'){rect(x,y,16,21,'#0e231b');rect(x+2,y,12,17,color);rect(x+4,y+4,8,2,'#6f8563');rect(x+4,y+9,6,2,'#6f8563');}
  function screen(x,y,w=60,h=39){rect(x,y,w,h,'#172c26');rect(x+3,y+3,w-6,h-8,'#203f35');rect(x+3,y+3,w-6,2,'#41644c');rect(x+w/2-3,y+h,6,8,'#829677');rect(x+w/2-14,y+h+7,28,3,'#96ad82');}
  function machine(i,x,t){
    const c=(current===i ? palette.light : '#91ae81');
    rect(x+10,231,106,6,'#849376');rect(x+13,237,7,29,'#46553f');rect(x+106,237,7,29,'#46553f');
    rect(x+19,243,86,14,'#293e2d');rect(x+22,246,36,2,'#506a42');
    if(i===0){
      rect(x+25,178,61,49,'#8c8664');rect(x+29,182,53,41,'#bcba8b');rect(x+34,190,42,3,'#687756');
      text('PEDIDO',x+57,205,'#334c37',9,'center');paper(x+83,206);paper(x+88,209);
      rect(x+7,217,13,14,'#8b9d6c');rect(x+10,205,8,12,'#49683d');rect(x+4,211,20,6,'#69804d');
    } else if(i===1){
      rect(x+23,161,73,59,'#718b73');rect(x+26,164,67,53,'#376f72');
      for(let xx=30;xx<92;xx+=10)rect(x+xx,165,1,50,'#508489');
      for(let yy=170;yy<216;yy+=9)rect(x+27,yy,65,1,'#508489');
      rect(x+35,176,19,15,'#afd5bf');rect(x+61,181,22,3,'#bbd5b5');rect(x+42,201,38,3,'#bbd5b5');
      rect(x+39,220,5,11,'#a2a67b');rect(x+79,220,5,11,'#a2a67b');paper(x+102,210);
    } else if(i===2){
      rect(x+60,167,7,62,'#b9b286');rect(x+31,179,65,4,'#a5ae83');rect(x+48,225,30,5,'#bec594');
      rect(x+35,183,2,21,'#77967d');rect(x+88,183,2,21,'#77967d');
      rect(x+23,203,28,5,'#acd0a2');rect(x+76,203,28,5,'#acd0a2');
      paper(x+29,184);rect(x+84,192,11,11,'#e4bd73');rect(x+87,188,5,4,'#e4bd73');
      rect(x+11,217,23,13,'#4b806b');text('?',x+23,227,palette.light,10,'center');
    } else if(i===3){
      screen(x+27,168,70,46);
      for(let r=0;r<5;r++){rect(x+34+(r%2)*5,177+r*6,10+(r*11)%36,2,r===2?palette.gold:'#86b69c');}
      rect(x+22,224,80,6,'#4c6b54');for(let xx=26;xx<98;xx+=8)rect(x+xx,225,5,2,'#9dae89');
      bot(x+105,207,Math.floor(t/350));
    } else if(i===4){
      screen(x+26,170,74,46);
      for(let r=0;r<2;r++)for(let q=0;q<3;q++){rect(x+34+q*19,179+r*14,13,9,(!fixed&&r===1&&q===2)?'#d3a266':'#a1cb80');rect(x+38+q*19,181+r*14,3,4,'#32513a');}
      rect(x+14,220,14,9,'#b9c28c');rect(x+95,221,18,9,'#bdce9d');
    } else if(i===5){
      paper(x+30,200);paper(x+46,204);
      const lens=['...gggg...','..g....g..','.g......g.','.g......g.','.g......g.','..g....g..','...gggg...','......kk..','.......kk.','........kk'];
      sprite(lens,x+65,163,{g:'#d6bd7c',k:'#a99561'},4);
      rect(x+15,168,28,24,'#304c3a');text(fixed?'OK':'!',x+29,185,fixed?palette.light:palette.gold,15,'center');
    } else if(i===6){
      rect(x+34,158,64,71,'#688770');rect(x+39,163,54,55,'#183e34');
      sprite(['...cc...','..cggc..','.cgllgc.','cgllllgc','.cgllgc.','..cggc..','...cc...'],x+49,171,{c:'#719e86',g:'#aad18e',l:current===6&&artifactReady()?'#d2efa9':'#8aab83'},4);
      rect(x+42,221,38,4,c);rect(x+85,220,6,6,palette.gold);rect(x+22,194,7,26,'#97b38e');
    } else if(i===7){
      rect(x+28,177,67,51,'#bb9863');rect(x+32,181,59,42,'#d6b77a');rect(x+58,177,10,51,'#a18858');
      rect(x+39,188,23,27,'#e7dab0');rect(x+43,192,15,14,'#7b9569');rect(x+46,197,9,2,'#d3e5a2');
      rect(x+101,189,3,42,'#a3bc90');rect(x+104,189,17,13,delivered?palette.light:'#608b69');
    }
    rect(x+16,266,95,4,'#182e22');
  }
  function draw(t=0){
    if(!ctx)return;
    ctx.imageSmoothingEnabled=false;rect(0,0,1152,370,palette.sky);
    for(let i=0;i<39;i++){const x=(i*157+27)%1152,y=(i*29+7)%77;rect(x,y,2,2,i%3?'#406049':'#839871');}
    // Silueta lejana y cañerías del taller.
    for(let i=0;i<12;i++){let h=15+(i*17)%32;rect(i*103,93-h,80,h,'#1d3329');for(let n=0;n<3;n++)rect(i*103+10+n*19,99-h,4,5,'#304a36');}
    rect(95,53,45,42,'#364d37');rect(98,53,39,6,'#668163');rect(105,41,6,13,'#6d8161');
    for(let i=0;i<4;i++){const yy=38-i*8-(playing?(t/180)%8:0);rect(106-i*4,yy,11+i*4,5,'#3a5440');}
    rect(293,62,741,5,'#4c6850');rect(1030,62,5,33,'#4c6850');
    rect(455,28,241,37,'#263f30');rect(458,31,235,31,'#324d37');text('O R A C L E  F A C T O R Y',575,51,'#c7dca5',12,'center');
    rect(23,96,1106,14,'#577252');rect(18,108,1116,9,'#6c8661');rect(27,117,1098,154,'#334f3a');
    for(let y=125;y<271;y+=17)for(let x=28+(y%2)*17;x<1120;x+=36)rect(x,y,31,1,'#3b5840');
    for(let i=0;i<8;i++){
      const x=28+i*137;
      rect(x,120,128,148,current===i?'#425f42':'#2c4433');
      rect(x+7,127,114,4,current===i?palette.light:'#779063');
      rect(x+5,134,2,132,'#203d2c');
      rect(x+8,146,112,83,current===i?'#3e5c3f':'#314a35');
      rect(x+53,116,21,8,'#84986c');rect(x+57,124,13,5,current===i?palette.light:'#adc293');
      text(String(i+1).padStart(2,'0'),x+13,144,current===i?palette.light:'#7b9770',8);
      machine(i,x,t);
      if([1,2,5,7].includes(i)){
        rect(x+108,135,6,6,accepted.has(i)?palette.light:palette.gold);
      }
    }
    rect(20,271,1112,10,'#647b52');rect(20,279,1112,5,'#253d2c');
    rect(14,286,1124,22,'#42593c');rect(14,288,1124,3,'#8d9e6b');rect(14,305,1124,3,'#879863');
    const offset=playing?(t/90)%14:0;
    for(let x=18+offset;x<1136;x+=14){rect(x,293,6,8,'#293f2d');rect(x+1,293,4,2,'#60744b');}
    for(let x=32;x<1130;x+=137){rect(x,308,8,12,'#4e6240');rect(x+91,308,8,12,'#4e6240');}
    const itemX=72+current*137;
    paper(itemX,270,palette.gold);rect(itemX-7,280,35,6,'#bd9d61');
    const humanX=85+current*137;
    person(humanX,243,playing&&Math.floor(t/260)%2===0);
    for(let i=0;i<8;i++){const x=28+i*137;const labels=['PEDIDO','SPEC','MEDIDAS','CÓDIGO','PRUEBAS','REVISIÓN','ORACLE','ENTREGA'];
      rect(x+5,329,117,26,current===i?'#335539':'#1c3126');
      text(labels[i],x+64,346,current===i?palette.light:'#93aa82',9,'center');
      if(current===i)rect(x+5,354,117,2,palette.light);
    }
  }

  const methods = {
    vibe: {name:'Vibe coding', subtitle:'Conversar, probar y ajustar.', steps:['Una idea','Pedir a la IA','Probar la app','Ajustar el pedido'], how:'Le contás a una IA qué querés y vas ajustando el resultado mientras lo probás. Es una forma directa de explorar una idea y aprender qué necesitás.', person:'Describe el pedido, prueba el resultado y pide cambios.', check:'La confianza suele empezar por lo que ves al usar la app. Podés agregar pruebas y acuerdos escritos para comprobar más casos.', example:'“Hacé una app de notas.” La probás y luego pedís: “No dejes guardar un título vacío”.', contribution:'Sirve para explorar rápido. Si los acuerdos y las comprobaciones no quedan registrados, cuesta saber qué se verificó y por qué se cambió algo.'},
    lifecycle: {name:'Ciclo de desarrollo (SDLC)', subtitle:'Organizar todo el trabajo.', steps:['Entender y diseñar','Construir','Probar y entregar','Mantener'], how:'El ciclo de vida del software, también llamado SDLC, organiza el trabajo desde entender la necesidad hasta mantener el producto. Puede ser iterativo: se vuelve a etapas anteriores cuando hace falta.', person:'Acuerda necesidades, organiza responsabilidades y revisa entregas. Puede trabajar con otras personas y con IA.', check:'Se definen revisiones y pruebas durante el proceso. La calidad depende de cómo se realizan, se mantienen y se documentan.', example:'El equipo acuerda cómo serán las notas, diseña la pantalla, construye el guardado, prueba casos y mantiene la app.', contribution:'Aporta organización para todo el ciclo. Es compatible con los demás enfoques: también una factory necesita planificar, construir, probar y mantener.'},
    spec: {name:'Desarrollo guiado por especificaciones', subtitle:'Acordar antes de construir.', steps:['Escribir el acuerdo','Revisarlo juntos','Construir con él','Comprobar los casos'], how:'Primero se escribe lo que el programa debe hacer, con ejemplos concretos. Ese documento —la especificación o spec— guía el código y sus pruebas.', person:'Revisa y acepta el acuerdo. Cuando cambia la necesidad, actualiza lo acordado.', check:'Se comparan la app y sus pruebas con los comportamientos esperados. Pueden usarse herramientas automáticas y revisión humana.', example:'“Si el título está vacío o solo tiene espacios, no guardar la nota y mostrar un mensaje”. Este caso se acuerda antes de programar.', contribution:'Da una referencia compartida y facilita comprobar el alcance. Todavía hay que decidir quién construye, cómo se revisa y qué evidencia demuestra cada promesa.'},
    factory: {name:'Oracle Factory', subtitle:'Coordinar el ciclo y conservar la evidencia.', steps:['Acordar y medir','Construir y probar','Revisar y evaluar','Decidir la entrega'], how:'Combina el acuerdo escrito, tareas, agentes de código, revisión y reglas de evaluación en un flujo que se puede seguir. La persona participa en los puntos donde hace falta criterio.', person:'Acepta el alcance, acuerda cómo comprobarlo, resuelve hallazgos y decide la entrega.', check:'Clue revisará riesgos del cambio. Oracle evalúa hechos contra reglas acordadas. Factory reúne los resultados y deja visibles los límites y pendientes.', example:'El acuerdo, la prueba del título vacío, la corrección de un hallazgo y la decisión de entrega quedan ligados al mismo cambio.', contribution:'Esa es la visión del producto. Hoy la POC conecta tareas, documentos, importación de requisitos, informes manuales y Oracle; la coordinación automática de agentes y el análisis automático de Clue siguen en desarrollo.'}
  };
  const methodTabs=[...document.querySelectorAll('[data-method]')];
  function selectMethod(key,focus=false){
    const m=methods[key]; if(!m)return;
    methodTabs.forEach(b=>{const active=b.dataset.method===key;b.setAttribute('aria-selected',String(active));b.tabIndex=active?0:-1;if(active&&focus)b.focus();});
    $('method-panel').setAttribute('aria-labelledby',`method-${key}`);
    $('method-subtitle').textContent=m.subtitle; $('method-how').textContent=m.how;
    $('method-person').textContent=m.person; $('method-check').textContent=m.check;
    $('method-example').textContent=m.example; $('method-contribution').textContent=m.contribution;
    $('method-lane').replaceChildren(...m.steps.map((s,i)=>{const node=document.createElement('div');node.className='path-stop';node.setAttribute('role','listitem');const n=document.createElement('span');n.textContent=String(i+1).padStart(2,'0');const t=document.createElement('strong');t.textContent=s;node.append(n,t);return node;}));
  }
  methodTabs.forEach((b,i)=>{
    b.addEventListener('click',()=>selectMethod(b.dataset.method));
    b.addEventListener('keydown',e=>{let n;if(e.key==='ArrowRight')n=(i+1)%4;if(e.key==='ArrowLeft')n=(i+3)%4;if(e.key==='Home')n=0;if(e.key==='End')n=3;if(n!==undefined){e.preventDefault();selectMethod(methodTabs[n].dataset.method,true);}});
  });
  selectMethod('vibe'); show(0);
})();
