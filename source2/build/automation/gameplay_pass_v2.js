const fs=require('fs'),path=require('path');
const root='C:/Users/Public/SpandauDefeatMapProduction/rebuild_20260928';
const inDir=root+'/gameplay_v1_kv2', outDir=root+'/gameplay_v2_kv2';
fs.mkdirSync(outDir,{recursive:true});
function blockAt(s,tok,from=0){const st=s.indexOf(tok,from);if(st<0)return null;const bs=s.indexOf('{',st);let d=0,q=false,esc=false,e=bs;for(;e<s.length;e++){const ch=s[e];if(q){if(esc)esc=false;else if(ch==='\\')esc=true;else if(ch==='"')q=false;continue;}if(ch==='"'){q=true;continue;}if(ch==='{')d++;else if(ch==='}'&&!--d){e++;break;}}return{st,e,text:s.slice(st,e)}}
function blocks(s,tok){let a=[],p=0,b;while((b=blockAt(s,tok,p))){a.push(b);p=b.e;}return a}
function meshBounds(s){const pts=[];for(const b of blocks(s,'"CMapMesh"')){const ms=[...b.text.matchAll(/"origin" "vector3" "(-?[\d.]+) (-?[\d.]+) (-?[\d.]+)"/g)];if(ms.length){const m=ms[ms.length-1];pts.push([+m[1],+m[2],+m[3]])}};const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);return{minX:Math.min(...xs),maxX:Math.max(...xs),minY:Math.min(...ys),maxY:Math.max(...ys)}}
function setOuterOrigin(b,x,y,z){const re=/"origin" "vector3" "[^"]+"/g;const ms=[...b.matchAll(re)];if(!ms.length)return b;const m=ms[ms.length-1];return b.slice(0,m.index)+'"origin" "vector3" "'+[x,y,z].map(v=>Number(v.toFixed(2))).join(' ')+'"'+b.slice(m.index+m[0].length)}
function grid(cx,cy,w,h){const s=Math.max(72,Math.min(128,Math.min(w,h)*0.03));const off=[-1.5,-.5,.5,1.5].map(v=>v*s);const out=[];for(const yy of off)for(const xx of off)out.push([cx+xx,cy+yy,32]);return out}
function patch(id){let s=fs.readFileSync(path.join(inDir,id+'.vmap'),'utf8');const bnd=meshBounds(s),w=bnd.maxX-bnd.minX,h=bnd.maxY-bnd.minY,cx=(bnd.minX+bnd.maxX)/2,cy=(bnd.minY+bnd.maxY)/2;
 const ct=[bnd.minX+w*.14,bnd.minY+h*.14],t=[bnd.maxX-w*.14,bnd.maxY-h*.14];
 const a=[cx-w*.19,cy+h*.13],b=[cx+w*.19,cy-h*.13];
 const ctg=grid(ct[0],ct[1],w,h),tg=grid(t[0],t[1],w,h);let ci=0,ti=0,bi=0;
 const es=blocks(s,'"CMapEntity"');
 for(let i=es.length-1;i>=0;i--){const e=es[i];let nb=e.text;
  if(nb.includes('"classname" "string" "info_player_counterterrorist"')){const p=ctg[ci++%ctg.length];nb=setOuterOrigin(nb,...p)}
  else if(nb.includes('"classname" "string" "info_player_terrorist"')){const p=tg[ti++%tg.length];nb=setOuterOrigin(nb,...p)}
  else if(nb.includes('"classname" "string" "func_buyzone"')){const tm=(nb.match(/"TeamNum" "string" "(\d+)"/)||[])[1];const p=tm==='2'?t:ct;nb=setOuterOrigin(nb,p[0],p[1],32)}
  else if(nb.includes('"classname" "string" "func_bomb_target"')){const des=(nb.match(/"bomb_site_designation" "string" "(\d+)"/)||[])[1];const p=(des==='0'||(des==null&&bi++===0))?a:b;nb=setOuterOrigin(nb,p[0],p[1],32)}
  if(nb!==e.text)s=s.slice(0,e.st)+nb+s.slice(e.e);
 }
 const out=path.join(outDir,id+'.vmap');fs.writeFileSync(out,s,'utf8');return{id,bounds:bnd,ct,t,A:a,B:b,counts:{CT:ci,T:ti}};
}
const report=[];for(const fn of fs.readdirSync(inDir).filter(x=>x.endsWith('.vmap'))){const id=fn.slice(0,-5);report.push(patch(id));console.log('OK '+id)}
fs.writeFileSync(root+'/gameplay_v2_report.json',JSON.stringify(report,null,2));console.log('TOTAL='+report.length);
