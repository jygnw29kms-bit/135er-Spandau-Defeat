const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const out = { csvPath: null, warmup: 20, measure: 30, outDir: 'ue5/SpandauStrike/Saved/Profiling/Reports' };
  if (argv.length < 3) throw new Error('CSV-Pfad fehlt');
  out.csvPath = argv[2];
  for (let i = 3; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--warmup') out.warmup = Number(argv[++i]);
    else if (a === '--measure') out.measure = Number(argv[++i]);
    else if (a === '--out-dir') out.outDir = argv[++i];
    else throw new Error(`Unbekanntes Argument: ${a}`);
  }
  if (!Number.isFinite(out.warmup) || out.warmup < 0 || !Number.isFinite(out.measure) || out.measure <= 0) {
    throw new Error('Warmup muss endlich und >= 0 sein; Messdauer muss endlich und > 0 sein.');
  }
  return out;
}

function parseCsvLine(line) {
  const cells = [];
  let cur = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') { cur += '"'; i++; }
      else inQuotes = !inQuotes;
    } else if (ch === ',' && !inQuotes) {
      cells.push(cur); cur = '';
    } else cur += ch;
  }
  cells.push(cur);
  return cells;
}

function norm(s) {
  return String(s || '').trim().toLowerCase().replace(/[^a-z0-9/_]/g, '');
}
function num(s) {
  if (s == null) return null;
  const x = Number(String(s).trim().replace(',', '.'));
  return Number.isFinite(x) ? x : null;
}
function percentile(values, q) {
  if (!values.length) return null;
  const xs = [...values].sort((a,b)=>a-b);
  const pos = (xs.length - 1) * q;
  const lo = Math.floor(pos), hi = Math.ceil(pos);
  if (lo === hi) return xs[lo];
  return xs[lo] * (hi - pos) + xs[hi] * (pos - lo);
}
function mean(v) { return v.reduce((a,b)=>a+b,0) / v.length; }
function median(v) { return percentile(v, 0.5); }
function chooseHeader(rows) {
  let bestI = -1, bestScore = -1;
  for (let i = 0; i < Math.min(40, rows.length); i++) {
    const ns = rows[i].map(norm);
    let score = 0;
    for (const n of ns) {
      if (n.includes('frametime')) score += 10;
      if (n.includes('gamethread') || n.includes('game_thread')) score += 3;
      if (n.includes('renderthread') || n.includes('render_thread')) score += 3;
      if (n === 'gpu' || n.includes('gputime') || n.includes('/gpu')) score += 3;
    }
    if (score > bestScore) { bestScore = score; bestI = i; }
  }
  if (bestI < 0 || bestScore < 10) throw new Error('Keine plausible UE-CSV-Headerzeile mit FrameTime gefunden.');
  return bestI;
}
function pickCol(headers, kind) {
  const ns = headers.map(norm);
  let best = null;
  for (let i = 0; i < ns.length; i++) {
    const n = ns[i];
    let score = 0;
    if (kind === 'frame') {
      if (n === 'frametime') score = 100;
      else if (n.endsWith('/frametime')) score = 95;
      else if (n.includes('frametime')) score = 80;
    } else if (kind === 'game') {
      if (n === 'gamethreadtime') score = 120;
      else if (n === 'gamethreadtime_criticalpath') score = 110;
      else if (n === 'gamethread') score = 100;
      else if (n.includes('gamethreadtime')) score = 95;
      else if (n.includes('gamethread')) score = 70;
      else if (n.includes('game_thread')) score = 65;
    } else if (kind === 'render') {
      if (n === 'renderthreadtime') score = 120;
      else if (n === 'renderthreadtime_criticalpath') score = 110;
      else if (n === 'renderthread') score = 100;
      else if (n.includes('renderthreadtime')) score = 95;
      else if (n.includes('renderthread')) score = 70;
      else if (n.includes('render_thread')) score = 65;
    } else if (kind === 'gpu') {
      if (n === 'gputime') score = 120;
      else if (n === 'gpu') score = 100;
      else if (n.endsWith('/gpu') || n.includes('gputime')) score = 90;
      else if (n.includes('gpu') && !['memory','clock','temperature','busy'].some(x=>n.includes(x))) score = 60;
    }
    if (score && (!best || score > best.score)) best = { score, i };
  }
  return best ? best.i : null;
}
function inferMs(values) {
  const vals = values.filter(v => v >= 0);
  if (!vals.length) return { values: vals, unit: 'unknown' };
  const med = median(vals);
  return med < 1.0 ? { values: vals.map(v=>v*1000), unit: 'seconds->ms' } : { values: vals, unit: 'ms' };
}
function statsMs(values) {
  if (!values.length) return {};
  const totalMs = values.reduce((a,b)=>a+b,0);
  const slowCount = Math.max(1, Math.ceil(values.length * 0.01));
  const slowest = [...values].sort((a,b)=>b-a).slice(0, slowCount);
  return {
    frames: values.length,
    duration_s: totalMs / 1000,
    avg_frame_ms: mean(values),
    median_frame_ms: median(values),
    p95_frame_ms: percentile(values, 0.95),
    p99_frame_ms: percentile(values, 0.99),
    avg_fps: totalMs > 0 ? values.length / (totalMs / 1000) : null,
    one_percent_low_fps: slowest.length && mean(slowest) > 0 ? 1000 / mean(slowest) : null,
    hitches_over_33_3ms: values.filter(v=>v>33.333).length,
    hitches_over_50ms: values.filter(v=>v>50).length
  };
}
function threadStats(values) {
  if (!values.length) return {};
  const r = inferMs(values);
  const v = r.values;
  return { unit_inference: r.unit, avg_ms: mean(v), p95_ms: percentile(v,0.95), p99_ms: percentile(v,0.99), max_ms: Math.max(...v) };
}
function fmt(x) { return x == null ? 'n/a' : Number(x).toFixed(2); }

