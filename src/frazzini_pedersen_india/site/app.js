'use strict';

class Formatter {
  static percent(value, digits = 2) {
    if (value === null || value === undefined) {
      return '';
    }
    return (value * 100).toFixed(digits);
  }

  static number(value, digits = 2) {
    if (value === null || value === undefined || Number.isNaN(value)) {
      return '';
    }
    return value.toFixed(digits).replace('-', '−');
  }

  static signed(value, digits = 2) {
    if (value === null || value === undefined) {
      return '';
    }
    const text = (value * 100).toFixed(digits);
    return text.replace('-', '−');
  }

  static minus(text) {
    return text.replace('-', '−');
  }
}

class Results {
  constructor(summary, monthly, meta) {
    this.summary = summary;
    this.monthly = monthly;
    this.meta = meta;
  }

  row(table, portfolio, costs) {
    const rows = this.summary[table];
    for (const row of rows) {
      if (row.portfolio === portfolio && row.costs === costs) {
        return row;
      }
    }
    return null;
  }

  series(name) {
    return this.monthly.series[name];
  }
}

class TableBuilder {
  constructor(tableId) {
    this.table = document.getElementById(tableId);
  }

  render(caption, headers, rows, note) {
    const table = this.table;
    table.innerHTML = '';
    const wrap = table.parentElement;
    let captionElement = wrap.previousElementSibling;
    if (!captionElement || !captionElement.classList.contains('table-caption')) {
      captionElement = document.createElement('p');
      captionElement.className = 'table-caption';
      wrap.parentElement.insertBefore(captionElement, wrap);
    }
    captionElement.innerHTML = caption;
    const head = document.createElement('thead');
    const headRow = document.createElement('tr');
    headers.forEach((text, index) => {
      const cell = document.createElement('th');
      cell.innerHTML = text;
      if (index === 0) {
        cell.className = 'text';
      }
      headRow.appendChild(cell);
    });
    head.appendChild(headRow);
    table.appendChild(head);
    const body = document.createElement('tbody');
    rows.forEach((values) => {
      const tr = document.createElement('tr');
      values.forEach((text, index) => {
        const cell = document.createElement('td');
        cell.innerHTML = text;
        if (index === 0) {
          cell.className = 'text';
        }
        tr.appendChild(cell);
      });
      body.appendChild(tr);
    });
    table.appendChild(body);
    if (note) {
      const parent = table.parentElement;
      let noteElement = parent.querySelector('.table-note');
      if (!noteElement) {
        noteElement = document.createElement('p');
        noteElement.className = 'table-note';
        parent.appendChild(noteElement);
      }
      noteElement.textContent = note;
    }
  }
}

class ChartBuilder {
  constructor() {
    this.charts = [];
    window.addEventListener('resize', () => {
      this.charts.forEach((chart) => chart.resize());
    });
  }

  chart(elementId) {
    const element = document.getElementById(elementId);
    let chart = echarts.getInstanceByDom(element);
    if (!chart) {
      chart = echarts.init(element, null, { renderer: 'svg' });
      this.charts.push(chart);
    }
    return chart;
  }

