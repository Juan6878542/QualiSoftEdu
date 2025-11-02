// app.js - lógica del evaluador
function getFormValues() {
  const form = document.getElementById('evalForm');
  const data = {};
  new FormData(form).forEach((v,k) => { data[k] = Number(v); });
  return data;
}

function mean(arr) {
  if (!arr.length) return 0;
  return arr.reduce((a,b)=>a+b,0)/arr.length;
}

function clampScore(s) {
  if (Number.isNaN(s)) return 0;
  return Math.max(0, Math.min(5, Math.round(s*100)/100));
}

function calculate() {
  const v = getFormValues();
  // group categories
  const calidad = [v.funcionalidad, v.fiabilidad, v.usabilidad, v.eficiencia];
  const codigo = [v.legibilidad, v.documentacion, v.unitarias];
  const programacion = [v.modularidad, v.errores, v.seguridad];

  const avgCalidad = mean(calidad);
  const avgCodigo = mean(codigo);
  const avgProgramacion = mean(programacion);

  // weights
  const wCalidad = 0.5, wCodigo = 0.3, wProgramacion = 0.2;
  const finalScore = clampScore(avgCalidad*wCalidad + avgCodigo*wCodigo + avgProgramacion*wProgramacion);

  // quantitative metrics: normalized to 0-100 as well
  const breakdown = {
    calidad: {score: clampScore(avgCalidad), weight: wCalidad},
    codigo: {score: clampScore(avgCodigo), weight: wCodigo},
    programacion: {score: clampScore(avgProgramacion), weight: wProgramacion},
    final: {score: finalScore}
  };

  return {inputs: v, breakdown};
}

function renderResult(res) {
  const area = document.getElementById('resultArea');
  const final = res.breakdown.final.score;
  area.innerHTML = `
    <h3>Resultado</h3>
    <p>Puntuación final (0 - 5): <strong>${final}</strong></p>
    <p>Desglose por categoría:</p>
    <ul>
      <li>Estándares de Calidad: ${res.breakdown.calidad.score} (peso ${res.breakdown.calidad.weight*100}%)</li>
      <li>Código: ${res.breakdown.codigo.score} (peso ${res.breakdown.codigo.weight*100}%)</li>
      <li>Programación: ${res.breakdown.programacion.score} (peso ${res.breakdown.programacion.weight*100}%)</li>
    </ul>
    <details>
      <summary>Ver datos completos (JSON)</summary>
      <pre>${JSON.stringify(res, null, 2)}</pre>
    </details>
  `;
}

document.getElementById('calculateBtn').addEventListener('click', () => {
  const r = calculate();
  renderResult(r);
});

document.getElementById('exportBtn').addEventListener('click', () => {
  const r = calculate();
  const filename = 'evaluacion_software.json';
  const blob = new Blob([JSON.stringify(r, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click();
  a.remove();
  URL.revokeObjectURL(url);
});
