/* Verificación funcional en Chromium. Requiere Playwright en NODE_PATH o node_modules. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'../site');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM||'/usr/bin/chromium',headless:true});
 const errors=[],external=[];let checks=0;
 try{
 const context=await browser.newContext({viewport:{width:1440,height:1000}});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
 await page.goto(pathToFileURL(path.join(root,'index.html')).href);
 assert.equal(await page.locator('h1').count(),1);checks++;
 // Reproducción se detiene en la aceptación humana y no permite saltarla con Siguiente.
 await page.locator('#play').click();await page.waitForTimeout(5500);
 assert.equal(await page.locator('#counter').innerText(),'02 / 08');
 assert.equal(await page.locator('#play').getAttribute('aria-pressed'),'false');
 assert(await page.locator('#next').isDisabled());checks++;
 await page.getByRole('button',{name:'Aceptar el alcance',exact:true}).click();
 assert.equal(await page.locator('#counter').innerText(),'03 / 08');
 assert(await page.locator('#next').isDisabled());
 await page.getByRole('button',{name:'Acordar estas medidas',exact:true}).click();
 await page.locator('#next').click();await page.locator('#next').click();
 assert.equal(await page.locator('#counter').innerText(),'06 / 08');
 assert.equal(await page.getByRole('button',{name:'Aceptar la revisión',exact:true}).count(),0);
 await page.getByRole('button',{name:'Pedir la corrección',exact:true}).click();
 assert.equal(await page.locator('#counter').innerText(),'04 / 08');
 await page.locator('#next').click();await page.locator('#next').click();
 await page.getByRole('button',{name:'Aceptar la revisión',exact:true}).click();
 assert.match(await page.locator('#decision-title').innerText(),/Lo medido se cumple/);
 await page.locator('#next').click();await page.getByRole('button',{name:'Aceptar la entrega',exact:true}).click();
 assert.match(await page.locator('#motion-status').innerText(),/Entrega aceptada/);checks++;
 // Explorar una estación no equivale a aprobar sus requisitos.
 await page.locator('#restart').click();await page.locator('[data-stage="7"]').click();
 assert.equal(await page.getByRole('button',{name:'Aceptar la entrega',exact:true}).count(),0);checks++;
 // Los cuatro métodos se recorren también por teclado, y cada uno explica rol y comprobación.
 await page.locator('#method-vibe').focus();
 for(const key of ['lifecycle','spec','factory','vibe']){
  await page.keyboard.press('ArrowRight');assert.equal(await page.locator(`#method-${key}`).getAttribute('aria-selected'),'true');
  assert((await page.locator('#method-person').innerText()).length>30);
  assert((await page.locator('#method-check').innerText()).length>30);
 }checks++;
 await page.emulateMedia({reducedMotion:'reduce'});await page.locator('#restart').click();
 assert(await page.locator('#play').isDisabled());
 const image=await page.locator('canvas').evaluate(c=>c.toDataURL());await page.waitForTimeout(160);
 assert.equal(await page.locator('canvas').evaluate(c=>c.toDataURL()),image);checks++;
 for(const width of [320,390,768,1440]){
  await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`overflow ${width}`);
 }checks++;
 // Ambas páginas funcionan sin red; enlaces internos y archivos locales existen.
 await context.setOffline(true);
 for(const filename of ['index.html','desde-cero.html']){
  await page.goto(pathToFileURL(path.join(root,filename)).href);
  const hrefs=await page.locator('a[href]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')));
  for(const href of hrefs){
   if(/^https?:/.test(href))continue;
   const url=new URL(href,page.url());assert(fs.existsSync(require('node:url').fileURLToPath(url)));
   if(url.hash && url.pathname===new URL(page.url()).pathname)assert(await page.locator(url.hash).count(),`anchor ${href}`);
  }
 }checks++;
 assert.equal(await page.locator('.guide-content section').count(),9);
 const target=page.locator('code[data-template]').filter({hasText:'aprobar-spec'});
 await page.locator('#change-id').fill('no es un id');assert.equal(await page.locator('#change-id').getAttribute('aria-invalid'),'true');
 const id='20260101-120000-prueba';await page.locator('#change-id').fill(id);
 assert((await target.innerText()).includes(id));
 assert.equal(await page.locator('.copy-code:disabled').count(),0);checks++;
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);checks++;
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);checks++;
 if(process.env.SCREENSHOTS){fs.mkdirSync(process.env.SCREENSHOTS,{recursive:true});
  await page.screenshot({path:path.join(process.env.SCREENSHOTS,'guide-mobile.png'),fullPage:true});
  await page.setViewportSize({width:1440,height:1080});await page.goto(pathToFileURL(path.join(root,'index.html')).href);
  await page.screenshot({path:path.join(process.env.SCREENSHOTS,'portada.png')});
  await page.locator('#formas').screenshot({path:path.join(process.env.SCREENSHOTS,'comparacion.png')});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(process.env.SCREENSHOTS,'portada-mobile.png'),fullPage:true});
 }
 console.log(JSON.stringify({resultado:'OK',comprobaciones:checks,errores:errors,peticiones_externas:external},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
