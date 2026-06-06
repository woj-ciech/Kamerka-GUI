function drawCharts(ports, cities, categories, products) {

    var T = {
        bg:      '#060e1a',
        surface: '#0c1828',
        text:    '#b0ccd8',
        muted:   '#5a7d8e',
        dim:     '#243a4a',
        bar:     '#0d4a87',
        blue:    '#0064d7',
        accent:  '#00d4f0',   /* cyan — sparingly */
        warm:    '#ff00cd',
        teal:    '#1caf9a',
        grid:    'rgba(0,172,204,0.055)',
        font:    "'JetBrains Mono','Courier New',monospace"
    };

    /* ── Ports — horizontal bar ──────────────────────────────────── */
    (function () {
        var el = document.getElementById('res-ports');
        if (!el || !ports || !ports.length) return;

        var ml = 50, mr = 36, mt = 10, mb = 6;
        var W  = el.offsetWidth  || 400;
        var H  = el.offsetHeight || 250;
        var h  = H - mt - mb;
        var rowH = Math.floor(h / ports.length);
        var w  = W - ml - mr;

        d3v3.select('#res-ports').selectAll('*').remove();

        var svg = d3v3.select('#res-ports').append('svg')
            .attr('width', '100%').attr('height', H)
            .append('g').attr('transform', 'translate(' + ml + ',' + mt + ')');

        var x = d3v3.scale.linear().range([0, w])
            .domain([0, d3v3.max(ports, function (d) { return d.c; })]);
        var y = d3v3.scale.ordinal().rangeRoundBands([0, h], 0.28)
            .domain(ports.map(function (d) { return d.port; }));

        x.ticks(4).forEach(function (v) {
            svg.append('line').attr({
                x1: x(v), x2: x(v), y1: 0, y2: h,
                stroke: T.grid, 'stroke-width': 1
            });
        });

        svg.selectAll('.track').data(ports).enter().append('rect').attr({
            y: function (d) { return y(d.port); }, x: 0,
            height: y.rangeBand(), width: w,
            fill: 'rgba(13,74,135,0.12)', rx: 1
        });

        svg.selectAll('.bar').data(ports).enter().append('rect').attr({
            y: function (d) { return y(d.port); }, x: 0,
            height: y.rangeBand(),
            width: function (d) { return Math.max(2, x(d.c)); },
            fill: T.bar, rx: 1
        });

        svg.selectAll('.lbl').data(ports).enter().append('text').attr({
            x: function (d) { return x(d.c) + 4; },
            y: function (d) { return y(d.port) + y.rangeBand() / 2; },
            dy: '.35em', fill: T.muted, 'font-family': T.font, 'font-size': '9px'
        }).text(function (d) { return d.c; });

        svg.selectAll('.ylabel').data(ports).enter().append('text').attr({
            x: -6,
            y: function (d) { return y(d.port) + y.rangeBand() / 2; },
            dy: '.35em', 'text-anchor': 'end',
            fill: T.text, 'font-family': T.font, 'font-size': '9px'
        }).text(function (d) { return d.port; });
    }());

    /* ── Cities — vertical lollipop ─────────────────────────────── */
    (function () {
        var el = document.getElementById('res-cities');
        if (!el || !cities || !cities.length) return;

        var mb = 56, mt = 26, ml = 10, mr = 10;
        var W  = el.offsetWidth  || 400;
        var H  = el.offsetHeight || 220;
        var colW = Math.max(36, Math.floor((W - ml - mr) / cities.length));
        var w  = colW * cities.length;
        var h  = H - mt - mb;

        d3v3.select('#res-cities').selectAll('*').remove();

        var svg = d3v3.select('#res-cities').append('svg')
            .attr('width', '100%').attr('height', H)
            .append('g').attr('transform', 'translate(' + ml + ',' + mt + ')');

        var y = d3v3.scale.linear().range([h, 0])
            .domain([0, d3v3.max(cities, function (d) { return d.c; })]);
        var x = d3v3.scale.ordinal().rangeRoundBands([0, w], 0.2)
            .domain(cities.map(function (d) { return d.city; }));

        y.ticks(4).forEach(function (v) {
            svg.append('line').attr({
                x1: 0, x2: w, y1: y(v), y2: y(v),
                stroke: T.grid, 'stroke-width': 1
            });
        });

        /* stems */
        svg.selectAll('.stem').data(cities).enter().append('line').attr({
            x1: function (d) { return x(d.city) + x.rangeBand() / 2; },
            x2: function (d) { return x(d.city) + x.rangeBand() / 2; },
            y1: h,
            y2: function (d) { return Math.min(h - 2, y(d.c)); },
            stroke: T.dim, 'stroke-width': 1.5
        });

        /* dots */
        svg.selectAll('.dot').data(cities).enter().append('circle')
            .attr('cx', function (d) { return x(d.city) + x.rangeBand() / 2; })
            .attr('cy', function (d) { return Math.min(h - 2, y(d.c)); })
            .attr('r', 5)
            .attr('fill', T.blue)
            .attr('stroke', T.surface).attr('stroke-width', 1.5)
            .on('mouseover', function () { d3v3.select(this).attr('fill', T.accent).attr('r', 7); })
            .on('mouseout',  function () { d3v3.select(this).attr('fill', T.blue).attr('r', 5); });

        /* count labels above dots */
        svg.selectAll('.lbl').data(cities).enter().append('text').attr({
            x: function (d) { return x(d.city) + x.rangeBand() / 2; },
            y: function (d) { return Math.min(h - 2, y(d.c)) - 10; },
            'text-anchor': 'middle',
            fill: T.muted, 'font-family': T.font, 'font-size': '9px'
        }).text(function (d) { return d.c; });

        /* x-axis labels */
        svg.selectAll('.xlabel').data(cities).enter().append('text').attr({
            x: function (d) { return x(d.city) + x.rangeBand() / 2; },
            y: h + 10,
            dy: '.71em',
            'text-anchor': 'end',
            transform: function (d) {
                var cx = x(d.city) + x.rangeBand() / 2;
                return 'rotate(-40,' + cx + ',' + (h + 10) + ')';
            },
            fill: T.text, 'font-family': T.font, 'font-size': '10px'
        }).text(function (d) {
            var s = String(d.city || '—');
            return s.length > 12 ? s.slice(0, 11) + '…' : s;
        });
    }());

    /* ── Products — treemap ──────────────────────────────────────── */
    (function () {
        var el = document.getElementById('res-products');
        if (!el || !products || !products.length) return;

        var W = el.offsetWidth || 500, H = el.offsetHeight || 220;

        d3v3.select('#res-products').selectAll('*').remove();

        var svg = d3v3.select('#res-products').append('svg')
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

        cell.append('text')
            .attr('x', function (d) { return d.dx / 2; })
            .attr('y', function (d) { return d.dy / 2 + 9; })
            .attr('text-anchor', 'middle')
            .attr('fill', T.muted).attr('font-family', T.font).attr('font-size', '9px')
            .text(function (d) { return (d.dx >= 36 && d.dy >= 26) ? d.value : ''; });
    }());

    /* ── Device types — donut ────────────────────────────────────── */
    (function () {
        var el = document.getElementById('res-devices');
        if (!el || !categories || !categories.length) return;

        var palette = [T.bar, T.blue, T.warm, T.teal,
            '#7F8C9A', '#e07b00', '#8855ff', '#33b5e5', '#aa66cc', '#99cc00',
            '#ff6680', '#00b894', '#fdcb6e', '#6c5ce7', '#e17055', '#74b9ff',
            '#a29bfe', '#fab1a0', '#55efc4', '#fd79a8'];

        var W      = el.offsetWidth  || 300;
        var H      = el.offsetHeight || 230;
        var cx     = W / 2, cy = H / 2;
        var r      = Math.min(cx, cy) - 20;
        var ir     = r * 0.52;

        d3v3.select('#res-devices').selectAll('*').remove();
        d3v3.select('#res-devices').style('position', 'relative');

        /* tooltip */
        var tip = d3v3.select('#res-devices').append('div').style({
            position: 'absolute',
            background: '#0c1828',
            border: '1px solid rgba(0,172,204,0.3)',
            padding: '4px 9px',
            'font-family': T.font,
            'font-size': '10px',
            color: T.text,
            'pointer-events': 'none',
            opacity: 0,
            'border-radius': '2px',
            'white-space': 'nowrap',
            'z-index': 10
        });

        var svg = d3v3.select('#res-devices').append('svg')
            .attr('width', '100%').attr('height', H);

        var donutG = svg.append('g')
            .attr('transform', 'translate(' + cx + ',' + cy + ')');

        var arc  = d3v3.svg.arc().innerRadius(ir).outerRadius(r);
        var arcH = d3v3.svg.arc().innerRadius(ir).outerRadius(r + 7);
        var pie  = d3v3.layout.pie().value(function (d) { return d.value; }).sort(null);

        donutG.selectAll('path').data(pie(categories)).enter().append('path')
            .attr('d',    arc)
            .attr('fill', function (d, i) { return palette[i % palette.length]; })
            .attr('stroke', T.surface).attr('stroke-width', 2)
            .on('mouseover', function (d) {
                d3v3.select(this).attr('d', arcH);
                var ev = d3v3.event;
                var rect = el.getBoundingClientRect();
                tip.style('opacity', 1)
                   .style('left', (ev.clientX - rect.left + 12) + 'px')
                   .style('top',  (ev.clientY - rect.top  - 32) + 'px')
                   .text(d.data.label + ': ' + d.data.value);
            })
            .on('mousemove', function () {
                var ev = d3v3.event;
                var rect = el.getBoundingClientRect();
                tip.style('left', (ev.clientX - rect.left + 12) + 'px')
                   .style('top',  (ev.clientY - rect.top  - 32) + 'px');
            })
            .on('mouseout', function () {
                d3v3.select(this).attr('d', arc);
                tip.style('opacity', 0);
            });

        var total = categories.reduce(function (s, d) { return s + d.value; }, 0);
        donutG.append('text').attr({
            'text-anchor': 'middle', dy: '-0.15em',
            fill: T.text, 'font-family': T.font, 'font-size': '22px', 'font-weight': '700'
        }).text(total);
        donutG.append('text').attr({
            'text-anchor': 'middle', dy: '1.1em',
            fill: T.dim, 'font-family': T.font, 'font-size': '9px', 'letter-spacing': '0.22em'
        }).text('TOTAL');
    }());

    /* ── Redraw on Statistics tab activate ───────────────────────── */
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        if ($(e.target).attr('href') === '#tab10') {
            ['res-ports', 'res-cities', 'res-products', 'res-devices'].forEach(function (id) {
                d3v3.select('#' + id).selectAll('*').remove();
            });
            drawCharts(ports, cities, categories, products);
        }
    });
}
