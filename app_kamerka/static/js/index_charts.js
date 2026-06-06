function drawcharts(ics_len, coordinates_len, healthcare_len, ports, countries, products) {

    var T = {
        bg:      '#060e1a',
        surface: '#0c1828',
        text:    '#b0ccd8',
        muted:   '#5a7d8e',
        dim:     '#243a4a',
        bar:     '#0d4a87',
        accent:  '#00d4f0',   /* cyan — sparingly: dots, hovers, strokes */
        blue:    '#0064d7',
        warm:    '#ff00cd',
        teal:    '#1caf9a',
        grid:    'rgba(0,172,204,0.055)',
        font:    "'JetBrains Mono','Courier New',monospace"
    };

    /* ── Ports — horizontal bar ────────────────────────────────────── */
    (function () {
        var el = document.getElementById('dashboard-bar-1');
        if (!el || !ports || !ports.length) return;

        var ml = 48, mr = 34, mt = 10, mb = 6;
        var W = el.offsetWidth || 280, H = 200;
        var w = W - ml - mr, h = H - mt - mb;

        d3v3.select('#dashboard-bar-1').selectAll('*').remove();
        var svg = d3v3.select('#dashboard-bar-1').append('svg')
            .attr('width', '100%').attr('height', H)
            .append('g').attr('transform', 'translate(' + ml + ',' + mt + ')');

        var x = d3v3.scale.linear().range([0, w])
            .domain([0, d3v3.max(ports, function (d) { return d.c; })]);
        var y = d3v3.scale.ordinal().rangeRoundBands([0, h], 0.30)
            .domain(ports.map(function (d) { return d.port; }));

        x.ticks(4).forEach(function (v) {
            svg.append('line').attr({ x1: x(v), x2: x(v), y1: 0, y2: h,
                stroke: T.grid, 'stroke-width': 1 });
        });

        /* track */
        svg.selectAll('.tk').data(ports).enter().append('rect').attr({
            y: function (d) { return y(d.port); }, x: 0,
            height: y.rangeBand(), width: w,
            fill: 'rgba(13,74,135,0.12)', rx: 1
        });

        /* bar */
        svg.selectAll('.bar').data(ports).enter().append('rect').attr({
            y: function (d) { return y(d.port); }, x: 0,
            height: y.rangeBand(),
            width: function (d) { return Math.max(2, x(d.c)); },
            fill: T.bar, rx: 1
        });

        /* count */
        svg.selectAll('.lbl').data(ports).enter().append('text').attr({
            x: function (d) { return x(d.c) + 4; },
            y: function (d) { return y(d.port) + y.rangeBand() / 2; },
            dy: '.35em', fill: T.muted, 'font-family': T.font, 'font-size': '9px'
        }).text(function (d) { return d.c; });

        /* port label */
        svg.selectAll('.yl').data(ports).enter().append('text').attr({
            x: -6, y: function (d) { return y(d.port) + y.rangeBand() / 2; },
            dy: '.35em', 'text-anchor': 'end',
            fill: T.text, 'font-family': T.font, 'font-size': '9px'
        }).text(function (d) { return d.port; });
    }());

    /* ── Categories — donut ────────────────────────────────────────── */
    (function () {
        var el = document.getElementById('dashboard-donut-1');
        if (!el) return;

        var catData = [
            { label: 'ICS',        value: ics_len,        color: T.blue  },
            { label: 'IoT/Coords', value: coordinates_len, color: T.teal  },
            { label: 'Healthcare', value: healthcare_len,  color: T.warm  }
        ].filter(function (d) { return d.value > 0; });

        var W = el.offsetWidth || 280, H = 200;
        var cx = W / 2, cy = H / 2;
        var r = Math.min(cx, cy) - 22, ir = r * 0.56;

        d3v3.select('#dashboard-donut-1').selectAll('*').remove();
        var svg = d3v3.select('#dashboard-donut-1').append('svg')
            .attr('width', '100%').attr('height', H)
            .append('g').attr('transform', 'translate(' + cx + ',' + cy + ')');

        if (!catData.length) {
            svg.append('text').attr({ 'text-anchor': 'middle', dy: '.35em',
                fill: T.dim, 'font-family': T.font, 'font-size': '10px' }).text('NO DATA');
            return;
        }

        var arc  = d3v3.svg.arc().innerRadius(ir).outerRadius(r);
        var arcH = d3v3.svg.arc().innerRadius(ir).outerRadius(r + 5);
        var pie  = d3v3.layout.pie().value(function (d) { return d.value; }).sort(null);

        svg.selectAll('path').data(pie(catData)).enter().append('path')
            .attr('d', arc)
            .attr('fill', function (d) { return d.data.color; })
            .attr('stroke', T.surface).attr('stroke-width', 2)
            .on('mouseover', function () { d3v3.select(this).attr('d', arcH); })
            .on('mouseout',  function () { d3v3.select(this).attr('d', arc);  });

        var total = catData.reduce(function (s, d) { return s + d.value; }, 0);
        svg.append('text').attr({ 'text-anchor': 'middle', dy: '-0.15em',
            fill: T.text, 'font-family': T.font, 'font-size': '20px', 'font-weight': '700'
        }).text(total);
        svg.append('text').attr({ 'text-anchor': 'middle', dy: '1.1em',
            fill: T.dim, 'font-family': T.font, 'font-size': '9px', 'letter-spacing': '0.22em'
        }).text('TOTAL');

        var legX = -cx + 10, legY = -cy + 14;
        catData.forEach(function (d, i) {
            var g = svg.append('g').attr('transform', 'translate(' + legX + ',' + (legY + i * 18) + ')');
            g.append('rect').attr({ width: 8, height: 8, rx: 1, fill: d.color });
            g.append('text').attr({ x: 13, y: 7,
                fill: T.text, 'font-family': T.font, 'font-size': '11px'
            }).text(d.label + '  ' + d.value);
        });
    }());

    /* ── Products — treemap ────────────────────────────────────────── */
    (function () {
        var el = document.getElementById('dashboard-products');
        if (!el || !products || !products.length) return;

        var W = el.offsetWidth || 600, H = 220;

        d3v3.select('#dashboard-products').selectAll('*').remove();
        var svg = d3v3.select('#dashboard-products').append('svg')
            .attr('width', '100%').attr('height', H);

        var root = { name: 'root', children: products.map(function (d) {
            return { name: d.product || '—', value: d.c };
        })};

        var nodes = d3v3.layout.treemap()
            .size([W, H]).value(function (d) { return d.value; }).padding(2)
            .nodes(root).filter(function (d) { return !d.children; });

        var maxVal = d3v3.max(nodes, function (d) { return d.value; }) || 1;
        var fill = d3v3.scale.linear().domain([0, maxVal]).range(['#0a2340', '#1a5494']);

        var cell = svg.selectAll('g').data(nodes).enter().append('g')
            .attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });

        cell.append('rect')
            .attr('width',  function (d) { return Math.max(0, d.dx - 1); })
            .attr('height', function (d) { return Math.max(0, d.dy - 1); })
            .attr('fill', function (d) { return fill(d.value); })
            .attr('stroke', T.bg).attr('stroke-width', 1)
            .attr('rx', 1)
            .on('mouseover', function () { d3v3.select(this).attr('fill', T.blue); })
            .on('mouseout',  function (d) { d3v3.select(this).attr('fill', fill(d.value)); });

        /* name label */
        cell.append('text')
            .attr('x', function (d) { return d.dx / 2; })
            .attr('y', function (d) { return d.dy / 2 - 5; })
            .attr('text-anchor', 'middle')
            .attr('fill', T.text).attr('font-family', T.font).attr('font-size', '10px')
            .text(function (d) {
                if (d.dx < 36 || d.dy < 22) return '';
                var maxChars = Math.max(3, Math.floor(d.dx / 7));
                return d.name.length > maxChars ? d.name.slice(0, maxChars - 1) + '…' : d.name;
            });

        /* count label */
        cell.append('text')
            .attr('x', function (d) { return d.dx / 2; })
            .attr('y', function (d) { return d.dy / 2 + 9; })
            .attr('text-anchor', 'middle')
            .attr('fill', T.muted).attr('font-family', T.font).attr('font-size', '9px')
            .text(function (d) { return (d.dx >= 36 && d.dy >= 26) ? d.value : ''; });
    }());

    /* ── World map ─────────────────────────────────────────────────── */
    new jvm.WorldMap({
        container: $('#dashboard-map-seles'),
        map: 'world_mill_en',
        backgroundColor: 'transparent',
        regionsSelectable: false,
        regionStyle: {
            initial:  { fill: '#0a1e30', 'stroke-width': 0.3, stroke: '#152c42' },
            selected: { fill: T.warm }
        },
        markerStyle: { initial: { fill: T.warm, stroke: '#0b1118' } },
        series: {
            regions: [{
                scale: [T.bar, T.blue],
                attribute: 'fill',
                normalizeFunction: 'polynomial',
                values: countries
            }]
        }
    });

    $('.x-navigation-minimize').on('click', function () {
        setTimeout(function () { if (typeof rdc_resize === 'function') rdc_resize(); }, 200);
    });
}
