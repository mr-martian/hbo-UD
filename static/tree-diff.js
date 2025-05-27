function arc_path(baseline, head, dep, height) {
    let d = (head < dep) ? +1 : -1;
    return `M ${head} ${baseline}
L ${head + d*10*(height + 1)} ${baseline - 70*height}
L ${dep - d*10*(height + 1)} ${baseline - 70*height}
L ${dep} ${baseline}`;
}

function arc_head(baseline, dep) {
    let s = 'M '+dep + ' ' + baseline + ' ';
    s += 'L ' + (dep - 6) + ' ' + (baseline - 10) + ' ';
    s += 'L ' + (dep + 6) + ' ' + (baseline - 10) + ' Z';
    return s;
}

function draw_sentence(elem) {
    console.log(elem);
    const blob = JSON.parse(elem.dataset.sent);
    let p = elem.appendChild(document.createElement('p'));
    p.innerText = blob.sent_id;
    let svg = elem.appendChild(document.createElementNS(
	'http://www.w3.org/2000/svg', 'svg'));
    let table = elem.appendChild(document.createElement('table'));
    let rows = [];
    for (let i = 0; i < 6; i++) {
	rows.push(table.appendChild(document.createElement('tr')));
    }
    for (let word of blob.words) {
	let hover = '';
	for (let k of Object.keys(word[6])) {
	    hover += k + ' = ' + word[6][k] + '\n';
	}
	for (let i = 0; i < 6; i++) {
	    let td = rows[i].appendChild(document.createElement('td'));
	    td.innerText = word[i];
	    td.title = hover;
	}
    }
    let offset = svg.getBoundingClientRect().left;
    let centers = Array.from(rows[0].children).map(
	function(w) {
	    let r = w.getBoundingClientRect();
	    return ((r.left + r.right) / 2) - offset;
	});
    let baseline = blob.height * 100 - 20;
    svg.setAttribute('width', rows[0].getBoundingClientRect().width);
    svg.setAttribute('height', blob.height * 100);
    svg.innerHTML = blob.arcs.map(
	function(arc) {
	    let head = centers[arc.head];
	    let dep = centers[arc.dep];
	    let label = arc.label;
	    if (head < dep) {
		label += '&gt;';
	    } else {
		label = '&lt;' + label;
	    }
	    return `
<g stroke="${arc.color}" fill="none">
  <path d="${arc_path(baseline, head, dep, arc.height)}"/>
  <path d="${arc_head(baseline, dep)}"/>
  <text x="${(head+dep)/2 - 2*label.length}" y="${baseline - arc.height*70 - 15}" transform="rotate(-20,${(head+dep)/2},${baseline - arc.height*70 - 20})">${label}</text>
</g>`;
	}
    ).join('');
}

document.querySelectorAll('.sentence').forEach(draw_sentence);