function main() {
  const args = parseArgs(process.argv);
  const text = fs.readFileSync(args.csvPath, 'utf8').replace(/^\uFEFF/, '');
  const rows = text.split(/\r?\n/).filter(Boolean).map(parseCsvLine);
  const hi = chooseHeader(rows);
  const headers = rows[hi];
  const frameCol = pickCol(headers, 'frame');
  if (frameCol == null) throw new Error('FrameTime-Spalte nicht gefunden.');
  const gameCol = pickCol(headers, 'game');
  const renderCol = pickCol(headers, 'render');
  const gpuCol = pickCol(headers, 'gpu');

  let readyRow = -1;
  for (let i = hi + 1; i < rows.length; i++) {
    if (rows[i].some(cell => String(cell).includes('LoadingScreen/Hide'))) readyRow = i;
  }
  if (readyRow < 0) throw new Error('LoadingScreen/Hide fehlt: kein belegtes Gameplay-Messfenster.');

  const parsed = [];
  const rawFrame = [];
  for (let rowIndex = hi + 1; rowIndex < rows.length; rowIndex++) {
    const row = rows[rowIndex];
    if (frameCol >= row.length) continue;
    const fv = num(row[frameCol]);
    if (fv == null || fv < 0) continue;
    rawFrame.push(fv);
    parsed.push({
      rowIndex,
      frame: fv,
      game: gameCol != null && gameCol < row.length ? num(row[gameCol]) : null,
      render: renderCol != null && renderCol < row.length ? num(row[renderCol]) : null,
      gpu: gpuCol != null && gpuCol < row.length ? num(row[gpuCol]) : null
    });
  }
  const inf = inferMs(rawFrame);
  if (!inf.values.length) throw new Error('Keine numerischen FrameTime-Werte gefunden.');
  parsed.forEach((r,i)=>r.frame_ms=inf.values[i]);
  const totalS = inf.values.reduce((a,b)=>a+b,0)/1000;
  const readyParsed = readyRow >= 0 ? parsed.filter(r => r.rowIndex > readyRow) : parsed;
  const readyTotalS = readyParsed.reduce((a,r)=>a+r.frame_ms,0)/1000;
  if (readyTotalS <= args.warmup) throw new Error(`Post-ready capture nur ${readyTotalS.toFixed(2)}s lang, Warmup ist ${args.warmup.toFixed(2)}s.`);

  const selected = [];
  let t = 0;
  const startMs = args.warmup * 1000, endMs = (args.warmup + args.measure) * 1000;
  for (const rec of readyParsed) {
    const dt = rec.frame_ms;
    const next = t + dt;
    // A frame that straddles the warmup boundary is still a warmup/loading frame.
    // Start measuring only once the previous frame has fully passed warmup.
    if (t >= startMs && t < endMs) selected.push(rec);
    t = next;
    if (t >= endMs) break;
  }
  const selectedFrame = selected.map(r=>r.frame_ms);
  const actualMeasureS = selectedFrame.reduce((a,b)=>a+b,0)/1000;
  const result = {
    source: args.csvPath,
    header_row_index: hi,
    frame_time_header: headers[frameCol],
    frame_time_unit_inference: inf.unit,
    capture_total_s: totalS,
    ready_anchor: readyRow >= 0 ? 'LoadingScreen/Hide' : 'capture-start-fallback',
    ready_row_index: readyRow,
    post_ready_total_s: readyTotalS,
    requested_warmup_s: args.warmup,
    requested_measure_s: args.measure,
    actual_measure_s: actualMeasureS,
    measurement_complete: actualMeasureS >= args.measure * 0.98,
    columns: {
      frame: headers[frameCol],
      game: gameCol != null ? headers[gameCol] : null,
      render: renderCol != null ? headers[renderCol] : null,
      gpu: gpuCol != null ? headers[gpuCol] : null
    },
    frame: statsMs(selectedFrame)
  };
  for (const key of ['game','render','gpu']) {
    const vals = selected.map(r=>r[key]).filter(v=>v != null);
    if (vals.length) result[key] = threadStats(vals);
  }

  fs.mkdirSync(args.outDir, { recursive: true });
  const stem = path.basename(args.csvPath, path.extname(args.csvPath)).replace(/[()]/g, '_');
  const jsonPath = path.join(args.outDir, `${stem}_analysis.json`);
  const mdPath = path.join(args.outDir, `${stem}_analysis.md`);
  fs.writeFileSync(jsonPath, JSON.stringify(result, null, 2), 'utf8');
  const f = result.frame;
  const lines = [
    '# Rathaus UE CSV Performance Report','',
    `- Quelle: \`${args.csvPath}\``,
    `- Capture gesamt: **${totalS.toFixed(2)} s**`,
    `- Ready-Anker: **${result.ready_anchor}**`,
    `- Laufzeit nach Ready: **${readyTotalS.toFixed(2)} s**`,
    `- Warmup nach Ready verworfen: **${args.warmup.toFixed(2)} s**`,
    `- Messfenster: **${actualMeasureS.toFixed(2)} s** von angefordert ${args.measure.toFixed(2)} s`,
    `- Messung vollständig: **${result.measurement_complete ? 'ja' : 'NEIN'}**`,'',
    '## Frame-Ergebnis','',
    `- Frames: **${f.frames || 0}**`,
    `- Durchschnitt: **${fmt(f.avg_fps)} FPS** / ${fmt(f.avg_frame_ms)} ms`,
    `- Median: **${fmt(f.median_frame_ms)} ms**`,
    `- P95: **${fmt(f.p95_frame_ms)} ms**`,
    `- P99: **${fmt(f.p99_frame_ms)} ms**`,
    `- 1% Low: **${fmt(f.one_percent_low_fps)} FPS**`,
    `- Hitches >33.3 ms: **${f.hitches_over_33_3ms || 0}**`,
    `- Hitches >50 ms: **${f.hitches_over_50ms || 0}**`
  ];
  for (const [key,title] of [['game','Game Thread'],['render','Render Thread'],['gpu','GPU']]) {
    if (result[key]) {
      const s = result[key];
      lines.push('',`## ${title}`,'',`- Avg: **${fmt(s.avg_ms)} ms**`,`- P95: **${fmt(s.p95_ms)} ms**`,`- P99: **${fmt(s.p99_ms)} ms**`,`- Max: **${fmt(s.max_ms)} ms**`);
    }
  }
  fs.writeFileSync(mdPath, lines.join('\n') + '\n', 'utf8');
  console.log(JSON.stringify(result, null, 2));
  console.log(`\nREPORT_MD=${mdPath}`);
  console.log(`REPORT_JSON=${jsonPath}`);
  if (!result.measurement_complete) {
    throw new Error(`Messfenster unvollständig: ${actualMeasureS.toFixed(2)} s von ${args.measure.toFixed(2)} s; Report gespeichert.`);
  }
}

try { main(); } catch (e) { console.error('ERROR:', e && e.stack ? e.stack : e); process.exit(1); }

