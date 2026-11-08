const fs=require('fs');
const p='C:\\Users\\anony\\Documents\\SpandauStrike\\SourceData\\DGM1\\rathaus_dgm_gameplay1000_1000m_513.obj';
const targets=[[-330,-34],[-330,-6],[-170,-34],[-170,-6],[-160,-96],[-160,-68],[25,-96],[25,-68],[35,-52],[35,-24],[205,-52],[205,-24],[225,61],[225,89],[400,61],[400,89],[0,0]];
let vs=[];
for(const l of fs.readFileSync(p,'utf8').split(/\r?\n/)) if(l.startsWith('v ')){const a=l.trim().split(/\s+/);vs.push([+a[1],+a[2],+a[3]]);}
for(const [tx,ty] of targets){let best=null,bd=1e99;for(const v of vs){const d=(v[0]-tx)**2+(v[1]-ty)**2;if(d<bd){bd=d;best=v;}}console.log(`${tx},${ty} -> grid ${best[0].toFixed(4)},${best[1].toFixed(4)} z=${best[2].toFixed(3)}m / ${(best[2]*100).toFixed(1)}cm d=${Math.sqrt(bd).toFixed(2)}m`)}
