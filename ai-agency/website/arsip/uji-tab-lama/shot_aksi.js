#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),os=require('os');
function lc(){for(const c of [process.env.PW_CORE,'/tmp/camofox/node_modules/playwright-core','playwright-core']){if(!c)continue;try{return require(c).chromium}catch(e){}}throw new Error('no pw')}
function fc(){if(process.env.CHROME_PATH)return process.env.CHROME_PATH;const b=path.join(os.homedir(),'.cache/ms-playwright');if(!fs.existsSync(b))return;for(const d of fs.readdirSync(b)){const p=path.join(b,d,'chrome-linux64/chrome');if(fs.existsSync(p))return p}}
const J={D1:4,D2:3,D3:5,D4:3,D5:2,D6:3,D7:3,D8:2};
(async()=>{const br=await lc().launch({executablePath:fc()});
const ctx=await br.newContext({viewport:{width:1440,height:900}});const pg=await ctx.newPage();
await pg.goto('file://'+path.resolve('index.html'),{waitUntil:'load'});await pg.waitForTimeout(2000);
for(const [k,v] of Object.entries(J))await pg.click(`#penList .pen-q[data-kode="${k}"] .pen-opt[data-nilai="${v}"]`);
await pg.click('#penHitung');await pg.waitForTimeout(3500);
const el=await pg.$('.ph-aksi');await el.scrollIntoViewIfNeeded();await pg.waitForTimeout(500);
await el.screenshot({path:'pratinjau/hasil-05-aksi.png'});
console.log('pratinjau/hasil-05-aksi.png');await br.close()})();