  baseOption() {
    return {
      textStyle: { fontFamily: 'Times New Roman, Times, Tinos, Liberation Serif, serif' },
      animation: false,
      grid: { left: 56, right: 24, top: 44, bottom: 40 },
      legend: { itemGap: 28, top: 0, textStyle: { fontSize: 13 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    };
  }

  columns(elementId, categories, values, color, axisName) {
    const option = this.baseOption();
    option.legend = { show: false };
    option.tooltip = { trigger: 'axis', axisPointer: { type: 'shadow' } };
    option.xAxis = { type: 'category', data: categories };
    option.yAxis = { type: 'value', name: axisName, nameLocation: 'end', nameGap: 14 };
    option.series = [{ type: 'bar', data: values, itemStyle: { color } }];
    this.chart(elementId).setOption(option, true);
  }

  lines(elementId, months, seriesList, logScale, axisFormatter) {
    const option = this.baseOption();
    const narrow = window.innerWidth < 640;
    if (seriesList.length > 2) {
      option.grid.top = narrow ? 112 : 76;
    }
    const all = [];
    seriesList.forEach((item) => item.values.forEach((value) => all.push(value)));
    const lowest = Math.min(...all);
    const highest = Math.max(...all);
    option.xAxis = {
      type: 'category',
      data: months,
      axisLabel: { formatter: (value) => value.slice(0, 4), interval: narrow ? 35 : 11 },
      axisTick: { interval: narrow ? 35 : 11 },
    };
    option.yAxis = {
      type: logScale ? 'log' : 'value',
      scale: true,
      axisLabel: { formatter: axisFormatter },
    };
    if (logScale) {
      option.yAxis.min = Number((lowest * 0.8).toPrecision(2));
      option.yAxis.max = Number((highest * 1.25).toPrecision(2));
    }
    option.series = seriesList.map((item) => ({
      name: item.name,
      type: 'line',
      data: item.values,
      showSymbol: false,
      lineStyle: { width: 1.6, color: item.color, type: item.dashed ? 'dashed' : 'solid' },
      itemStyle: { color: item.color },
    }));
    this.chart(elementId).setOption(option, true);
  }
}

class SeriesMath {
  static growth(returns) {
    const values = [];
    let level = 1;
    returns.forEach((value) => {
      level = level * (1 + (value === null ? 0 : value));
      values.push(Number(level.toFixed(4)));
    });
    return values;
  }

  static drawdown(returns) {
    const values = [];
    let level = 1;
    let peak = 1;
    returns.forEach((value) => {
      level = level * (1 + (value === null ? 0 : value));
      peak = Math.max(peak, level);
      values.push(Number(((level / peak - 1) * 100).toFixed(2)));
    });
    return values;
  }
}

class Page {
  constructor(results) {
    this.results = results;
    this.charts = new ChartBuilder();
    this.universe = 'liquid';
    this.costs = 'gross';
    this.readHash();
  }

  readHash() {
    const parts = window.location.hash.replace('#', '').split('-');
    if (parts.length === 2 && ['liquid', 'full'].includes(parts[0]) && ['gross', 'net'].includes(parts[1])) {
      this.universe = parts[0];
      this.costs = parts[1];
    }
  }

  start() {
    const universeControl = document.getElementById('control-universe');
    const costsControl = document.getElementById('control-costs');
    universeControl.value = this.universe;
    costsControl.value = this.costs;
    universeControl.addEventListener('change', () => this.changed());
    costsControl.addEventListener('change', () => this.changed());
    document.getElementById('copy-citation').addEventListener('click', () => {
      const text = document.getElementById('citation-text').textContent;
      navigator.clipboard.writeText(text);
    });
    this.renderStatic();
    this.render();
  }

  changed() {
    this.universe = document.getElementById('control-universe').value;
    this.costs = document.getElementById('control-costs').value;
    window.location.hash = `${this.universe}-${this.costs}`;
    this.render();
  }

  universeLabel() {
    return this.universe === 'liquid' ? 'the 500 most traded shares' : 'all shares with a beta';
  }

  costsLabel() {
    return this.costs === 'gross' ? 'before costs' : 'after costs';
  }

  set(id, text) {
    document.getElementById(id).textContent = text;
  }

  renderStatic() {
    const meta = this.results.meta;
    this.set('first-month', meta.first_month);
    this.set('last-month', meta.last_month);
    this.set('generated', meta.generated);
    const low = this.results.row('main', 'liquid_D1', 'gross');
    const high = this.results.row('main', 'liquid_D10', 'gross');
    const full = this.results.row('main', 'bab_full', 'gross');
    const liquid = this.results.row('main', 'bab_liquid', 'gross');
    this.set('abstract-alpha-low', `${Formatter.signed(low.capm_alpha)}%`);
    this.set('abstract-alpha-high', `${Formatter.signed(high.capm_alpha)}%`);
    this.set('abstract-bab-full', `${Formatter.percent(full.mean_monthly)}%`);
    this.set('abstract-bab-full-t', Formatter.number(full.nw_t));
    this.set('abstract-bab-liquid', `${Formatter.percent(liquid.mean_monthly)}%`);
    this.set('abstract-bab-liquid-t', Formatter.number(liquid.nw_t));
    const long = this.results.row('benchmarks', 'liquid_D1', 'net');
    const index = this.results.row('benchmarks', 'NIFTY 500 TRI', 'index');
    this.set('abstract-long-only', `${Formatter.percent(long.compound_annual, 1)}%`);
    this.set('abstract-benchmark', `${Formatter.percent(index.compound_annual, 1)}%`);
  }

  render() {
    this.set(
      'specification-summary',
      `${this.universeLabel()}, ${this.costsLabel()}; ${this.results.meta.months} holding months, ${this.results.meta.first_month} to ${this.results.meta.last_month}.`
    );
    this.renderDeciles();
    this.renderBab();
    this.renderLegs();
    this.renderGroups('size', 'table-size', 'Table 4.', 'BAB within groups of median traded value, all shares with a beta. Group 1 is the least traded fifth.');
    this.renderGroups('ivol', 'table-ivol', 'Table 5.', 'BAB within groups of idiosyncratic volatility, all shares with a beta. Group 1 is the least volatile fifth.');
    this.renderSubperiods();
    this.renderVariants();
    this.renderLongOnly();
  }

  renderDeciles() {
    const builder = new TableBuilder('table-deciles');
    const rows = [];
    const categories = [];
    const alphas = [];
    const betas = [];
    for (let decile = 1; decile <= 10; decile += 1) {
      const row = this.results.row('main', `${this.universe}_D${decile}`, this.costs);
      categories.push(`P${decile}`);
      alphas.push(Number((row.capm_alpha * 100).toFixed(3)));
      betas.push(Number(row.capm_beta.toFixed(3)));
      rows.push([
        `P${decile}${decile === 1 ? ' (low beta)' : ''}${decile === 10 ? ' (high beta)' : ''}`,
        Formatter.signed(row.mean_monthly),
        Formatter.number(row.nw_t),
        Formatter.signed(row.capm_alpha),
        Formatter.number(row.capm_alpha_t),
        Formatter.signed(row.ff4_alpha),
        Formatter.number(row.ff4_alpha_t),
        Formatter.number(row.capm_beta),
        Formatter.number(row.volatility_annual * 100, 1),
        Formatter.number(row.sharpe),
      ]);
    }
    builder.render(
      `<b>Table 1.</b> Portfolios sorted on beta: ${this.universeLabel()}, ${this.costsLabel()}. Monthly percent in excess of the risk-free rate; <i>t</i> is Newey–West.`,
      ['Decile', 'Excess return', '<i>t</i>', 'CAPM alpha', '<i>t</i>', '4-factor alpha', '<i>t</i>', 'Realised beta', 'Volatility %', 'Sharpe'],
      rows,
      'Paper, Table III (US, 1926–2012, before costs): P1 excess 0.91, CAPM alpha 0.52, realised beta 0.67; P10 excess 0.97, CAPM alpha −0.10, realised beta 1.85.'
    );
    this.charts.columns('figure-alpha', categories, alphas, '#2a78d6', '% a month');
    this.charts.columns('figure-beta', categories, betas, '#eb6834', 'beta');
    const first = this.results.row('main', `${this.universe}_D1`, this.costs);
    const last = this.results.row('main', `${this.universe}_D10`, this.costs);
    document.getElementById('text-deciles').textContent =
      `For ${this.universeLabel()} ${this.costsLabel()}, the lowest-beta decile has a CAPM alpha of ${Formatter.signed(first.capm_alpha)}% a month (t = ${Formatter.number(first.capm_alpha_t)}) and the highest-beta decile ${Formatter.signed(last.capm_alpha)}% (t = ${Formatter.number(last.capm_alpha_t)}). Realised betas rise from ${Formatter.number(first.capm_beta)} to ${Formatter.number(last.capm_beta)}.`;
  }

  renderBab() {
    const builder = new TableBuilder('table-bab');
    const names = [
      [`bab_${this.universe}`, 'Rank weights (paper)', 'main'],
      [`bab_${this.universe}_equal`, 'Equal weights', 'tables'],
      [`bab_${this.universe}_value`, 'Traded-value weights, 2 size × 3 beta', 'tables'],
    ];
    const rows = [];
    names.forEach(([name, label, table]) => {
      const row = this.results.row(table, name, this.costs);
      rows.push([
        label,
        Formatter.signed(row.mean_monthly),
        Formatter.number(row.nw_t),
        Formatter.signed(row.capm_alpha),
        Formatter.signed(row.ff4_alpha),
        Formatter.number(row.ff4_alpha_t),
        Formatter.number(row.capm_beta),
        Formatter.number(row.volatility_annual * 100, 1),
        Formatter.number(row.sharpe),
        Formatter.minus(Formatter.number(row.max_drawdown * 100, 1)),
      ]);
    });
    builder.render(
      `<b>Table 2.</b> The BAB factor: ${this.universeLabel()}, ${this.costsLabel()}. Monthly percent in excess of the risk-free rate.`,
      ['Weighting', 'Excess return', '<i>t</i>', 'CAPM alpha', '4-factor alpha', '<i>t</i>', 'Realised beta', 'Volatility %', 'Sharpe', 'Worst drawdown %'],
      rows,
      'Paper, Table III (US, rank weights, before costs): excess 0.70 (t 7.12), 4-factor alpha 0.55 (t 5.59), volatility 10.7, Sharpe 0.78. Traded value stands in for market capitalisation in the value-weighted version.'
    );
    const months = this.results.monthly.months;
    const key = `bab_${this.universe}_${this.costs}`;
    this.charts.lines(
      'figure-bab',
      months,
      [
        { name: `BAB, ${this.universeLabel()}`, values: SeriesMath.growth(this.results.series(key)), color: '#2a78d6' },
        { name: 'NIFTY 500 excess return', values: SeriesMath.growth(this.results.series('market_excess')), color: '#eb6834', dashed: true },
      ],
      true,
      (value) => `₹${value}`
    );
    const row = this.results.row('main', `bab_${this.universe}`, this.costs);
    const exposure = this.results.summary.exposure.find((item) => item.portfolio === `bab_${this.universe}`);
    document.getElementById('text-bab').textContent =
      `The rank-weighted BAB for ${this.universeLabel()} earns ${Formatter.percent(row.mean_monthly)}% a month ${this.costsLabel()} over ${row.months} months (t = ${Formatter.number(row.nw_t)}). On average it is long $${Formatter.number(exposure.dollar_long)} and short $${Formatter.number(exposure.dollar_short)} for each $1 of capital, against $1.40 and $0.70 in the paper's US sample.`;
  }

  renderLegs() {
    const builder = new TableBuilder('table-legs');
    const rows = [];
    [
      ['full_low_leg_scaled', 'Low-beta leg, all shares'],
      ['full_high_leg_scaled', 'High-beta leg, all shares'],
      ['liquid_low_leg_scaled', 'Low-beta leg, 500 most traded'],
      ['liquid_high_leg_scaled', 'High-beta leg, 500 most traded'],
    ].forEach(([name, label]) => {
      const row = this.results.row('tables', name, this.costs);
      rows.push([
        label,
        Formatter.signed(row.mean_monthly),
        Formatter.number(row.nw_t),
        Formatter.signed(row.ff4_alpha),
        Formatter.number(row.ff4_alpha_t),
      ]);
    });
    builder.render(
      `<b>Table 3.</b> The two legs of the BAB factor, each scaled to beta 1, ${this.costsLabel()}. Monthly percent.`,
      ['Leg', 'Excess return', '<i>t</i>', '4-factor alpha', '<i>t</i>'],
      rows
    );
  }

  renderGroups(kind, tableId, label, description) {
    const builder = new TableBuilder(tableId);
    const rows = [];
    for (let group = 1; group <= 5; group += 1) {
      const row = this.results.row('tables', `bab_${kind}_Q${group}`, this.costs);
      rows.push([
        `Group ${group}`,
        Formatter.signed(row.mean_monthly),
        Formatter.number(row.nw_t),
        Formatter.signed(row.ff4_alpha),
        Formatter.number(row.ff4_alpha_t),
      ]);
    }
    builder.render(
      `<b>${label}</b> ${description} Shown ${this.costsLabel()}, monthly percent.`,
      ['Group', 'Excess return', '<i>t</i>', '4-factor alpha', '<i>t</i>'],
      rows
    );
  }

  portfolioLabel(name) {
    const labels = {
      bab_full: 'BAB, all shares',
      bab_liquid: 'BAB, 500 most traded',
      liquid_D1: 'Lowest-beta decile, 500 most traded',
      full_D1: 'Lowest-beta decile, all shares',
    };
    return labels[name] || name;
  }

  renderSubperiods() {
    const builder = new TableBuilder('table-subperiods');
    const rows = [];
    this.results.summary.subperiods
      .filter((row) => row.costs === this.costs)
      .forEach((row) => {
        rows.push([
          this.portfolioLabel(row.portfolio),
          `${row.first_month} to ${row.last_month}`,
          Formatter.signed(row.mean_monthly),
          Formatter.number(row.nw_t),
        ]);
      });
    builder.render(
      `<b>Table 6.</b> Three consecutive subperiods of about six years each, ${this.costsLabel()}. Monthly percent in excess of the risk-free rate.`,
      ['Portfolio', 'Months', 'Excess return', '<i>t</i>'],
      rows
    );
  }

  variantLabel(name) {
    const labels = {
      main: 'Main specification',
      liquid_300: 'Liquid universe of 300 shares',
      liquid_1000: 'Liquid universe of 1,000 shares',
      drop_least_traded_half: 'Drop the least traded half of shares',
      delay_one_session: 'Trade one session after month-end',
      'delisting_-1.0': 'Delisted shares lose 100%',
      'delisting_-0.3': 'Delisted shares lose 30%',
      correlation_3_year: 'Correlation over 3 years',
      correlation_1_year: 'Correlation over 1 year',
      no_shrinkage: 'No shrinkage of betas',
      five_day_overlap: 'Five-day overlapping returns',
    };
    return labels[name] || name;
  }

  renderVariants() {
    const builder = new TableBuilder('table-variants');
    const names = [];
    this.results.summary.variants.forEach((row) => {
      if (!names.includes(row.variant)) {
        names.push(row.variant);
      }
    });
    const cell = (variant, portfolio, costs) => {
      const row = this.results.summary.variants.find(
        (item) => item.variant === variant && item.portfolio === portfolio && item.costs === costs
      );
      return `${Formatter.percent(row.mean_monthly)} (${Formatter.number(row.nw_t)})`;
    };
    const rows = names.map((name) => [
      this.variantLabel(name),
      cell(name, 'bab_full', 'gross'),
      cell(name, 'bab_full', 'net'),
      cell(name, 'bab_liquid', 'gross'),
      cell(name, 'bab_liquid', 'net'),
      cell(name, 'liquid_D1', 'net'),
    ]);
    builder.render(
      '<b>Table 7.</b> Robustness variants of the main specification: monthly excess return in percent, with the Newey–West <i>t</i>-statistic in brackets.',
      ['Variant', 'BAB, all shares, before costs', 'BAB, all shares, after costs', 'BAB, 500 most traded, before costs', 'BAB, 500 most traded, after costs', 'Lowest-beta decile, 500 most traded, after costs'],
      rows
    );
    document.getElementById('text-variants').textContent =
      'Dropping the least traded half of shares halves the all-share BAB. Charging every delisted share a 100% loss lowers it from 0.79% to 0.66% a month. Waiting one session after the month-end before trading does not hurt. Shorter correlation windows and no shrinkage raise the all-share BAB but leave the 500 most traded result small.';
  }

  renderLongOnly() {
    const builder = new TableBuilder('table-long-only');
    const labels = {
      'NIFTY 500 TRI': 'NIFTY 500 TRI',
      'NIFTY100 Low Volatility 30 TRI': 'NIFTY100 Low Volatility 30 TRI',
      'NIFTY Low Volatility 50 TRI': 'NIFTY Low Volatility 50 TRI',
      liquid_D1: 'Lowest-beta decile, monthly',
      liquid_D1_every_3_months: 'Lowest-beta decile, 3-month hold',
      liquid_D1_every_12_months: 'Lowest-beta decile, 12-month hold',
      bab_low_leg: 'Rank-weighted low-beta half',
      bab_low_leg_every_3_months: 'Rank-weighted low-beta half, 3-month hold',
      full_D1: 'Lowest-beta decile, all shares',
    };
    const rows = [];
    this.results.summary.benchmarks.forEach((row) => {
      if (row.costs === 'gross') {
        return;
      }
      rows.push([
        labels[row.portfolio] || row.portfolio,
        row.costs === 'index' ? 'index' : 'after costs',
        Formatter.number(row.compound_annual * 100, 1),
        Formatter.number(row.volatility_annual * 100, 1),
        Formatter.minus(Formatter.number(row.maximum_drawdown * 100, 1)),
        row.costs === 'index' && row.portfolio === 'NIFTY 500 TRI' ? '' : Formatter.number(row.excess_annual * 100, 1),
        row.excess_t === null ? '' : Formatter.number(row.excess_t),
        row.alpha === null ? '' : Formatter.signed(row.alpha),
        row.alpha_t === null ? '' : Formatter.number(row.alpha_t),
        Formatter.number(row.beta),
      ]);
    });
    builder.render(
      '<b>Table 8.</b> Long-only portfolios against the NIFTY 500 total-return index. Annual figures are on total returns, and Excess is the annual return minus that of the NIFTY 500; alpha is the CAPM alpha on returns in excess of the risk-free rate, monthly percent.',
      ['Portfolio', 'Costs', 'Annual return %', 'Volatility %', 'Worst drawdown %', 'Excess % a year', '<i>t</i>', 'CAPM alpha', '<i>t</i>', 'Beta'],
      rows
    );
    const months = this.results.monthly.months;
    const series = (name) => this.results.series(name);
    const curves = [
      { name: 'NIFTY 500 TRI', key: 'nifty500_total', color: '#52514e' },
      { name: 'NIFTY100 Low Volatility 30 TRI', key: 'lowvol30_total', color: '#1baf7a', dashed: true },
      { name: 'Lowest-beta decile, monthly', key: 'liquid_D1_net_total', color: '#2a78d6' },
      { name: 'Lowest-beta decile, 12-month hold', key: 'liquid_D1_every_12_months_net_total', color: '#eb6834' },
    ];
    this.charts.lines(
      'figure-wealth',
      months,
      curves.map((item) => ({ name: item.name, values: SeriesMath.growth(series(item.key)), color: item.color, dashed: item.dashed })),
      true,
      (value) => `₹${value}`
    );
    this.charts.lines(
      'figure-drawdown',
      months,
      curves.map((item) => ({ name: item.name, values: SeriesMath.drawdown(series(item.key)), color: item.color, dashed: item.dashed })),
      false,
      (value) => `${value}%`
    );
  }
}

async function loadResults() {
  const [summary, monthly, meta] = await Promise.all([
    fetch('data/summary.json').then((response) => response.json()),
    fetch('data/monthly.json').then((response) => response.json()),
    fetch('data/meta.json').then((response) => response.json()),
  ]);
  return new Results(summary, monthly, meta);
}

loadResults()
  .then((results) => new Page(results).start())
  .catch((error) => {
    document.getElementById('specification-summary').textContent = `Could not load the data: ${error.message}`;
  });
