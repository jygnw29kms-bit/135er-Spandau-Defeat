// Deterministic Unreal Landscape heightfield export from the 513x513 Rathaus OBJ.
// UE Landscape height conversion: centimeters = (uint16 - 32768) / 128 * ZScale;
// at ZScale=100, uint16 = 32768 + elevation_metres * 128.
// This exports data only; no visual terrain or collision actor is changed.
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const repo = path.resolve(__dirname, '../..');
const src = process.argv[2] || 'C:/Users/anony/Documents/SpandauStrike/SourceData/DGM1/rathaus_dgm_gameplay1000_1000m_513.obj';
const dir = path.join(repo, 'ue5/SpandauStrike/SourceData/Rathaus');
const dst = path.join(dir, 'rathaus_dgm1_height_513.r16');
const meta = path.join(dir, 'rathaus_dgm1_height_513.json');
const size = 513, count = size * size, samples = Buffer.alloc(count * 2);
const xStep = 1000 / 512, yStep = 1000 / 512;
let n = 0, min = Infinity, max = -Infinity, prevY = -Infinity;
async function main(){
  const reader=readline.createInterface({input:fs.createReadStream(src,{encoding:'utf8'}),crlfDelay:Infinity});
  for await (const line of reader){
    if (!line.startsWith('v ')) continue;
    if(n >= count) throw new Error('More than 513*513 OBJ vertices');
    const [,xs,ys,zs]=line.trim().split(/\s+/);
    const x=Number(xs), y=Number(ys), z=Number(zs);
    const row=Math.floor(n/size), col=n%size;
    if(![x,y,z].every(Number.isFinite))throw new Error('Non-finite vertex at '+n);
    if(Math.abs(x-(-500+col*xStep))>0.003 || Math.abs(y-(-500+row*yStep))>0.003)throw new Error('Unexpected OBJ grid at '+n+': '+x+','+y);
    const raw=Math.round(32768+z*128);
    if(raw<0||raw>65535)throw new Error('Height out of Landscape range '+z);
    samples.writeUInt16LE(raw,n*2);min=Math.min(min,z);max=Math.max(max,z);n++;
  }
  if(n!==count)throw new Error('Expected '+count+' vertices; got '+n);
  fs.mkdirSync(dir,{recursive:true});
  fs.writeFileSync(dst,samples);
  const data={source:src,width:size,height:size,vertices:n,format:'16-bit unsigned little-endian UE Landscape .r16',row_order:'Y -500m to +500m',column_order:'X -500m to +500m',origin_m:[-500,-500],xy_scale_cm_per_vertex:xStep*100,z_scale_unreal:100,encoding:'round(32768 + z_m * 128)',min_elevation_m:min,max_elevation_m:max,bytes:samples.length,notes:'Source vertical datum is unchanged. Import as landscape heightmap, do not rotate or flip without matching mesh alignment. Generated collision is NOT yet integrated or validated.'};
  fs.writeFileSync(meta,JSON.stringify(data,null,2)+'\n');
  process.stdout.write('R16_READY '+JSON.stringify(data)+'\n');
}
main().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
